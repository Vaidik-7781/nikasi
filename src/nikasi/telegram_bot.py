"""Telegram webhook. Privacy by design (DPDP): we keep only chat_id + the 3 nearest
spot ids, for 24 h, refreshed on each interaction. Location is used once and never stored.
/stop erases the record immediately. Token and webhook secret arrive as Lambda env vars
resolved by CloudFormation from Secrets Manager (see infra/template.yaml)."""
from __future__ import annotations
import hmac, json, os, time, urllib.request
from . import templates
from .geo import nearest

TTL_S = 24 * 3600
CONSENT = ("Nikasi warns about flooded underpasses in Delhi. Share your location and I will "
           "check the 3 nearest ones and alert you if they turn NO-GO. I store only your chat id "
           "and those spot names for 24 hours. Your location is not stored. /stop erases everything. "
           "This is guidance, not a guarantee: if water is on the road, do not enter.")

def _status_lines(spot_ids, states):
    out = []
    for sid in spot_ids:
        st = states.get(sid)
        out.append(templates.render(st) if st else f"NO-GO (no data): {sid}. Treat as closed.")
    return out

def handle_update(update, spots, states, subs, send, now=None):
    msg = update.get("message") or {}
    chat = (msg.get("chat") or {}).get("id")
    if chat is None:
        return
    now = int(now or time.time())
    text = (msg.get("text") or "").strip().lower()
    if text.startswith("/start") or text.startswith("/help"):
        send(chat, CONSENT)
    elif text.startswith("/stop"):
        subs.delete_item(Key={"chat_id": str(chat)})
        send(chat, "Done. Your data is erased and you will get no more alerts.")
    elif "location" in msg:
        loc = msg["location"]
        ids = [s["id"] for s in nearest(loc["latitude"], loc["longitude"], spots)]
        subs.put_item(Item={"chat_id": str(chat), "spot_ids": ids, "ttl": now + TTL_S})
        send(chat, "\n".join(_status_lines(ids, states)))
    elif text.startswith("/status"):
        rec = subs.get_item(Key={"chat_id": str(chat)}).get("Item")
        if not rec:
            send(chat, "Share your location first (attachment icon, Location).")
        else:
            send(chat, "\n".join(_status_lines(rec["spot_ids"], states)))
    else:
        send(chat, "Send your location, or use /status, /stop, /help.")

def tg_send(chat_id, text):
    req = urllib.request.Request(f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": text}).encode(), headers={"content-type": "application/json"})
    urllib.request.urlopen(req, timeout=8).read()

def lambda_handler(event, context, state_table=None, subs=None, send=None):
    hdr = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if not hmac.compare_digest(hdr.get("x-telegram-bot-api-secret-token", ""), os.environ.get("WEBHOOK_SECRET") or "\0"):
        return {"statusCode": 403, "body": "forbidden"}
    if state_table is None or subs is None:
        import boto3
        ddb = boto3.resource("dynamodb")
        state_table = state_table or ddb.Table(os.environ["STATE_TABLE"])
        subs = subs or ddb.Table(os.environ["SUBS_TABLE"])
    spots = json.load(open(os.path.join(os.path.dirname(__file__), "spots.json")))["spots"]
    states = {i["spot_id"]: i for i in state_table.scan().get("Items", [])}
    handle_update(json.loads(event.get("body") or "{}"), spots, states, subs, send or tg_send)
    return {"statusCode": 200, "body": "ok"}
