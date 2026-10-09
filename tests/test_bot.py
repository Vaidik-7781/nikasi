from nikasi.telegram_bot import handle_update, CONSENT
from nikasi.sender import deliver

SPOTS = [{"id": "a", "name": "A", "lat": 28.63, "lon": 77.22}, {"id": "b", "name": "B", "lat": 28.50, "lon": 77.30},
         {"id": "c", "name": "C", "lat": 28.66, "lon": 77.14}, {"id": "d", "name": "D", "lat": 19.0, "lon": 72.8}]
STATES = {"a": {"name": "A", "state": "GO", "act_as": "GO", "reasons": []}}

class Subs:
    def __init__(self): self.d = {}
    def put_item(self, Item): self.d[Item["chat_id"]] = Item
    def get_item(self, Key): return {"Item": self.d[Key["chat_id"]]} if Key["chat_id"] in self.d else {}
    def delete_item(self, Key): self.d.pop(Key["chat_id"], None)

def run():
    out = []
    return out, Subs(), lambda c, t: out.append((c, t))

def test_location_subscribes_to_nearest_three_and_missing_state_is_no_go():
    out, subs, send = run()
    handle_update({"message": {"chat": {"id": 1}, "location": {"latitude": 28.63, "longitude": 77.2}}}, SPOTS, STATES, subs, send, now=1000)
    assert subs.d["1"]["spot_ids"] == ["a", "c", "b"] and subs.d["1"]["ttl"] == 1000 + 86400
    assert "NO-GO (no data)" in out[0][1] and "latitude" not in str(subs.d)

def test_stop_erases():
    out, subs, send = run()
    subs.put_item({"chat_id": "1", "spot_ids": ["a"]})
    handle_update({"message": {"chat": {"id": 1}, "text": "/stop"}}, SPOTS, STATES, subs, send)
    assert "1" not in subs.d

def test_start_shows_consent():
    out, subs, send = run()
    handle_update({"message": {"chat": {"id": 1}, "text": "/start"}}, SPOTS, STATES, subs, send)
    assert out[0][1] == CONSENT

def test_sender_is_idempotent():
    seen, sent = set(), []
    def claim(k):
        if k in seen: return False
        seen.add(k); return True
    body = {"spot_id": "a", "text": "NO-GO", "dedupe_id": "x"}
    scan = lambda s: [{"chat_id": "1"}, {"chat_id": "2"}]
    deliver(body, scan, claim, lambda c, t: sent.append(c)); deliver(body, scan, claim, lambda c, t: sent.append(c))
    assert sent == ["1", "2"]
