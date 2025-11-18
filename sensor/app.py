# controller/app.py
"""
FastAPI controller that receives alerts from detector and sends notifications.
Optionally can run a blocking action (iptables or router API). The block
function here is a stub — replace with router/OpenWrt API calls if available.
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import subprocess
import os
import requests
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

class Alert(BaseModel):
    mac: str
    score: float
    features: dict = None
    time: float = None

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.info("[+] Telegram not configured. Message: %s", msg)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        logging.error("Telegram send failed: %s", e)

def block_mac_stub(mac):
    """
    Blocking a MAC depends on your network: OpenWrt API, router SSH, or iptables (if gateway).
    This is a stub for demonstration. Do NOT call iptables on machines that are not
    the network gateway. Implement safe router API calls here instead.
    """
    logging.info("[+] block_mac_stub called for %s (no-op)", mac)
    return True

@app.post("/alert")
async def alert_endpoint(alert: Alert, request: Request):
    msg = f"ALERT: {alert.mac} flagged as suspicious (score={alert.score:.4f})"
    logging.info(msg)
    # send notification
    send_telegram(msg)
    # optional block
    try:
        block_mac_stub(alert.mac)
    except Exception as e:
        logging.error("Block action failed: %s", e)
    return {"ok": True}
