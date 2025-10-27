# 👗 Outfit Planner – AWS CDK Project

A serverless outfit planning app built with AWS CDK (Python).  
It uses **API Gateway**, **Lambda**, and **DynamoDB** for backend logic, with **S3 + CloudFront** hosting the static web client.  
Users can create, list, and view outfit items in a responsive web interface.

🔗 **Live Demo:** [https://d13vpwdkbkv4ik.cloudfront.net](https://d13vpwdkbkv4ik.cloudfront.net)








This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

## Stacks
- OutfitPlanner-Dev
  - Table: OutfitPlanner-dev (DESTROY on delete)
  - CORS: *
- OutfitPlanner-Prod
  - Table: OutfitPlanner-prod (RETAIN on delete)
  - CORS: https://<your-cloudfront-domain>

### Useful
- Get Prod URL:
  aws cloudformation describe-stacks --stack-name OutfitPlanner-Prod \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text

## Health Check
- `GET /health` → `{ ok, service, stage, table, time }`
- Prod CORS: https://d13vpwdkbkv4ik.cloudfront.net

## Version
- `GET /version` → `{ version, stage, deployedAt }`
- Current APP_VERSION: `v0.6-week5`

## Postman
- Import `postman/OutfitPlanner.postman_collection.json`
- Set collection var `base = <ApiUrl from CloudFormation outputs>`


