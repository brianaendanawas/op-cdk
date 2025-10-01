import os, json, uuid, time, boto3
from decimal import Decimal

TABLE = os.environ["TABLE_NAME"]
ddb = boto3.resource("dynamodb").Table(TABLE)

HEAD = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key"
}

def to_py(v):
    """Recursively convert DynamoDB Decimals to int/float to make json.dumps happy."""
    if isinstance(v, list):
        return [to_py(x) for x in v]
    if isinstance(v, dict):
        return {k: to_py(val) for k, val in v.items()}
    if isinstance(v, Decimal):
        return int(v) if v % 1 == 0 else float(v)
    return v

def ok(body, code=200):
    return {
        "statusCode": code,
        "headers": HEAD,
        "body": json.dumps(to_py(body))
    }

def bad(msg, code=400):
    return ok({"error": msg}, code)

def handler(event, context):
    method = event.get("httpMethod", "GET")

    if method == "GET":
        # Demo simplicity: scan + filter by pk
        resp = ddb.scan()
        items = [x for x in resp.get("Items", []) if x.get("pk") == "ITEM"]
        return ok(items)

    if method == "POST":
        body = json.loads(event.get("body") or "{}")
        name = (body.get("name") or "").strip()
        if not name:
            return bad("name required")

        item_id = body.get("id") or uuid.uuid4().hex[:8]
        it = {
            "pk": "ITEM",
            "sk": f"ITEM#{item_id}",
            "id": item_id,
            "name": name,
            "type": (body.get("type") or "").strip(),
            "color": (body.get("color") or "").strip(),
            "tags": body.get("tags") or [],
            "created": int(time.time()),
        }
        ddb.put_item(Item=it)
        return ok(it, 201)

    return bad("Unsupported method", 405)

