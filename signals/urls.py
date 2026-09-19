from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CandleViewSet, AnalysisViewSet, SignalViewSet, BacktestViewSet, MLModelViewSet, health, analyse_now
r=DefaultRouter(); r.register("candles",CandleViewSet); r.register("analyses",AnalysisViewSet); r.register("signals",SignalViewSet); r.register("backtests",BacktestViewSet); r.register("models",MLModelViewSet)
urlpatterns=[path("health/",health),path("analyse/",analyse_now),path("",include(r.urls))]
