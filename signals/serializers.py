from rest_framework import serializers
from .models import Candle, AnalysisRun, Signal, SignalEvent, BacktestRun, MLModel
class CandleSerializer(serializers.ModelSerializer):
    class Meta: model=Candle; fields="__all__"
class AnalysisSerializer(serializers.ModelSerializer):
    class Meta: model=AnalysisRun; fields="__all__"
class EventSerializer(serializers.ModelSerializer):
    class Meta: model=SignalEvent; fields="__all__"
class SignalSerializer(serializers.ModelSerializer):
    analysis=AnalysisSerializer(read_only=True); events=EventSerializer(many=True,read_only=True)
    class Meta: model=Signal; fields="__all__"
class BacktestSerializer(serializers.ModelSerializer):
    class Meta: model=BacktestRun; fields="__all__"
class MLModelSerializer(serializers.ModelSerializer):
    class Meta: model=MLModel; fields="__all__"
