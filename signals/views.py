from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Candle, AnalysisRun, Signal, BacktestRun, MLModel
from .serializers import CandleSerializer, AnalysisSerializer, SignalSerializer, BacktestSerializer, MLModelSerializer
from .services.orchestrator import run_analysis

@login_required
def dashboard(request): return render(request,"dashboard.html",{"signals":Signal.objects.select_related("analysis").order_by("-created_at")[:20],"analyses":AnalysisRun.objects.order_by("-created_at")[:10]})
class CandleViewSet(viewsets.ReadOnlyModelViewSet): queryset=Candle.objects.all().order_by("-open_time"); serializer_class=CandleSerializer; filterset_fields=["symbol","interval"]
class AnalysisViewSet(viewsets.ReadOnlyModelViewSet): queryset=AnalysisRun.objects.all().order_by("-created_at"); serializer_class=AnalysisSerializer; filterset_fields=["symbol","interval","status"]
class SignalViewSet(viewsets.ReadOnlyModelViewSet): queryset=Signal.objects.select_related("analysis").all().order_by("-created_at"); serializer_class=SignalSerializer; filterset_fields=["state","direction"]
class BacktestViewSet(viewsets.ReadOnlyModelViewSet): queryset=BacktestRun.objects.all().order_by("-created_at"); serializer_class=BacktestSerializer
class MLModelViewSet(viewsets.ReadOnlyModelViewSet): queryset=MLModel.objects.all().order_by("-created_at"); serializer_class=MLModelSerializer
@api_view(["GET"])
def health(request): return Response({"status":"ok","signals_enabled":True,"ml_enabled":settings.ML_ENABLED})
@api_view(["POST"])
def analyse_now(request):
    symbol=request.data.get("symbol",settings.TRADING_SYMBOLS[0]).upper(); interval=request.data.get("interval",settings.ENTRY_INTERVAL)
    if symbol not in settings.TRADING_SYMBOLS: return Response({"detail":"Symbol is not configured"},status=400)
    run,signal=run_analysis(symbol,interval); return Response({"analysis":AnalysisSerializer(run).data,"signal":SignalSerializer(signal).data if signal else None})
