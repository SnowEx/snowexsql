#!/bin/bash

# Test script for the deployed Lambda function
# This script tests the basic functionality of the deployed Lambda
# Supports both direct Lambda invocation (requires AWS creds) and Function URL (public)

set -e

AWS_REGION="us-west-2"
LAMBDA_FUNCTION_NAME="lambda-snowex-sql"
FUNCTION_URL="https://izwsawyfkxss5vawq5v64mruqy0ahxek.lambda-url.us-west-2.on.aws"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Testing Lambda function: ${LAMBDA_FUNCTION_NAME}${NC}"

# Determine test method
if [ "$1" = "--function-url" ] || [ "$1" = "-u" ]; then
    TEST_METHOD="function-url"
    echo -e "${YELLOW}Using Function URL (public access - no AWS credentials required)${NC}"
else
    TEST_METHOD="boto3"
    echo -e "${YELLOW}Using boto3 invocation (requires AWS credentials)${NC}"
    echo -e "${YELLOW}Tip: Use --function-url flag to test public Function URL instead${NC}"
fi

# Test 1: Basic connectivity test
echo -e "${YELLOW}Test 1: Basic database connectivity...${NC}"

if [ "$TEST_METHOD" = "function-url" ]; then
    # Test via Function URL
    echo -e "${YELLOW}Testing via HTTP POST to: ${FUNCTION_URL}${NC}"
    HTTP_STATUS=$(curl -s -o test_response.json -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d '{"action":"test_connection"}' \
        "${FUNCTION_URL}")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "${GREEN}✓ Function URL request successful (HTTP ${HTTP_STATUS})${NC}"
    else
        echo -e "${RED}✗ Function URL request failed (HTTP ${HTTP_STATUS})${NC}"
        cat test_response.json
        exit 1
    fi
else
    # Test via AWS CLI (boto3)
    aws lambda invoke \
        --region ${AWS_REGION} \
        --function-name ${LAMBDA_FUNCTION_NAME} \
        --cli-binary-format raw-in-base64-out \
        --payload '{"action":"test_connection"}' \
        test_response.json

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Lambda invocation successful${NC}"
    else
        echo -e "${RED}✗ Lambda invocation failed${NC}"
        exit 1
    fi
fi

# Display response
echo -e "${YELLOW}Response:${NC}"

# Display response
echo -e "${YELLOW}Response:${NC}"
if command -v jq >/dev/null 2>&1; then
    # For boto3 invocation, parse nested body; for Function URL, show direct response
    if [ "$TEST_METHOD" = "boto3" ]; then
        echo -e "${YELLOW}Full invoke response:${NC}"
        jq . test_response.json
        echo -e "${YELLOW}Decoded body:${NC}"
        jq -r '.body' test_response.json | jq . 2>/dev/null || jq -r '.body' test_response.json
    else
        echo -e "${YELLOW}Function URL response:${NC}"
        jq . test_response.json
    fi
else
    echo -e "${YELLOW}jq not found; using Python to pretty-print JSON${NC}"
    if command -v python3 >/dev/null 2>&1; then
        if [ "$TEST_METHOD" = "boto3" ]; then
            echo -e "${YELLOW}Full invoke response:${NC}"
            python3 -m json.tool < test_response.json || cat test_response.json
            echo -e "${YELLOW}Decoded body:${NC}"
            python3 - << 'PY'
import json
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
except Exception:
    print(open('test_response.json','r').read())
PY
        else
            python3 -m json.tool < test_response.json || cat test_response.json
        fi
    else
        cat test_response.json
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ All tests passed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Usage tips:${NC}"
echo -e "  • Test with Function URL (public):  ./test_lambda.sh --function-url"
echo -e "  • Test with boto3 (requires creds): ./test_lambda.sh"
echo ""

# Cleanup
rm -f test_response.json

# Cleanup
rm -f test_response.json

echo -e "${GREEN}Testing completed!${NC}"