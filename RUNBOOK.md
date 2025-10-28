# Outfit Planner – Runbook / Deployment Notes

## 0) Prerequisites
- AWS account with Admin or CDK deploy permissions
- AWS CLI configured (`aws configure`)
- Node.js + Python3
- CDK installed: `npm i -g aws-cdk`

## 1) One-time: CDK bootstrap (per account/region)
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>

## 2) Install deps
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt

## 3) Deploy Dev
cdk deploy OutfitPlanner-Dev

Get Dev API URL
DEV_API=$(aws cloudformation describe-stacks --stack-name OutfitPlanner-Dev \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
echo $DEV_API

Smoke test
curl -sS "${DEV_API}health" | jq .
curl -sS "${DEV_API}items"  | jq .

Create a sample item
curl -sS -X POST "${DEV_API}items" -H "Content-Type: application/json" \
  -d '{"name":"Black Hoodie","type":"top","color":"black","tags":["casual"]}' | jq .

## 4) Promote to Prod
cdk deploy OutfitPlanner-Prod

Get Prod API URL
PROD_API=$(aws cloudformation describe-stacks --stack-name OutfitPlanner-Prod \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
echo $PROD_API

Prod health check
curl -sS "${PROD_API}health" | jq .

































































cdk deploy OutfitPlanner-Prod

Get Prod API URL
PROD_API=$(aws cloudformation describe-stacks --stack-name OutfitPlanner-Prod \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)
echo $PROD_API







Prod health check
curl -sS "${PROD_API}health" | jq .

## 5) Frontend (S3 + CloudFront)
CF_DOMAIN="d13vpwdkbkv4ik.cloudfront.net"
CF_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?DomainName=='${CF_DOMAIN}'].Id | [0]" \
  --output text)
echo $CF_ID

aws cloudfront create-invalidation --distribution-id "$CF_ID" --paths "/*"

## 6) Rollback / Teardown
cdk destroy OutfitPlanner-Dev

## 7) Notes
- Dev table → DESTROY on delete; Prod table → RETAIN
- CORS → Dev = *; Prod = https://d13vpwdkbkv4ik.cloudfront.net

