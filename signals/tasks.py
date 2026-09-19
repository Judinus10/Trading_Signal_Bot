from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Candle, Signal, SignalEvent
from .services.exchange import BinancePublicClient
from .services.orchestrator import run_analysis

@shared_task(autoretry_for=(Exception,),retry_backoff=True,max_retries=4)
def ingest(symbol,interval,limit=500):
    rows=BinancePublicClient().klines(symbol,interval,limit)
    for row in rows: Candle.objects.update_or_create(symbol=row["symbol"],interval=row["interval"],open_time=row["open_time"],defaults=row)
    return len(rows)

@shared_task
def scan_markets():
    output=[]
    for symbol in settings.TRADING_SYMBOLS:
        for interval in dict.fromkeys([settings.ENTRY_INTERVAL,settings.CONTEXT_INTERVAL,settings.REGIME_INTERVAL]):
            ingest(symbol,interval)
        run,signal=run_analysis(symbol,settings.ENTRY_INTERVAL,settings.CONTEXT_INTERVAL,settings.REGIME_INTERVAL); output.append({"symbol":symbol,"status":run.status,"signal":signal.pk if signal else None})
    return output

@shared_task
def track_open_signals():
    client=BinancePublicClient(); changed=0
    for s in Signal.objects.select_related("analysis").filter(state__in=["active","target1"]):
        price=client.price(s.analysis.symbol); state=None
        if price<=s.stop_loss: state="stopped"
        elif price>=s.target_2: state="won"
        elif price>=s.target_1 and s.state=="active": state="target1"
        elif timezone.now()>=s.expires_at: state="expired"
        if state:
            s.state=state
            if state in ["won","stopped","expired"]: s.resolved_at=timezone.now()
            s.save(); SignalEvent.objects.create(signal=s,event_type=state,price=price); changed+=1
    return changed
