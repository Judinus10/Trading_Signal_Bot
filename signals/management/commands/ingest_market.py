from django.core.management.base import BaseCommand
from signals.tasks import ingest
class Command(BaseCommand):
    help="Download public Binance candles"
    def add_arguments(self,p): p.add_argument("symbol"); p.add_argument("interval"); p.add_argument("--limit",type=int,default=500)
    def handle(self,*a,**o): self.stdout.write(self.style.SUCCESS(f"Stored {ingest(o['symbol'].upper(),o['interval'],o['limit'])} candles"))
