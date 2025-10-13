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
    --payload '{"test": "connectivity"}' \
    test_response.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Lambda invocation successful${NC}"
    echo -e "${YELLOW}Response:${NC}"
    cat test_response.json | jq .
else
    echo -e "${RED}✗ Lambda invocation failed${NC}"
    exit 1
fi

# Test 2: Check logs
echo -e "${YELLOW}Test 2: Checking recent logs...${NC}"
aws logs describe-log-groups \
    --region ${AWS_REGION} \
    --log-group-name-prefix "/aws/lambda/${LAMBDA_FUNCTION_NAME}" \
    --query 'logGroups[0].logGroupName' \
    --output text | xargs -I {} aws logs describe-log-streams \
    --region ${AWS_REGION} \
    --log-group-name {} \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --query 'logStreams[0].logStreamName' \
    --output text | xargs -I {} aws logs get-log-events \
    --region ${AWS_REGION} \
    --log-group-name "/aws/lambda/${LAMBDA_FUNCTION_NAME}" \
    --log-stream-name {} \
    --limit 10 \
    --query 'events[*].message' \
    --output text

# Cleanup
rm -f test_response.json

echo -e "${GREEN}Testing completed!${NC}"