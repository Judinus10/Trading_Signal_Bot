# Personal Crypto Trading Signal Bot

A private, signal-only crypto market analysis application. It uses public Binance candle data, creates explainable long setups, tracks results, backtests the same strategy logic, and can train a calibrated machine-learning confirmation model from resolved signals.

> This project does **not** place, modify, or cancel trades. It contains no exchange trading-key form and no order API client. Signals are informational and can lose money.

## Included

- Django 5 application, admin, private dashboard and REST API
- Public Binance OHLCV ingestion
- EMA, RSI, ATR, volume, structure and multi-factor scoring
- Entry zone, stop, two targets, expiry and reward-to-risk
- Idempotent analysis and duplicate protection
- Telegram alerts (optional)
- Signal outcome tracking
- Historical backtest command with fees, slippage and conservative same-candle handling
- Django-managed ML training command using scikit-learn
- Model registry, approval fields and shadow/disabled-by-default operation
- Celery/Redis scheduled jobs
- PostgreSQL production and SQLite development support
- Docker Compose, migrations, tests and API documentation

## Architecture

1. `exchange.py` fetches public candles.
2. `indicators.py` creates versionable numeric features.
3. `strategy.py` produces an explainable deterministic decision.
4. `ml.py` optionally evaluates an approved trained artifact.
5. `orchestrator.py` stores one analysis per strategy/candle and creates a signal.
6. `notifications.py` sends a private Telegram message.
7. `tasks.py` schedules ingestion, analysis and outcome tracking.
8. `backtest.py` replays the strategy without future-candle access.

## Quick start (local SQLite)

Requirements: Python 3.12+, pip, and optionally Redis for background workers.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Django will redirect to the admin login when needed. API documentation is at `/api/docs/` after login.

## Load data and generate analysis

The strategy requires at least 210 completed candles.

```bash
python manage.py ingest_market BTCUSDT 1h --limit 500
python manage.py ingest_market BTCUSDT 4h --limit 500
python manage.py ingest_market BTCUSDT 1d --limit 500
python manage.py analyse_market BTCUSDT 1h
python manage.py backtest_strategy BTCUSDT 1h
```

Repeat ingestion for ETHUSDT or change `TRADING_SYMBOLS` in `.env`.

## Telegram setup

1. Create a bot through Telegram BotFather.
2. Send a message to the bot and determine your private chat ID.
3. Set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and `TELEGRAM_ENABLED=true` in `.env`.
4. Keep `.env` out of Git. Never paste the token into code.

When Telegram is disabled, signals are still stored and visible in the dashboard/API.

## Machine-learning training through Django

Django owns the data, command, model registry and activation workflow. Scikit-learn performs the mathematical training. Only resolved `won` and `stopped` signals become labels.

```bash
python manage.py train_model --min-samples 100
```

The command:

- uses a chronological dataset;
- applies `TimeSeriesSplit` rather than random splitting;
- calculates out-of-fold Brier score and ROC AUC;
- trains a calibrated logistic-regression baseline;
- writes the artifact to `artifacts/signal_model.joblib`;
- registers metrics and the training window in Django admin.

Review the metrics, then mark exactly one model both `approved` and `active` in admin. Set `ML_ENABLED=true` only after adequate out-of-sample and paper evidence. Inference refuses artifacts that do not have an approved, active registry record. The supplied inference code remains disabled by default. A model trained from a tiny dataset is not trustworthy.

## Background workers

With Redis running:

```bash
celery -A config worker -l INFO
celery -A config beat -l INFO
```

The default schedule scans hourly and tracks active signals every five minutes. For production, align the hourly scan shortly after candle close rather than relying on a relative interval.

## Docker production-style start

```bash
cp .env.example .env
# Change SECRET_KEY and review every value.
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```

Use a reverse proxy with HTTPS. Do not expose PostgreSQL or Redis publicly.

## REST endpoints

- `GET /api/v1/health/`
- `GET /api/v1/candles/?symbol=BTCUSDT&interval=1h`
- `GET /api/v1/analyses/`
- `GET /api/v1/signals/`
- `POST /api/v1/analyse/` with `{"symbol":"BTCUSDT","interval":"1h"}`
- `GET /api/v1/backtests/`
- `GET /api/v1/models/`

All endpoints require a logged-in Django session. The browsable schema is `/api/docs/`.

## Tests

```bash
pytest
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Important production work before relying on signals

- Run several years of data through the backtest and inspect regime-specific results.
- Add a paginated historical importer; Binance limits one kline response to 1,000 rows.
- Run walk-forward and untouched out-of-sample tests.
- Paper-track enough independent signals.
- Add alerting for stale candles and database/worker failures.
- Put the web service behind HTTPS and enable MFA for the owner.
- Back up PostgreSQL and perform a restoration test.
- Do not enable ML because a training command completed. Require meaningful calibration and improvement over the rule-only baseline.

## Known scope boundaries

- Initial strategy is long-only spot analysis.
- Higher-timeframe confirmation uses the configured 4h and 1d completed-candle datasets. If either lacks 200 candles, agreement fails closed.
- Backtest output currently prints metrics; persist detailed run/trade records before large experiment campaigns.
- The dashboard is intentionally lightweight; Django admin provides management functions.
- No automatic trading is included.

## License and disclaimer

Private-use project. Add the license you want before redistribution. This software is educational decision-support, not financial advice. Crypto assets are highly volatile and losses can be total.
