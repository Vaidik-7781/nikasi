"""API Gateway (HTTP API) Lambda: GET /spots and GET /spots/{id}. Read-only."""
from __future__ import annotations
import json, os

H = {"content-type": "application/json", "access-control-allow-origin": "*"}

def _resp(code, body):
    return {"statusCode": code, "headers": H, "body": json.dumps(body, default=str)}

def lambda_handler(event, context, table=None):
    if table is None:
        import boto3
        table = boto3.resource("dynamodb").Table(os.environ["STATE_TABLE"])
    sid = (event.get("pathParameters") or {}).get("id")
    if sid:
        item = table.get_item(Key={"spot_id": sid}).get("Item")
        if not item:
            # a missing row is NOT a safe row: say unknown, act as no-go
            return _resp(404, {"spot_id": sid, "state": "UNKNOWN", "act_as": "NO-GO"})
        return _resp(200, item)
    items = table.scan().get("Items", [])
    return _resp(200, {"spots": items})
