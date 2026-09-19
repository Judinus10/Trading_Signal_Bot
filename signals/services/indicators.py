import numpy as np
import pandas as pd

FEATURE_COLUMNS=["ema20_distance","ema50_distance","ema200_distance","rsi14","atr_pct","volume_ratio","return_5","trend_alignment"]

def enrich(frame: pd.DataFrame) -> pd.DataFrame:
    df=frame.copy().sort_values("open_time").reset_index(drop=True)
    for c in ["open","high","low","close","volume"]: df[c]=pd.to_numeric(df[c],errors="coerce")
    df["ema20"]=df.close.ewm(span=20,adjust=False).mean(); df["ema50"]=df.close.ewm(span=50,adjust=False).mean(); df["ema200"]=df.close.ewm(span=200,adjust=False).mean()
    delta=df.close.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); rs=gain/loss.replace(0,np.nan); df["rsi14"]=(100-(100/(1+rs))).fillna(50)
    prev=df.close.shift(1); tr=pd.concat([(df.high-df.low).abs(),(df.high-prev).abs(),(df.low-prev).abs()],axis=1).max(axis=1); df["atr14"]=tr.ewm(alpha=1/14,adjust=False).mean()
    df["volume_sma20"]=df.volume.rolling(20).mean(); df["volume_ratio"]=(df.volume/df.volume_sma20).replace([np.inf,-np.inf],np.nan).fillna(0)
    df["ema20_distance"]=(df.close-df.ema20)/df.close; df["ema50_distance"]=(df.close-df.ema50)/df.close; df["ema200_distance"]=(df.close-df.ema200)/df.close
    df["atr_pct"]=df.atr14/df.close; df["return_5"]=df.close.pct_change(5).fillna(0); df["trend_alignment"]=((df.close>df.ema50)&(df.ema50>df.ema200)).astype(int)
    df["recent_resistance"]=df.high.shift(1).rolling(20).max(); df["recent_support"]=df.low.shift(1).rolling(20).min()
    return df
