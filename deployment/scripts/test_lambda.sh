#!/bin/bash

# Test script for the deployed Lambda function
# This script tests the basic functionality of the deployed Lambda

set -e

AWS_REGION="us-west-2"
LAMBDA_FUNCTION_NAME="lambda-snowex-sql"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Lambda function: ${LAMBDA_FUNCTION_NAME}${NC}"

# Test 1: Basic connectivity test
echo -e "${YELLOW}Test 1: Basic database connectivity...${NC}"
aws lambda invoke \
    --region ${AWS_REGION} \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --cli-binary-format raw-in-base64-out \
    --payload '{"action":"test_connection"}' \
    test_response.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Lambda invocation successful${NC}"
    echo -e "${YELLOW}Response:${NC}"
    if command -v jq >/dev/null 2>&1; then
        # Show full response and decoded body
        echo -e "${YELLOW}Full invoke response:${NC}"
        jq . test_response.json
        echo -e "${YELLOW}Decoded body:${NC}"
        jq -r '.body' test_response.json | jq . 2>/dev/null || jq -r '.body' test_response.json
    else
        echo -e "${YELLOW}jq not found; using Python to pretty-print JSON${NC}"
        if command -v python3 >/dev/null 2>&1; then
            echo -e "${YELLOW}Full invoke response:${NC}"
            python3 -m json.tool < test_response.json || cat test_response.json
            echo -e "${YELLOW}Decoded body:${NC}"
            python3 - "$AWS_REGION" << 'PY'
import json,sys
try:
    data=json.load(open('test_response.json','r'))
    body=data.get('body')
    if isinstance(body,str):
        try:
            print(json.dumps(json.loads(body), indent=2))
        except Exception:
            print(body)
    else:
        print(json.dumps(body, indent=2))
except Exception as e:
    print(open('test_response.json','r').read())
PY
        else
            cat test_response.json
        fi
    fi
else
    echo -e "${RED}✗ Lambda invocation failed${NC}"
    exit 1
fi

#############################################
# Test 2: Check logs (best-effort)
#############################################
echo -e "${YELLOW}Test 2: Checking recent logs...${NC}"
LOG_GROUP=$(aws logs describe-log-groups \
    --region ${AWS_REGION} \
    --log-group-name-prefix "/aws/lambda/${LAMBDA_FUNCTION_NAME}" \
    --query 'logGroups[0].logGroupName' \
    --output text 2>/dev/null || echo "")

if [ -z "$LOG_GROUP" ] || [ "$LOG_GROUP" = "None" ]; then
    echo -e "${YELLOW}No log group found yet for ${LAMBDA_FUNCTION_NAME}. Skipping log fetch.${NC}"
else
    LOG_STREAM=$(aws logs describe-log-streams \
        --region ${AWS_REGION} \
        --log-group-name "$LOG_GROUP" \
        --order-by LastEventTime \
        --descending \
        --max-items 1 \
        --query 'logStreams[0].logStreamName' \
        --output text 2>/dev/null || echo "")

    if [ -z "$LOG_STREAM" ] || [ "$LOG_STREAM" = "None" ]; then
        echo -e "${YELLOW}No recent log stream found. It can take a few seconds for logs to appear.${NC}"
    else
        aws logs get-log-events \
            --region ${AWS_REGION} \
            --log-group-name "$LOG_GROUP" \
            --log-stream-name "$LOG_STREAM" \
            --limit 10 \
            --query 'events[*].message' \
            --output text || true
    fi
fi

# Cleanup
rm -f test_response.json

echo -e "${GREEN}Testing completed!${NC}"