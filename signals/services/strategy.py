from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from .indicators import enrich, FEATURE_COLUMNS

@dataclass(frozen=True)
class Decision:
    status:str; score:int; reasons:list; warnings:list; features:dict; levels:dict|None=None

def timeframe_is_bullish(frame):
    if frame is None or len(frame) < 200:
        return False
    row = enrich(frame).iloc[-1]
    return bool(row.close > row.ema50 > row.ema200)

def analyse(frame, context_bullish=True, regime_bullish=True):
    df=enrich(frame)
    if len(df)<210: return Decision("rejected",0,[],["At least 210 completed candles are required."],{})
    x=df.iloc[-1]; reasons=[]; warnings=[]; score=0
    if x.close>x.ema200 and x.ema50>x.ema200: score+=20; reasons.append("Price and EMA50 are above EMA200")
    if context_bullish and regime_bullish: score+=15; reasons.append("4-hour and daily trends agree")
    elif not context_bullish or not regime_bullish: warnings.append("Higher-timeframe trend does not fully agree")
    pullback=x.low<=x.ema20*1.005 and x.close>x.ema20
    breakout=x.close>x.recent_resistance if x.recent_resistance==x.recent_resistance else False
    if pullback or breakout: score+=20; reasons.append("Confirmed pullback" if pullback else "Resistance breakout")
    if 50<=x.rsi14<=68: score+=10; reasons.append("RSI is constructive without extreme extension")
    if x.volume_ratio>=1.3: score+=15; reasons.append("Volume exceeds its 20-candle average")
    atr=Decimal(str(x.atr14)); close=Decimal(str(x.close)); support=Decimal(str(x.recent_support)) if x.recent_support==x.recent_support else close-atr*2
    stop=max(support,close-atr*2); risk=close-stop
    if risk<=0: return Decision("rejected",score,reasons,["Invalid stop geometry"],_features(x))
    target1=close+risk*Decimal("1.25"); target2=close+risk*Decimal(str(settings.MIN_RISK_REWARD)); score+=10; reasons.append("Risk geometry meets minimum reward-to-risk")
    if x.atr_pct>0.06: warnings.append("Abnormally high volatility"); return Decision("rejected",score,reasons,warnings,_features(x))
    score+=10
    status="confirmed" if score>=settings.SIGNAL_SCORE_THRESHOLD else "watch" if score>=settings.WATCH_SCORE_THRESHOLD else "rejected"
    levels={"entry_low":close-atr*Decimal("0.15"),"entry_high":close+atr*Decimal("0.10"),"stop_loss":stop,"target_1":target1,"target_2":target2,"risk_reward":settings.MIN_RISK_REWARD,"expires_at":x.close_time+timedelta(hours=8)}
    return Decision(status,min(score,100),reasons,warnings,_features(x),levels)

def _features(row):
    return {k:float(row[k]) for k in FEATURE_COLUMNS}
