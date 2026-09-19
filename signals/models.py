from django.db import models

class Candle(models.Model):
    symbol=models.CharField(max_length=20); interval=models.CharField(max_length=8)
    open_time=models.DateTimeField(); close_time=models.DateTimeField()
    open=models.DecimalField(max_digits=24,decimal_places=8); high=models.DecimalField(max_digits=24,decimal_places=8)
    low=models.DecimalField(max_digits=24,decimal_places=8); close=models.DecimalField(max_digits=24,decimal_places=8)
    volume=models.DecimalField(max_digits=30,decimal_places=8); is_closed=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["symbol","interval","open_time"],name="unique_candle")]
        indexes=[models.Index(fields=["symbol","interval","-open_time"])]
    def __str__(self): return f"{self.symbol} {self.interval} {self.open_time}"

class AnalysisRun(models.Model):
    created_at=models.DateTimeField(auto_now_add=True); symbol=models.CharField(max_length=20); interval=models.CharField(max_length=8)
    candle_close_time=models.DateTimeField(); strategy_version=models.CharField(max_length=30,default="trend-v1")
    status=models.CharField(max_length=20,choices=[("rejected","Rejected"),("watch","Watch"),("confirmed","Confirmed"),("error","Error")])
    score=models.PositiveSmallIntegerField(default=0); reasons=models.JSONField(default=list); warnings=models.JSONField(default=list); features=models.JSONField(default=dict)
    class Meta: constraints=[models.UniqueConstraint(fields=["symbol","interval","candle_close_time","strategy_version"],name="unique_analysis")]

class Signal(models.Model):
    STATES=[("active","Active"),("target1","Target 1"),("won","Won"),("stopped","Stopped"),("expired","Expired"),("invalidated","Invalidated")]
    analysis=models.OneToOneField(AnalysisRun,on_delete=models.PROTECT,related_name="signal")
    direction=models.CharField(max_length=8,default="long"); entry_low=models.DecimalField(max_digits=24,decimal_places=8); entry_high=models.DecimalField(max_digits=24,decimal_places=8)
    stop_loss=models.DecimalField(max_digits=24,decimal_places=8); target_1=models.DecimalField(max_digits=24,decimal_places=8); target_2=models.DecimalField(max_digits=24,decimal_places=8)
    risk_reward=models.DecimalField(max_digits=8,decimal_places=3); confidence=models.PositiveSmallIntegerField(); ml_probability=models.FloatField(null=True,blank=True)
    expires_at=models.DateTimeField(); state=models.CharField(max_length=20,choices=STATES,default="active"); created_at=models.DateTimeField(auto_now_add=True); resolved_at=models.DateTimeField(null=True,blank=True)
    def __str__(self): return f"{self.analysis.symbol} {self.direction} {self.state}"

class SignalEvent(models.Model):
    signal=models.ForeignKey(Signal,on_delete=models.CASCADE,related_name="events"); event_type=models.CharField(max_length=40); price=models.DecimalField(max_digits=24,decimal_places=8,null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True); details=models.JSONField(default=dict)

class BacktestRun(models.Model):
    created_at=models.DateTimeField(auto_now_add=True); symbol=models.CharField(max_length=20); interval=models.CharField(max_length=8); strategy_version=models.CharField(max_length=30,default="trend-v1"); start=models.DateTimeField(); end=models.DateTimeField(); status=models.CharField(max_length=20,default="pending"); parameters=models.JSONField(default=dict); metrics=models.JSONField(default=dict)

class MLModel(models.Model):
    name=models.CharField(max_length=80); version=models.CharField(max_length=40,unique=True); artifact_path=models.CharField(max_length=255); created_at=models.DateTimeField(auto_now_add=True); training_start=models.DateTimeField(); training_end=models.DateTimeField(); metrics=models.JSONField(default=dict); feature_names=models.JSONField(default=list); active=models.BooleanField(default=False); approved=models.BooleanField(default=False)
