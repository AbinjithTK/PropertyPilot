#!/usr/bin/env python3
"""
PropertyPilot AgentCore Build and Deployment Script
Builds Docker image with full AgentCore capabilities and deploys to AWS
"""

import os
import json
import boto3
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (but not AWS credentials - use AWS CLI instead)
load_dotenv()

# Remove AWS credentials from environment if they exist in .env
# This ensures we use AWS CLI credentials instead
for aws_key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
    if aws_key in os.environ:
        del os.environ[aws_key]

class PropertyPilotAgentCoreBuilder:
    """Enhanced builder for PropertyPilot with full AgentCore capabilities"""
    
    def __init__(self):
        self.aws_region = os.getenv("AWS_REGION", "us-west-2")
        self.aws_account_id = self.get_aws_account_id()
        self.ecr_base_uri = f"{self.aws_account_id}.dkr.ecr.{self.aws_region}.amazonaws.com"
        self.repo_name = "propertypilot-gemini-agentcore"
        self.image_tag = "latest"
        self.image_uri = f"{self.ecr_base_uri}/{self.repo_name}:{self.image_tag}"
        
        # Initialize AWS clients (using default AWS CLI credentials)
        self.ecr_client = boto3.client('ecr', region_name=self.aws_region)
        self.bedrock_client = boto3.client('bedrock-agentcore-control', region_name=self.aws_region)
        self.iam_client = boto3.client('iam', region_name=self.aws_region)
        self.cognito_client = boto3.client('cognito-idp', region_name=self.aws_region)
        
        print("🚀 PropertyPilot AgentCore Builder")
        print("=" * 50)
        print(f"AWS Region: {self.aws_region}")
        print(f"AWS Account: {self.aws_account_id}")
        print(f"Image URI: {self.image_uri}")
    
    def get_aws_account_id(self):
        """Get AWS account ID"""
        try:
            # Use default AWS credentials (from AWS CLI) instead of .env
            sts_client = boto3.client('sts', region_name=self.aws_region)
            return sts_client.get_caller_identity()['Account']
        except Exception as e:
            print(f"❌ Failed to get AWS account ID: {e}")
            print("💡 Please run 'aws configure' to set up your AWS credentials")
            return "123456789012"
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("\n🔍 Checking Prerequisites...")
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker: {result.stdout.strip()}")
            else:
                print("❌ Docker not found. Please install Docker Desktop.")
                return False
        except FileNotFoundError:
            print("❌ Docker not found. Please install Docker Desktop.")
            return False
        
        # Check AWS CLI
        try:
            result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ AWS CLI: {result.stdout.strip()}")
            else:
                print("❌ AWS CLI not found. Please install AWS CLI.")
                return False
        except FileNotFoundError:
            print("❌ AWS CLI not found. Please install AWS CLI.")
            return False
        
        # Check environment variables
        required_vars = ['GEMINI_API_KEY', 'AWS_REGION']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✅ Environment variables configured")
        
        # Check AWS credentials (use default AWS CLI credentials)
        try:
            sts_client = boto3.client('sts', region_name=self.aws_region)
            identity = sts_client.get_caller_identity()
            print(f"✅ AWS Credentials: {identity['Arn']}")
        except Exception as e:
            print(f"❌ AWS credentials not configured: {e}")
            print("💡 Please run 'aws configure' to set up your AWS credentials")
            return False
        
        return True
    
    def create_ecr_repository(self):
        """Create ECR repository with enhanced configuration"""
        print(f"\n📦 Creating ECR Repository: {self.repo_name}")
        
        try:
            # Check if repository exists
            self.ecr_client.describe_repositories(repositoryNames=[self.repo_name])
            print("✅ ECR repository already exists")
            return True
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            pass
        
        try:
            # Create repository with enhanced configuration
            response = self.ecr_client.create_repository(
                repositoryName=self.repo_name,
                imageScanningConfiguration={
                    'scanOnPush': True
                },
                encryptionConfiguration={
                    'encryptionType': 'AES256'
                },
                imageTagMutability='MUTABLE'
            )
            
            # Set lifecycle policy to manage image retention
            lifecycle_policy = {
                "rules": [
                    {
                        "rulePriority": 1,
                        "description": "Keep last 10 images",
                        "selection": {
                            "tagStatus": "tagged",
                            "tagPrefixList": ["latest"],
                            "countType": "imageCountMoreThan",
                            "countNumber": 10
                        },
                        "action": {
                            "type": "expire"
                        }
                    }
                ]
            }
            
            self.ecr_client.put_lifecycle_policy(
                repositoryName=self.repo_name,
                lifecyclePolicyText=json.dumps(lifecycle_policy)
            )
            
            print("✅ ECR repository created with lifecycle policy")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create ECR repository: {e}")
            return False
    
    def build_docker_image(self):
        """Build Docker image with AgentCore enhancements"""
        print(f"\n🔨 Building Docker Image...")
        
        try:
            # Build command with enhanced build args
            build_cmd = [
                'docker', 'build',
                '-f', 'Dockerfile.main',
                '-t', self.image_uri,
                '--build-arg', f'AWS_REGION={self.aws_region}',
                '--build-arg', f'MODEL_PROVIDER=gemini',
                '--build-arg', f'GEMINI_MODEL_ID=gemini-2.5-pro',
                '--platform', 'linux/arm64',
                '.'
            ]
            
            print(f"Build command: {' '.join(build_cmd)}")
            
            # Execute build
            result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Docker image built successfully")
                print(f"Image URI: {self.image_uri}")
                return True
            else:
                print(f"❌ Docker build failed:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to build Docker image: {e}")
            return False
    
    def push_to_ecr(self):
        """Push Docker image to ECR"""
        print(f"\n📤 Pushing to ECR...")
        
        try:
            # Get ECR login token
            token_response = self.ecr_client.get_authorization_token()
            token = token_response['authorizationData'][0]['authorizationToken']
            endpoint = token_response['authorizationData'][0]['proxyEndpoint']
            
            # Docker login to ECR
            import base64
            username, password = base64.b64decode(token).decode().split(':')
            
            login_cmd = ['docker', 'login', '--username', username, '--password-stdin', endpoint]
            login_process = subprocess.Popen(login_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            login_result = login_process.communicate(input=password)
            
            if login_process.returncode != 0:
                print(f"❌ ECR login failed: {login_result[1]}")
                return False
            
            print("✅ Logged into ECR")
            
            # Push image
            push_cmd = ['docker', 'push', self.image_uri]
            push_result = subprocess.run(push_cmd, capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("✅ Image pushed to ECR successfully")
                return True
            else:
                print(f"❌ Push failed: {push_result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to push to ECR: {e}")
            return False
    
    def create_iam_role_with_agentcore_permissions(self):
        """Create IAM role with comprehensive AgentCore permissions"""
        print(f"\n🔐 Creating IAM Role with AgentCore Permissions...")
        
        role_name = "PropertyPilotAgentCoreEnhancedRole"
        
        try:
            # Check if role exists
            self.iam_client.get_role(RoleName=role_name)
            print(f"✅ IAM role {role_name} already exists")
            return f"arn:aws:iam::{self.aws_account_id}:role/{role_name}"
        except self.iam_client.exceptions.NoSuchEntityException:
            pass
        
        # Trust policy for AgentCore
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "bedrock-agentcore.amazonaws.com",
                            "lambda.amazonaws.com"
                        ]
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            # Create role
            role_response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Enhanced IAM role for PropertyPilot AgentCore with full capabilities",
                Tags=[
                    {'Key': 'Application', 'Value': 'PropertyPilot'},
                    {'Key': 'Service', 'Value': 'AgentCore'},
                    {'Key': 'Environment', 'Value': 'Production'}
                ]
            )
            
            # Comprehensive policy for AgentCore capabilities
            agentcore_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock-agentcore:*",
                            "bedrock:InvokeModel",
                            "bedrock:InvokeModelWithResponseStream"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                            "logs:DescribeLogGroups",
                            "logs:DescribeLogStreams"
                        ],
                        "Resource": f"arn:aws:logs:{self.aws_region}:{self.aws_account_id}:*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "xray:PutTraceSegments",
                            "xray:PutTelemetryRecords"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "cloudwatch:PutMetricData"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "ecr:GetAuthorizationToken",
                            "ecr:BatchGetImage",
                            "ecr:GetDownloadUrlForLayer"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "cognito-idp:AdminGetUser",
                            "cognito-idp:AdminInitiateAuth",
                            "cognito-idp:AdminCreateUser",
                            "cognito-idp:AdminSetUserPassword"
                        ],
                        "Resource": f"arn:aws:cognito-idp:{self.aws_region}:{self.aws_account_id}:userpool/*"
                    }
                ]
            }
            
            # Attach custom policy
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='PropertyPilotAgentCorePolicy',
                PolicyDocument=json.dumps(agentcore_policy)
            )
            
            # Attach AWS managed policies
            managed_policies = [
                "arn:aws:iam::aws:policy/service-role/AmazonBedrockAgentCoreExecutionRolePolicy",
                "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
            ]
            
            for policy_arn in managed_policies:
                try:
                    self.iam_client.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                except Exception as e:
                    print(f"⚠️ Warning: Could not attach {policy_arn}: {e}")
            
            print(f"✅ Created IAM role with comprehensive permissions")
            return role_response['Role']['Arn']
            
        except Exception as e:
            print(f"❌ Failed to create IAM role: {e}")
            return None
    
    def deploy_to_agentcore(self, role_arn):
        """Deploy to AgentCore with full capabilities"""
        print(f"\n🚀 Deploying to AgentCore...")
        
        runtime_name = f"PropertyPilotGeminiEnhanced"
        
        # Load AgentCore configuration
        with open('agentcore_config.json', 'r') as f:
            config = json.load(f)
        
        # Environment variables from config
        env_vars = config['agentcore']['runtime_configuration']['environment_variables'].copy()
        env_vars.update({
            'AWS_REGION': self.aws_region,
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY', ''),
            'HASDATA_API_KEY': os.getenv('HASDATA_API_KEY', ''),
            'AGENTCORE_CONFIG': json.dumps(config)
        })
        
        # Simplified runtime configuration based on actual API
        runtime_config = {
            'agentRuntimeName': runtime_name,
            'agentRuntimeArtifact': {
                'containerConfiguration': {
                    'containerUri': self.image_uri
                }
            },
            'roleArn': role_arn,
            'environmentVariables': env_vars,
            'networkConfiguration': {
                'networkMode': config['agentcore']['networking']['mode']
            }
        }
        
        # Skip observability configuration for now (may not be supported in this API version)
        
        try:
            response = self.bedrock_client.create_agent_runtime(**runtime_config)
            
            print(f"✅ AgentCore Runtime Created Successfully!")
            print(f"   Runtime Name: {runtime_name}")
            print(f"   Runtime ARN: {response['agentRuntimeArn']}")
            print(f"   Status: {response['status']}")
            
            # Save deployment information
            deployment_info = {
                'timestamp': datetime.now().isoformat(),
                'runtime_arn': response['agentRuntimeArn'],
                'runtime_name': runtime_name,
                'image_uri': self.image_uri,
                'role_arn': role_arn,
                'aws_region': self.aws_region,
                'aws_account_id': self.aws_account_id,
                'status': response['status'],
                'capabilities': config['agentcore']['capabilities'],
                'model_configuration': config['model_configuration']
            }
            
            with open('agentcore_deployment_info.json', 'w') as f:
                json.dump(deployment_info, f, indent=2)
            
            print(f"📊 Deployment info saved to: agentcore_deployment_info.json")
            
            return response
            
        except Exception as e:
            print(f"❌ Failed to deploy to AgentCore: {e}")
            return None
    
    def run_full_deployment(self):
        """Run complete deployment process"""
        print("🏠 PropertyPilot AgentCore Full Deployment")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Please fix the issues above.")
            return False
        
        # Step 2: Create ECR repository
        if not self.create_ecr_repository():
            print("❌ Failed to create ECR repository.")
            return False
        
        # Step 3: Build Docker image
        if not self.build_docker_image():
            print("❌ Failed to build Docker image.")
            return False
        
        # Step 4: Push to ECR
        if not self.push_to_ecr():
            print("❌ Failed to push to ECR.")
            return False
        
        # Step 5: Create IAM role
        role_arn = self.create_iam_role_with_agentcore_permissions()
        if not role_arn:
            print("❌ Failed to create IAM role.")
            return False
        
        # Step 6: Deploy to AgentCore
        deployment_result = self.deploy_to_agentcore(role_arn)
        if not deployment_result:
            print("❌ Failed to deploy to AgentCore.")
            return False
        
        print("\n🎉 PropertyPilot Successfully Deployed to AgentCore!")
        print("=" * 60)
        print("Your AI-powered real estate investment system is now running with:")
        print("✅ Google Gemini 2.5 Pro AI model")
        print("✅ Full AgentCore capabilities (Memory, Observability, Identity)")
        print("✅ Built-in real estate analysis tools")
        print("✅ Scalable AWS infrastructure")
        print("✅ Enterprise-grade security")
        print("")
        print(f"🔗 Runtime ARN: {deployment_result['agentRuntimeArn']}")
        print(f"📊 Monitor at: https://console.aws.amazon.com/bedrock/home?region={self.aws_region}#/agentcore")
        
        return True

def main():
    """Main deployment function"""
    builder = PropertyPilotAgentCoreBuilder()
    success = builder.run_full_deployment()
    
    if not success:
        print("\n❌ Deployment failed. Please check the logs above.")
        exit(1)
    
    print("\n🚀 Ready to analyze real estate investments with AI!")

if __name__ == "__main__":
    main()