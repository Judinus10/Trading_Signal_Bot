import pandas as pd
from django.core.management.base import BaseCommand
from signals.models import Candle
from signals.services.backtest import run_backtest
class Command(BaseCommand):
    help="Backtest the current strategy against stored candles"
    def add_arguments(self,p): p.add_argument("symbol"); p.add_argument("interval")
    def handle(self,*a,**o):
        qs=Candle.objects.filter(symbol=o["symbol"].upper(),interval=o["interval"],is_closed=True).order_by("open_time")
        frame=pd.DataFrame(list(qs.values("open_time","close_time","open","high","low","close","volume")))
        result=run_backtest(frame); self.stdout.write(self.style.SUCCESS(str(result.metrics)))
