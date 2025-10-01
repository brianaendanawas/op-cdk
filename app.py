#!/usr/bin/env python3
import os
import aws_cdk as cdk
from src.op_stack import OutfitPlannerStack

app = cdk.App()

region  = os.getenv("CDK_DEFAULT_REGION")
account = os.getenv("CDK_DEFAULT_ACCOUNT")

# Dev stack
OutfitPlannerStack(app, "OutfitPlanner-Dev",
    env=cdk.Environment(account=account, region=region),
    stage="dev"
)

app.synth()

