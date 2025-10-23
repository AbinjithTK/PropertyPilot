#!/bin/bash

# PropertyPilot Multi-Agent Deployment Script for AWS Bedrock AgentCore
# This script builds and deploys all PropertyPilot agents to AWS

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_BASE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
PROJECT_NAME="propertypilot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏠 PropertyPilot Multi-Agent Deployment${NC}"
echo -e "${BLUE}======================================${NC}"
echo "AWS Region: $AWS_REGION"
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "ECR Base URI: $ECR_BASE_URI"
echo ""

# Function to create ECR repository if it doesn't exist
create_ecr_repo() {
    local repo_name=$1
    echo -e "${YELLOW}📦 Creating ECR repository: $repo_name${NC}"
    
    if aws ecr describe-repositories --repository-names "$repo_name" --region "$AWS_REGION" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Repository $repo_name already exists${NC}"
    else
        aws ecr create-repository --repository-name "$repo_name" --region "$AWS_REGION"
        echo -e "${GREEN}✅ Created repository $repo_name${NC}"
    fi
}

# Function to build and push Docker image
build_and_push() {
    local service_name=$1
    local dockerfile=$2
    local repo_name="${PROJECT_NAME}-${service_name}"
    local image_uri="${ECR_BASE_URI}/${repo_name}:latest"
    
    echo -e "${YELLOW}🔨 Building $service_name agent...${NC}"
    
    # Create ECR repository
    create_ecr_repo "$repo_name"
    
    # Build Docker image for ARM64
    docker buildx build --platform linux/arm64 -f "$dockerfile" -t "$image_uri" --load .
    
    # Login to ECR
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_BASE_URI"
    
    # Push image
    docker buildx build --platform linux/arm64 -f "$dockerfile" -t "$image_uri" --push .
    
    echo -e "${GREEN}✅ Successfully built and pushed $service_name${NC}"
    echo "   Image URI: $image_uri"
    echo ""
}

# Setup Docker buildx for ARM64
echo -e "${YELLOW}🔧 Setting up Docker buildx...${NC}"
docker buildx create --use --name propertypilot-builder 2>/dev/null || docker buildx use propertypilot-builder
echo -e "${GREEN}✅ Docker buildx ready${NC}"
echo ""

# Build and push all agent images
echo -e "${BLUE}🚀 Building and pushing agent images...${NC}"
echo ""

build_and_push "property-scout" "Dockerfile.property-scout"
build_and_push "market-analyzer" "Dockerfile.market-analyzer" 
build_and_push "deal-evaluator" "Dockerfile.deal-evaluator"
build_and_push "investment-manager" "Dockerfile.investment-manager"
build_and_push "main" "Dockerfile.main"

# Create IAM role for agents (if it doesn't exist)
echo -e "${YELLOW}🔐 Setting up IAM role...${NC}"
ROLE_NAME="PropertyPilotAgentRole"
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

# Check if role exists
if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ IAM role $ROLE_NAME already exists${NC}"
else
    # Create trust policy
    cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock-agentcore.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

    # Create the role
    aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document file://trust-policy.json
    
    # Attach necessary policies
    aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
    aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
    
    # Clean up
    rm trust-policy.json
    
    echo -e "${GREEN}✅ Created IAM role $ROLE_NAME${NC}"
fi

echo ""

# Deploy agents to Bedrock AgentCore
echo -e "${BLUE}🚀 Deploying agents to Bedrock AgentCore...${NC}"
echo ""

# Create deployment configuration
cat > deployment_config.json << EOF
{
    "aws_region": "$AWS_REGION",
    "aws_account_id": "$AWS_ACCOUNT_ID",
    "ecr_base_uri": "$ECR_BASE_URI",
    "role_arn": "$ROLE_ARN",
    "agents": {
        "property-scout": "${ECR_BASE_URI}/${PROJECT_NAME}-property-scout:latest",
        "market-analyzer": "${ECR_BASE_URI}/${PROJECT_NAME}-market-analyzer:latest",
        "deal-evaluator": "${ECR_BASE_URI}/${PROJECT_NAME}-deal-evaluator:latest",
        "investment-manager": "${ECR_BASE_URI}/${PROJECT_NAME}-investment-manager:latest",
        "main": "${ECR_BASE_URI}/${PROJECT_NAME}-main:latest"
    }
}
EOF

# Run the deployment
python3 -c "
import json
import asyncio
from bedrock_deployment import BedrockDeploymentManager

# Load configuration
with open('deployment_config.json', 'r') as f:
    config = json.load(f)

# Deploy agents
deployment_manager = BedrockDeploymentManager()
deployed_agents = deployment_manager.deploy_all_agents(
    config['ecr_base_uri'] + '/${PROJECT_NAME}',
    config['role_arn']
)

# Save deployment results
with open('deployed_agents.json', 'w') as f:
    json.dump(deployed_agents, f, indent=2)

print('✅ Deployment complete!')
print(f'Deployed {len(deployed_agents)} agents')
"

# Clean up
rm deployment_config.json

echo ""
echo -e "${GREEN}🎉 PropertyPilot Multi-Agent Deployment Complete!${NC}"
echo -e "${GREEN}=================================================${NC}"
echo ""
echo -e "${BLUE}📋 Deployment Summary:${NC}"
if [ -f "deployed_agents.json" ]; then
    echo "Deployed agents saved to: deployed_agents.json"
    cat deployed_agents.json
else
    echo "Check the deployment logs above for agent ARNs"
fi

echo ""
echo -e "${BLUE}🧪 Testing Instructions:${NC}"
echo "1. Use the AWS CLI or SDK to invoke agents:"
echo "   aws bedrock-agentcore invoke-agent-runtime --agent-runtime-arn <ARN> --runtime-session-id <SESSION_ID> --payload '{\"prompt\":\"Find properties in Austin, TX\"}'"
echo ""
echo "2. Or run the test script:"
echo "   python3 bedrock_deployment.py deploy"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "- View logs in CloudWatch"
echo "- Monitor metrics in the Bedrock AgentCore console"
echo "- Enable observability with ADOT for detailed tracing"
echo ""
echo -e "${GREEN}🚀 Your PropertyPilot agents are ready for real estate investment analysis!${NC}"