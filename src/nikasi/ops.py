"""Ward console API (behind a Cognito JWT authorizer). GET /dispatch proposes a barricade
list from current state; POST /dispatch/approve records a named person's approval.
The approver is taken from the verified token, never from the request body."""
from __future__ import annotations
import json, os
from datetime import datetime, timezone
from .agents import dispatcher

H = {"content-type": "application/json"}

def _r(code, body):
    return {"statusCode": code, "headers": H, "body": json.dumps(body, default=str)}

def lambda_handler(event, context, state_table=None, disp_table=None):
    claims = ((event.get("requestContext") or {}).get("authorizer") or {}).get("jwt", {}).get("claims", {})
    who = claims.get("email") or claims.get("cognito:username") or claims.get("username")
    if not who:
        return _r(403, {"error": "not signed in"})
    if state_table is None or disp_table is None:
        import boto3
        ddb = boto3.resource("dynamodb")
        state_table = state_table or ddb.Table(os.environ["STATE_TABLE"])
        disp_table = disp_table or ddb.Table(os.environ["DISPATCH_TABLE"])
    d = dispatcher.build(state_table.scan().get("Items", []))
    route = event.get("routeKey", "")
    if route == "GET /dispatch":
        return _r(200, d)
    if route == "POST /dispatch/approve":
        body = json.loads(event.get("body") or "{}")
        if sorted(body.get("spots", [])) != sorted(d["spots"]):
            return _r(409, {"error": "conditions changed, reload and review again", "current": d})
        if not d["spots"]:
            return _r(400, {"error": "nothing to approve"})
        now = datetime.now(timezone.utc).isoformat()
        ok = dispatcher.approve(d, who, now)
        disp_table.put_item(Item={"id": now, **ok})
        return _r(200, ok)
    return _r(404, {"error": "unknown route"})
