from decimal import Decimal
import pandas as pd
from django.db import transaction
from .strategy import analyse, timeframe_is_bullish
from .ml import predict
from .notifications import send_signal
from ..models import Candle, AnalysisRun, Signal, SignalEvent

@transaction.atomic
def _frame(symbol, interval, limit=500):
    rows=list(Candle.objects.filter(symbol=symbol,interval=interval,is_closed=True).order_by("-open_time")[:limit])
    rows.reverse()
    return rows, pd.DataFrame([{f:getattr(c,f) for f in ["open_time","close_time","open","high","low","close","volume"]} for c in rows])

def run_analysis(symbol,interval,context_interval="4h",regime_interval="1d"):
    candles,frame=_frame(symbol,interval)
    if not candles: raise ValueError(f"No candles for {symbol} {interval}")
    _,context=_frame(symbol,context_interval); _,regime=_frame(symbol,regime_interval)
    decision=analyse(frame,timeframe_is_bullish(context),timeframe_is_bullish(regime))
    run,created=AnalysisRun.objects.get_or_create(symbol=symbol,interval=interval,candle_close_time=candles[-1].close_time,strategy_version="trend-v1",defaults={"status":decision.status,"score":decision.score,"reasons":decision.reasons,"warnings":decision.warnings,"features":decision.features})
    if not created or decision.status!="confirmed": return run,None
    probability=predict(decision.features)
    if probability is not None and probability<0.55:
        run.status="rejected"; run.warnings=[*run.warnings,"ML probability below confirmation threshold"]; run.save(update_fields=["status","warnings"]); return run,None
    l=decision.levels
    signal=Signal.objects.create(analysis=run,entry_low=l["entry_low"],entry_high=l["entry_high"],stop_loss=l["stop_loss"],target_1=l["target_1"],target_2=l["target_2"],risk_reward=Decimal(str(l["risk_reward"])),confidence=decision.score,ml_probability=probability,expires_at=l["expires_at"])
    SignalEvent.objects.create(signal=signal,event_type="created")
    send_signal(signal)
    return run,signal
