import requests
from django.conf import settings

def format_signal(signal):
    a=signal.analysis
    return (f"🟢 LONG SIGNAL — {a.symbol}\n\nTimeframe: {a.interval}\nEntry: {signal.entry_low} - {signal.entry_high}\nStop: {signal.stop_loss}\nTarget 1: {signal.target_1}\nTarget 2: {signal.target_2}\nRisk/Reward: 1:{signal.risk_reward}\nScore: {signal.confidence}/100\n\nReasons:\n"+"\n".join(f"✓ {r}" for r in a.reasons)+f"\n\nExpires: {signal.expires_at:%Y-%m-%d %H:%M UTC}\nSignal only. No automatic trade was placed.")

def send_signal(signal):
    if not settings.TELEGRAM_ENABLED: return {"skipped":True,"reason":"Telegram disabled"}
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID: raise RuntimeError("Telegram credentials missing")
    r=requests.post(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",json={"chat_id":settings.TELEGRAM_CHAT_ID,"text":format_signal(signal)},timeout=15); r.raise_for_status(); return r.json()
