import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-development-key")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [x.strip() for x in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "django_filters", "drf_spectacular", "signals.apps.SignalsConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
db = urlparse(os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"))
if db.scheme.startswith("postgres"):
    DATABASES={"default":{"ENGINE":"django.db.backends.postgresql","NAME":db.path.lstrip('/'),"USER":db.username,"PASSWORD":db.password,"HOST":db.hostname,"PORT":db.port or 5432}}
else:
    DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/(db.path.lstrip('/') or 'db.sqlite3')}}
AUTH_PASSWORD_VALIDATORS = [{"NAME":f"django.contrib.auth.password_validation.{x}"} for x in ["UserAttributeSimilarityValidator","MinimumLengthValidator","CommonPasswordValidator","NumericPasswordValidator"]]
LANGUAGE_CODE="en-us"; TIME_ZONE=os.getenv("TIME_ZONE","UTC"); USE_I18N=True; USE_TZ=True
STATIC_URL="static/"; STATIC_ROOT=BASE_DIR/"staticfiles"; STATICFILES_DIRS=[BASE_DIR/"static"]
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"; LOGIN_URL="/admin/login/"
REST_FRAMEWORK={"DEFAULT_AUTHENTICATION_CLASSES":["rest_framework.authentication.SessionAuthentication"],"DEFAULT_PERMISSION_CLASSES":["rest_framework.permissions.IsAuthenticated"],"DEFAULT_FILTER_BACKENDS":["django_filters.rest_framework.DjangoFilterBackend","rest_framework.filters.OrderingFilter"],"DEFAULT_SCHEMA_CLASS":"drf_spectacular.openapi.AutoSchema"}
SPECTACULAR_SETTINGS={"TITLE":"Crypto Signal Bot API","VERSION":"1.0.0","SERVE_INCLUDE_SCHEMA":False}
CELERY_BROKER_URL=os.getenv("REDIS_URL","redis://localhost:6379/0"); CELERY_RESULT_BACKEND=CELERY_BROKER_URL; CELERY_TIMEZONE="UTC"
CELERY_BEAT_SCHEDULE={"scan-hourly":{"task":"signals.tasks.scan_markets","schedule":3600.0},"track-signals":{"task":"signals.tasks.track_open_signals","schedule":300.0}}
BINANCE_BASE_URL=os.getenv("BINANCE_BASE_URL","https://api.binance.com")
TRADING_SYMBOLS=[x.strip().upper() for x in os.getenv("TRADING_SYMBOLS","BTCUSDT,ETHUSDT").split(',') if x.strip()]
ENTRY_INTERVAL=os.getenv("ENTRY_INTERVAL","1h"); CONTEXT_INTERVAL=os.getenv("CONTEXT_INTERVAL","4h"); REGIME_INTERVAL=os.getenv("REGIME_INTERVAL","1d")
SIGNAL_SCORE_THRESHOLD=int(os.getenv("SIGNAL_SCORE_THRESHOLD","70")); WATCH_SCORE_THRESHOLD=int(os.getenv("WATCH_SCORE_THRESHOLD","60")); MIN_RISK_REWARD=float(os.getenv("MIN_RISK_REWARD","2.0"))
TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN",""); TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID",""); TELEGRAM_ENABLED=os.getenv("TELEGRAM_ENABLED","false").lower()=="true"
ML_ENABLED=os.getenv("ML_ENABLED","false").lower()=="true"; ML_MODEL_PATH=str(BASE_DIR/os.getenv("ML_MODEL_PATH","artifacts/signal_model.joblib"))
SECURE_CONTENT_TYPE_NOSNIFF=True; X_FRAME_OPTIONS="DENY"; SESSION_COOKIE_HTTPONLY=True; CSRF_COOKIE_HTTPONLY=True
if not DEBUG:
    SECURE_SSL_REDIRECT=True; SESSION_COOKIE_SECURE=True; CSRF_COOKIE_SECURE=True; SECURE_HSTS_SECONDS=31536000; SECURE_HSTS_INCLUDE_SUBDOMAINS=True; SECURE_HSTS_PRELOAD=True
