from constructs import Construct
from aws_cdk import (
    Stack, CfnOutput, RemovalPolicy, Duration,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_iam as iam,
)

class OutfitPlannerStack(Stack):
    def __init__(self, scope: Construct, id: str, *, stage: str = "dev", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # --- 0) simple per-stage flags/values ---
        is_prod = stage == "prod"

        # Your CloudFront domain (for CORS). Replace after first deploy if unknown.
        # Example: d123abcde8.cloudfront.net  (NO trailing slash)
        allowed_origin = "*" if not is_prod else "https://d13vpwdkbkv4ik.cloudfront.net"

        # --- 1) DynamoDB (separate per stage; safer RETAIN on prod) ---
        table = dynamodb.Table(
            self, "Table",
            table_name=f"OutfitPlanner-{stage}",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN if is_prod else RemovalPolicy.DESTROY
        )

        # --- 2) Lambdas (timeouts small; env passes table + CORS) ---
        common_env = {
            "TABLE_NAME": table.table_name,
            "ALLOWED_ORIGIN": allowed_origin
        }

        items_fn = lambda_.Function(
            self, "ItemsFn",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="items.handler",
            code=lambda_.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            environment=common_env
        )

        outfits_fn = lambda_.Function(
            self, "OutfitsFn",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="outfits.handler",
            code=lambda_.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            environment=common_env
        )

        # --- 3) Least-privilege IAM: exact DynamoDB actions only on this table ---
        table_arn = table.table_arn
        minimal_actions = [
            "dynamodb:GetItem",
            "dynamodb:Query",
            "dynamodb:BatchGetItem",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:BatchWriteItem"
        ]

        for fn in (items_fn, outfits_fn):
            fn.add_to_role_policy(iam.PolicyStatement(
                actions=minimal_actions,
                resources=[table_arn]
            ))

        # --- 4) API Gateway (separate /dev and /prod stages; CORS restricted on prod) ---
        api = apigw.RestApi(
            self, "Api",
            rest_api_name=f"OutfitPlanner-{stage}",
            endpoint_types=[apigw.EndpointType.EDGE],
            deploy_options=apigw.StageOptions(stage_name=stage),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS if not is_prod else [allowed_origin],
                allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"]
            )
        )

        # /items
        items = api.root.add_resource("items")
        items.add_method("GET",  apigw.LambdaIntegration(items_fn))
        items.add_method("POST", apigw.LambdaIntegration(items_fn))

        # /outfits and /outfits/{id}
        outfits = api.root.add_resource("outfits")
        outfits.add_method("GET",  apigw.LambdaIntegration(outfits_fn))
        outfits.add_method("POST", apigw.LambdaIntegration(outfits_fn))

        outfit_id = outfits.add_resource("{id}")
        outfit_id.add_method("GET",    apigw.LambdaIntegration(outfits_fn))
        outfit_id.add_method("PATCH",  apigw.LambdaIntegration(outfits_fn))
        outfit_id.add_method("DELETE", apigw.LambdaIntegration(outfits_fn))

        # --- 5) Clean outputs ---
        CfnOutput(self, "ApiUrl", value=api.url_for_path("/"))
        CfnOutput(self, "ItemsUrl", value=api.url_for_path("/items"))
        CfnOutput(self, "OutfitsUrl", value=api.url_for_path("/outfits"))
        CfnOutput(self, "TableName", value=table.table_name)
        CfnOutput(self, "Stage", value=stage)
        CfnOutput(self, "AllowedOrigin", value=allowed_origin)

