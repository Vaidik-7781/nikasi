class T:
    def __init__(self, prev=None): self.items, self.prev = [], prev
    def put_item(self, Item): self.items.append(Item)
    def get_item(self, Key): return {"Item": self.prev} if self.prev else {}

class Q:
    def __init__(self): self.sent = []
    def send_message(self, **kw): self.sent.append(kw)

def test_handler_writes_unknown_when_fetch_fails():
    from nikasi.handler import lambda_handler
    t = T()
    r = lambda_handler({}, None, table=t, fetch=lambda *a: None)
    assert r["count"] == len(t.items) >= 1
    assert all(i["state"] == "UNKNOWN" and i["act_as"] == "NO-GO" and "lat" in i for i in t.items)

def test_state_change_enqueues_alert(monkeypatch):
    from nikasi.handler import lambda_handler
    monkeypatch.setenv("ALERT_QUEUE_URL", "q")
    q = Q()
    lambda_handler({}, None, table=T(prev={"act_as": "GO"}), fetch=lambda *a: None, sqs=q)
    assert q.sent and "NO-GO" in q.sent[0]["MessageBody"]

def test_no_change_no_alert(monkeypatch):
    from nikasi.handler import lambda_handler
    monkeypatch.setenv("ALERT_QUEUE_URL", "q")
    q = Q()
    lambda_handler({}, None, table=T(prev={"act_as": "NO-GO"}), fetch=lambda *a: None, sqs=q)
    assert not q.sent
