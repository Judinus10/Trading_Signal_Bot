from django.contrib import admin
from .models import Candle, AnalysisRun, Signal, SignalEvent, BacktestRun, MLModel
@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin): list_display=("symbol","interval","open_time","close","is_closed"); list_filter=("symbol","interval")
@admin.register(AnalysisRun)
class AnalysisAdmin(admin.ModelAdmin): list_display=("symbol","interval","candle_close_time","status","score","strategy_version"); list_filter=("status","symbol","interval")
@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin): list_display=("analysis","direction","confidence","risk_reward","state","created_at"); list_filter=("state","direction")
admin.site.register(SignalEvent); admin.site.register(BacktestRun); admin.site.register(MLModel)
