import os, json, uuid, time, boto3
from decimal import Decimal

TABLE = os.environ["TABLE_NAME"]
ddb = boto3.resource("dynamodb").Table(TABLE)

HEAD = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS",
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
    # API Gateway provides "resource" as the matched route template, e.g., "/outfits" or "/outfits/{id}"
    resource = event.get("resource", "")
    method = event.get("httpMethod", "GET")
    path_params = event.get("pathParameters") or {}

    # List
    if method == "GET" and resource.endswith("/outfits"):
        resp = ddb.scan()
        outfits = [x for x in resp.get("Items", []) if x.get("pk") == "OUTFIT"]
        return ok(outfits)

    # Create
    if method == "POST" and resource.endswith("/outfits"):
        body = json.loads(event.get("body") or "{}")
        name = (body.get("name") or "").strip()
        items = body.get("items") or []
        if not name:
            return bad("name required")
        if not isinstance(items, list):
            return bad("items must be an array")

        oid = body.get("id") or uuid.uuid4().hex[:8]
        ot = {
            "pk": "OUTFIT",
            "sk": f"OUTFIT#{oid}",
            "id": oid,
            "name": name,
            "items": items,
            "created": int(time.time()),
        }
        ddb.put_item(Item=ot)
        return ok(ot, 201)

    # GET/DELETE/PATCH by id
    if "id" in path_params:
        oid = path_params["id"]
        key = {"pk": "OUTFIT", "sk": f"OUTFIT#{oid}"}

        if method == "GET":
            resp = ddb.get_item(Key=key)
            it = resp.get("Item")
            return ok(it) if it else bad("not found", 404)

        if method == "DELETE":
            ddb.delete_item(Key=key)
            return ok({"deleted": oid})

        if method == "PATCH":
            body = json.loads(event.get("body") or "{}")
            expr, names, vals = [], {}, {}

            if body.get("name"):
                names["#n"] = "name"
                vals[":n"] = body["name"]
                expr.append("#n = :n")

            if isinstance(body.get("items"), list):
                names["#it"] = "items"
                vals[":it"] = body["items"]
                expr.append("#it = :it")

            if not expr:
                return bad("no fields to update")

            ddb.update_item(
                Key=key,
                UpdateExpression="SET " + ", ".join(expr),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=vals,
            )
            resp = ddb.get_item(Key=key)
            return ok(resp.get("Item"))

    return bad("Unsupported route", 404)

