from datetime import datetime, timezone
from decimal import Decimal
import requests
from django.conf import settings

class BinancePublicClient:
    def __init__(self, base_url=None, timeout=15): self.base_url=(base_url or settings.BINANCE_BASE_URL).rstrip('/'); self.timeout=timeout
    def klines(self,symbol,interval,limit=500,start_ms=None,end_ms=None):
        params={"symbol":symbol.upper(),"interval":interval,"limit":min(limit,1000)}
        if start_ms is not None: params["startTime"]=start_ms
        if end_ms is not None: params["endTime"]=end_ms
        r=requests.get(f"{self.base_url}/api/v3/klines",params=params,timeout=self.timeout); r.raise_for_status()
        now_ms=int(datetime.now(timezone.utc).timestamp()*1000); rows=[]
        for x in r.json():
            rows.append({"symbol":symbol.upper(),"interval":interval,"open_time":datetime.fromtimestamp(x[0]/1000,tz=timezone.utc),"close_time":datetime.fromtimestamp(x[6]/1000,tz=timezone.utc),"open":Decimal(x[1]),"high":Decimal(x[2]),"low":Decimal(x[3]),"close":Decimal(x[4]),"volume":Decimal(x[5]),"is_closed":x[6]<now_ms})
        return rows
    def price(self,symbol):
        r=requests.get(f"{self.base_url}/api/v3/ticker/price",params={"symbol":symbol.upper()},timeout=self.timeout); r.raise_for_status(); return Decimal(r.json()["price"])
