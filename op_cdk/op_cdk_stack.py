from constructs import Construct
from aws_cdk import (
    Stack, CfnOutput, RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
)

class OutfitPlannerStack(Stack):
    def __init__(self, scope: Construct, id: str, *, stage: str = "dev", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1) DynamoDB (pay-per-request; separate table per stage)
        table = dynamodb.Table(
            self, "Table",
            table_name=f"OutfitPlanner-{stage}",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY  # learning/dev; use RETAIN for real prod
        )

        # 2) Lambdas (update handler names if yours differ)
        items_fn = lambda_.Function(
            self, "ItemsFn",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="items.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": table.table_name,
                "ALLOWED_ORIGIN": "*"
            }
        )
        outfits_fn = lambda_.Function(
            self, "OutfitsFn",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="outfits.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": table.table_name,
                "ALLOWED_ORIGIN": "*"
            }
        )

        table.grant_read_write_data(items_fn)
        table.grant_read_write_data(outfits_fn)

        # 3) API Gateway (stage-aware)
        api = apigw.RestApi(
            self, "Api",
            rest_api_name=f"OutfitPlanner-{stage}",
            endpoint_types=[apigw.EndpointType.EDGE],
            deploy_options=apigw.StageOptions(stage_name=stage),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
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

        # 4) Outputs
        CfnOutput(self, "ApiUrl", value=api.url_for_path("/"))
        CfnOutput(self, "Stage", value=stage)
        CfnOutput(self, "TableName", value=table.table_name)
