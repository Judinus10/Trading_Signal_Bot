import pandas as pd
from signals.services.indicators import enrich
def test_indicator_columns_exist():
    n=240; df=pd.DataFrame({"open_time":pd.date_range("2025-01-01",periods=n,freq="h",tz="UTC"),"close_time":pd.date_range("2025-01-01 01:00",periods=n,freq="h",tz="UTC"),"open":range(100,100+n),"high":range(102,102+n),"low":range(99,99+n),"close":range(101,101+n),"volume":[100+i%20 for i in range(n)]})
    out=enrich(df); assert {"ema20","ema50","ema200","rsi14","atr14","volume_ratio"}.issubset(out.columns); assert len(out)==n
