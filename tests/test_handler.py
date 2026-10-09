from datetime import timezone
from nikasi.handler import lambda_handler
from nikasi.risk import Weather

class T:
    items = []
    def put_item(self, Item): self.items.append(Item)

def test_handler_writes_unknown_when_fetch_fails():
    t = T()
    r = lambda_handler({}, None, table=t, fetch=lambda *a: None)
    assert r["count"] == len(t.items) >= 1
    assert all(i["state"] == "UNKNOWN" and i["act_as"] == "NO-GO" for i in t.items)
