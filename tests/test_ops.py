import json
from nikasi.ops import lambda_handler as ops

class S:
    def __init__(self, items): self.items = items
    def scan(self): return {"Items": self.items}

class D:
    def __init__(self): self.rows = []
    def put_item(self, Item): self.rows.append(Item)

NOGO = {"spot_id": "a", "name": "A", "state": "NO-GO", "act_as": "NO-GO"}
GO = {"spot_id": "b", "name": "B", "state": "GO", "act_as": "GO"}

def ev(route, body=None, email="officer@mcd.example"):
    claims = {"email": email} if email else {}
    return {"routeKey": route, "body": json.dumps(body) if body else None,
            "requestContext": {"authorizer": {"jwt": {"claims": claims}}}}

def test_requires_signed_in_user():
    assert ops(ev("GET /dispatch", email=None), None, S([NOGO]), D())["statusCode"] == 403

def test_get_proposes_only_no_go():
    r = ops(ev("GET /dispatch"), None, S([NOGO, GO]), D())
    b = json.loads(r["body"])
    assert r["statusCode"] == 200 and b["spots"] == ["a"] and b["status"] == "PENDING_APPROVAL"

def test_approval_records_token_identity_not_body():
    d = D()
    r = ops(ev("POST /dispatch/approve", {"spots": ["a"], "approved_by": "someone else"}), None, S([NOGO, GO]), d)
    b = json.loads(r["body"])
    assert r["statusCode"] == 200 and b["approved_by"] == "officer@mcd.example" and d.rows[0]["status"] == "APPROVED"

def test_stale_review_is_rejected():
    d = D()
    r = ops(ev("POST /dispatch/approve", {"spots": ["a", "z"]}), None, S([NOGO]), d)
    assert r["statusCode"] == 409 and not d.rows

def test_nothing_to_approve():
    assert ops(ev("POST /dispatch/approve", {"spots": []}), None, S([GO]), D())["statusCode"] == 400
