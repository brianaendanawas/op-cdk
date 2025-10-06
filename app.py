#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from op_cdk.op_cdk_stack import OutfitPlannerStack

app = App()

env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1")
)

OutfitPlannerStack(app, "OutfitPlanner-Dev", stage="dev", env=env)
OutfitPlannerStack(app, "OutfitPlanner-Prod", stage="prod", env=env)

app.synth()

