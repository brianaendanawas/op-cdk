from aws_cdk import (
    Stack, Duration, CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

class OutfitPlannerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, stage: str="dev", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.Table(
            self, f"Table-{stage}",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        items_fn = _lambda.Function(
            self, f"ItemsFn-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="items.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            environment={"TABLE_NAME": table.table_name, "STAGE": stage}
        )
        outfits_fn = _lambda.Function(
            self, f"OutfitsFn-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="outfits.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            environment={"TABLE_NAME": table.table_name, "STAGE": stage}
        )

        table.grant_read_write_data(items_fn)
        table.grant_read_write_data(outfits_fn)

        api = apigw.RestApi(
            self, f"Api-{stage}",
            rest_api_name=f"OutfitPlanner-{stage}",
            deploy_options=apigw.StageOptions(stage_name=stage),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"],
                allow_headers=apigw.Cors.DEFAULT_HEADERS
            )
        )

        items = api.root.add_resource("items")
        items.add_method("GET", apigw.LambdaIntegration(items_fn))
        items.add_method("POST", apigw.LambdaIntegration(items_fn))

        outfits = api.root.add_resource("outfits")
        outfits.add_method("GET", apigw.LambdaIntegration(outfits_fn))
        outfits.add_method("POST", apigw.LambdaIntegration(outfits_fn))

        outfits_id = outfits.add_resource("{id}")
        outfits_id.add_method("GET", apigw.LambdaIntegration(outfits_fn))
        outfits_id.add_method("DELETE", apigw.LambdaIntegration(outfits_fn))
        outfits_id.add_method("PATCH", apigw.LambdaIntegration(outfits_fn))

        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "TableName", value=table.table_name)

