"""SQS consumer: sends one alert to every subscriber of the spot. Idempotent per
(dedupe_id, chat): a redelivered message cannot double-send. Any failure raises so
SQS retries, and after 3 tries the message lands in the DLQ."""
from __future__ import annotations
import json, os, time

def deliver(body, subs_scan, claim, send):
    for sub in subs_scan(body["spot_id"]):
        if claim(f'{body["dedupe_id"]}|{sub["chat_id"]}'):
            send(sub["chat_id"], body["text"])

def lambda_handler(event, context):
    import boto3
    from boto3.dynamodb.conditions import Attr
    from botocore.exceptions import ClientError
    from .telegram_bot import tg_send
    ddb = boto3.resource("dynamodb")
    subs, dedupe = ddb.Table(os.environ["SUBS_TABLE"]), ddb.Table(os.environ["DEDUPE_TABLE"])
    def scan(spot_id):
        return subs.scan(FilterExpression=Attr("spot_ids").contains(spot_id)).get("Items", [])
    def claim(key):
        try:
            dedupe.put_item(Item={"k": key, "ttl": int(time.time()) + 86400},
                            ConditionExpression="attribute_not_exists(k)")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise
    for rec in event["Records"]:
        deliver(json.loads(rec["body"]), scan, claim, tg_send)
