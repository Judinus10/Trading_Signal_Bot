from pathlib import Path
import joblib
import numpy as np
from django.conf import settings
from .indicators import FEATURE_COLUMNS
from ..models import MLModel

def predict(features):
    record=MLModel.objects.filter(active=True,approved=True).order_by("-created_at").first()
    if not settings.ML_ENABLED or record is None: return None
    path=Path(record.artifact_path)
    if not path.is_absolute(): path=Path(settings.BASE_DIR)/path
    if not path.exists(): return None
    bundle=joblib.load(path); x=np.array([[features[name] for name in bundle["features"]]])
    return float(bundle["model"].predict_proba(x)[0,1])
