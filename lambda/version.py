import json, os, time

def handler(event, context):
    body = {
        "version": os.getenv("APP_VERSION", "dev"),
        "stage": os.getenv("STAGE", "dev"),
        "deployedAt": int(time.time())
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
