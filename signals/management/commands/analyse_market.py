from django.core.management.base import BaseCommand
from signals.services.orchestrator import run_analysis
class Command(BaseCommand):
    help="Run one idempotent analysis"
    def add_arguments(self,p): p.add_argument("symbol"); p.add_argument("interval")
    def handle(self,*a,**o):
        run,signal=run_analysis(o["symbol"].upper(),o["interval"]); self.stdout.write(self.style.SUCCESS(f"status={run.status} score={run.score} signal={getattr(signal,'pk',None)}"))
