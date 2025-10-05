import json, os, time

def handler(event, context):
    body = {
        "ok": True,
        "service": "OutfitPlanner",
        "stage": os.getenv("STAGE", "dev"),
        "table": os.getenv("TABLE_NAME", ""),
        "time": int(time.time())
    }
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": os.getenv("ALLOWED_ORIGIN", "*"),
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }

