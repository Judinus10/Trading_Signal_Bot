from datetime import datetime, timezone
from pathlib import Path
import joblib, numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_predict
from signals.models import AnalysisRun, Signal, MLModel
from signals.services.indicators import FEATURE_COLUMNS

class Command(BaseCommand):
    help="Train and register a calibrated signal-confirmation model from resolved signals"
    def add_arguments(self,p): p.add_argument("--min-samples",type=int,default=100)
    def handle(self,*a,**o):
        rows=AnalysisRun.objects.filter(signal__state__in=["won","stopped"]).select_related("signal").order_by("candle_close_time")
        X=[]; y=[]; dates=[]
        for r in rows:
            if all(k in r.features for k in FEATURE_COLUMNS): X.append([r.features[k] for k in FEATURE_COLUMNS]); y.append(1 if r.signal.state=="won" else 0); dates.append(r.candle_close_time)
        if len(X)<o["min_samples"]: raise CommandError(f"Need {o['min_samples']} resolved samples; found {len(X)}")
        X=np.asarray(X); y=np.asarray(y); split=TimeSeriesSplit(n_splits=5)
        base=LogisticRegression(max_iter=2000,class_weight="balanced"); pred=cross_val_predict(base,X,y,cv=split,method="predict_proba")[:,1]
        model=CalibratedClassifierCV(LogisticRegression(max_iter=2000,class_weight="balanced"),cv=split); model.fit(X,y)
        path=Path(settings.ML_MODEL_PATH); path.parent.mkdir(parents=True,exist_ok=True); joblib.dump({"model":model,"features":FEATURE_COLUMNS},path)
        version=datetime.now(timezone.utc).strftime("signal-%Y%m%d%H%M%S")
        record=MLModel.objects.create(name="Calibrated logistic baseline",version=version,artifact_path=str(path),training_start=dates[0],training_end=dates[-1],feature_names=FEATURE_COLUMNS,metrics={"samples":len(y),"brier":float(brier_score_loss(y,pred)),"roc_auc":float(roc_auc_score(y,pred)) if len(set(y))>1 else None})
        self.stdout.write(self.style.SUCCESS(f"Created {record.version}: {record.metrics}. Approve in admin before enabling ML_ENABLED."))
