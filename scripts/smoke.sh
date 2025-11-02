#!/usr/bin/env bash
set -euo pipefail
API="https://<replace-with-your-api>/prod"   # << put your real base here
echo "Version:" && curl -s $API/version
echo "Health:"  && curl -s $API/health
echo "CloudFront:" && curl -I https://d13vpwdkbkv4ik.cloudfront.net/ | head -n1
