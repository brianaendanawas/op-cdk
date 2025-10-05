from constructs import Construct
from aws_cdk import (
    Stack, CfnOutput, RemovalPolicy, Duration,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)

class OutfitPlannerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, stage: str = "dev", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- 0) per-stage flags/values ---
        is_prod = stage == "prod"

        # Replace with the CloudFront domain that serves your UI (no trailing slash)
        allowed_origin = "*" if not is_prod else "https://d13vpwdkbkv4ik.cloudfront.net"

        # --- 1) DynamoDB ---
        table = dynamodb.Table(
            self, "Table",
            table_name=f"OutfitPlanner-{stage}",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN if is_prod else RemovalPolicy.DESTROY
        )

        # --- 2) Lambdas ---
        env = {
            "TABLE_NAME": table.table_name,
            "ALLOWED_ORIGIN": allowed_origin,
            "STAGE": stage
        }

        # Stable names make log tailing easy
        items_fn = _lambda.Function(
            self, "ItemsFn",
            function_name=f"OutfitPlanner-{stage}-Items",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="items.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            environment=env
        )

        outfits_fn = _lambda.Function(
            self, "OutfitsFn",
            function_name=f"OutfitPlanner-{stage}-Outfits",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="outfits.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            environment=env
        )

        health_fn = _lambda.Function(
            self, "HealthFn",
            function_name=f"OutfitPlanner-{stage}-Health",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="health.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(5),
            environment=env
        )

        # --- 3) Permissions (simple & safe now) ---
        # This fixes the AccessDenied on dynamodb:Scan
        table.grant_read_write_data(items_fn)
        table.grant_read_write_data(outfits_fn)
        # (health_fn doesn't touch DynamoDB)

        # --- 4) API Gateway ---
        api = apigw.RestApi(
            self, "Api",
            rest_api_name=f"OutfitPlanner-{stage}",
            endpoint_types=[apigw.EndpointType.EDGE],
            deploy_options=apigw.StageOptions(stage_name=stage),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS if not is_prod else [allowed_origin],
                allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
            )
        )

        # /health
        health = api.root.add_resource("health")
        health.add_method("GET", apigw.LambdaIntegration(health_fn))

        # /items
        items = api.root.add_resource("items")
        items.add_method("GET", apigw.LambdaIntegration(items_fn))
        items.add_method("POST", apigw.LambdaIntegration(items_fn))

        # /outfits and /outfits/{id}
        outfits = api.root.add_resource("outfits")
        outfits.add_method("GET", apigw.LambdaIntegration(outfits_fn))
        outfits.add_method("POST", apigw.LambdaIntegration(outfits_fn))

        outfit_id = outfits.add_resource("{id}")
        outfit_id.add_method("GET", apigw.LambdaIntegration(outfits_fn))
        outfit_id.add_method("PATCH", apigw.LambdaIntegration(outfits_fn))
        outfit_id.add_method("DELETE", apigw.LambdaIntegration(outfits_fn))

        # --- 5) Clean outputs ---
        CfnOutput(self, "ApiUrl", value=api.url_for_path("/"))
        CfnOutput(self, "HealthUrl", value=api.url_for_path("/health"))
        CfnOutput(self, "ItemsUrl", value=api.url_for_path("/items"))
        CfnOutput(self, "OutfitsUrl", value=api.url_for_path("/outfits"))
        CfnOutput(self, "TableName", value=table.table_name)
        CfnOutput(self, "Stage", value=stage)
        CfnOutput(self, "AllowedOrigin", value=allowed_origin)

