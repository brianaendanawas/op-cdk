![](https://img.shields.io/github/actions/workflow/status/brianaendanawas/op-cdk/cdk-synth.yml?branch=main) ![](https://img.shields.io/github/license/brianaendanawas/op-cdk ) ![](https://img.shields.io/github/last-commit/brianaendanawas/op-cdk )

![](https://img.shields.io/github/actions/workflow/status/brianaendanawas/op-cdk/cdk-synth.yml?branch=main) ![](https://img.shields.io/github/license/brianaendanawas/op-cdk ) ![](https://img.shields.io/github/last-commit/brianaendanawas/op-cdk )

# 👗 Outfit Planner – AWS CDK Project

A **serverless outfit planning app** built with **AWS CDK (Python)**.  
It uses **API Gateway**, **Lambda**, and **DynamoDB** for backend logic, with **S3 + CloudFront** hosting the static web client.  
Users can create, list, and view outfit items in a responsive web interface.

🔗 **Live Demo:** [https://d13vpwdkbkv4ik.cloudfront.net](https://d13vpwdkbkv4ik.cloudfront.net)

---

## ⚡ At a Glance

Stack: API Gateway • Lambda (Python 3.12) • DynamoDB • S3 + CloudFront • CDK (Python)
What to try: Create → List → View outfits via the web client (CloudFront).
Why it’s here: Simple serverless CRUD + IaC with a dev/prod split and a short runbook.

Quick Start

1. ```bash
   cdk bootstrap
   ```
   (first time only)
2. ```bash
   cdk deploy OutfitPlanner-Dev
   ```
3. Open the CloudFront URL → paste your API base URL in config.js
4. Test Create/List in the UI

Runbook: see RUNBOOK.md (deploy, smoke tests, rollback, CloudFront cache invalidation).

---

## 60 Second Smoke Test
```bash
# API quick check
curl -s https://jauog4gfif.execute-api.us-east-1.amazonaws.com/version
curl -s https://jauog4gfif.execute-api.us-east-1.amazonaws.com/health
# CloudFront reachable?
curl -I https://d13vpwdkbkv4ik.cloudfront.net/
```

---

## 🏗️ Architecture Overview

**Frontend:**  
- Static website hosted on **Amazon S3**  
- Distributed via **CloudFront (HTTPS)**  

**Backend:**  
- **API Gateway** routes REST requests  
- **Lambda functions** handle CRUD operations  
- **DynamoDB** stores outfit data  
- **CDK (Python)** defines and deploys infrastructure  

---

## 🖼️ Screenshots

| Web App | DynamoDB Table |
|---|---|
| ![Outfit Planner Web](./app-screenshot.png) | ![DynamoDB Items](./dynamodb-items.png) |

---

## 📁 Project Structure

op-cdk/
├── app.py # CDK app entry point
├── stacks/ # CDK stack definitions (Dev/Prod)
├── lambda/ # Lambda function code
├── postman/ # API test collection
├── README.md # Project documentation
└── requirements.txt # Python dependencies

---

## 🧰 Setup Instructions

This project is set up like a standard Python CDK project.  
It uses a virtual environment (`.venv`) to manage dependencies.

### Create and activate virtual environment

**MacOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Synthesize CloudFormation template
```bash
cdk synth
```

### Deploy the stack
```bash
cdk deploy
```

---

## 🧩 Useful CDK Commands

| Command | Description |
|----------|-------------|
| `cdk ls` | List all stacks in the app |
| `cdk synth` | Emit synthesized CloudFormation template |
| `cdk deploy` | Deploy the stack to your AWS account/region |
| `cdk diff` | Compare deployed stack with current state |
| `cdk docs` | Open AWS CDK documentation |

---

## ☁️ Stacks

### OutfitPlanner-Dev
- Table: `OutfitPlanner-dev` (DESTROY on delete)
- CORS: `*`

### OutfitPlanner-Prod
- Table: `OutfitPlanner-prod` (RETAIN on delete)
- CORS: `https://d13vpwdkbkv4ik.cloudfront.net`

---

## 🔍 Useful CLI Commands

Get Prod API URL:
```bash
aws cloudformation describe-stacks --stack-name OutfitPlanner-Prod
--query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue"
--output text
```

---

## 🩺 Health Check

`GET /health` → returns:
{ "ok": true, "service": "OutfitPlanner", "stage": "prod", "table": "OutfitPlanner-prod", "time": "..." }

Prod CORS: `https://d13vpwdkbkv4ik.cloudfront.net`

---

## 🧾 Version Endpoint

`GET /version` → returns:
{ "version": "v0.6-week5", "stage": "prod", "deployedAt": "..." }

---

## 📬 Postman Collection

Import the file:
postman/OutfitPlanner.postman_collection.json

Set collection variable:
base = ApiUrl from CloudFormation outputs

---

## 🧭 Future Ideas
- Auth (Cognito) – user-specific items
- Image upload (S3 signed URLs) for item photos
- Tag-based search & filters
- Batch import/export (CSV/JSON)
- Simple CI gate: synth only on infra changes

---

## ✅ Current Version

**APP_VERSION:** `v1.0-week7`  
**Stacks deployed:** Dev + Prod  
**CloudFront URL:** [https://d13vpwdkbkv4ik.cloudfront.net](https://d13vpwdkbkv4ik.cloudfront.net)

---


### 🔍 Quick Verify
```bash
bash scripts/smoke.sh
```
