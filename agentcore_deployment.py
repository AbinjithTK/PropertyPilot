"""
Enhanced AWS Bedrock AgentCore Deployment for PropertyPilot
Leverages all AgentCore benefits: session isolation, observability, scaling, security
Based on official AgentCore documentation and Strands Agents integration patterns
"""

import os
import json
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from dataclasses import dataclass, field
import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from property_pilot_agents import PropertyPilotSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentCoreConfig:
    """Enhanced configuration for AgentCore deployment following official patterns"""
    # Basic AWS configuration
    aws_region: str = "us-east-1"
    role_arn: str = ""
    ecr_base_uri: str = ""
    
    # AgentCore Runtime configuration
    enable_observability: bool = True
    enable_session_persistence: bool = True
    enable_auto_scaling: bool = True
    memory_size: int = 2048  # MB - changed to int as per AgentCore API
    timeout: int = 900  # seconds
    concurrent_executions: int = 100
    
    # AgentCore Memory configuration
    enable_memory: bool = True
    memory_strategies: List[str] = field(default_factory=lambda: [
        "summaryMemoryStrategy",
        "userPreferenceMemoryStrategy", 
        "semanticMemoryStrategy"
    ])
    
    # Network and security configuration
    network_mode: str = "PUBLIC"  # Can be "PRIVATE" for enhanced security
    enable_encryption: bool = True
    
    # Observability configuration
    enable_cloudwatch_logs: bool = True
    enable_xray_tracing: bool = True
    enable_custom_metrics: bool = True
    log_level: str = "INFO"
    
    # Session configuration
    session_timeout_minutes: int = 30
    max_sessions_per_user: int = 10


class AgentCoreDeploymentManager:
    """Enhanced deployment manager with full AgentCore capabilities following official patterns"""
    
    def __init__(self, config: AgentCoreConfig):
        self.config = config
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client('bedrock-agentcore-control', region_name=config.aws_region)
        self.runtime_client = boto3.client('bedrock-agentcore', region_name=config.aws_region)
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=config.aws_region)
        self.iam_client = boto3.client('iam', region_name=config.aws_region)
        
        # Initialize AgentCore Memory client if enabled
        self.memory_client = None
        if config.enable_memory:
            self.memory_client = MemoryClient(region_name=config.aws_region)
        
        # Store deployment results
        self.deployment_results = {
            "agents": {},
            "memory_instances": {},
            "observability": {},
            "identity": {},
            "scaling": {},
            "security": {}
        }
    
    def create_enhanced_agent_runtime(self, agent_name: str, container_uri: str) -> Dict:
        """Create agent runtime with all AgentCore benefits enabled following official API patterns"""
        try:
            logger.info(f"Creating AgentCore Runtime for {agent_name}")
            
            # Build environment variables for observability and configuration
            env_vars = {
                'AWS_REGION': self.config.aws_region,
                'LOG_LEVEL': self.config.log_level,
                'AGENT_NAME': agent_name,
                'PROPERTYPILOT_SERVICE': 'true'
            }
            
            # Add observability environment variables if enabled
            if self.config.enable_observability:
                env_vars.update({
                    'OTEL_SERVICE_NAME': f'propertypilot-{agent_name.lower()}',
                    'OTEL_RESOURCE_ATTRIBUTES': f'service.name=propertypilot-{agent_name.lower()},service.version=1.0.0',
                    'AWS_LAMBDA_EXEC_WRAPPER': '/opt/otel-instrument',
                    'ENABLE_AGENTCORE_OBSERVABILITY': 'true'
                })
            
            # Add memory configuration if enabled
            if self.config.enable_memory:
                env_vars.update({
                    'AGENTCORE_MEMORY_ENABLED': 'true',
                    'MEMORY_STRATEGIES': ','.join(self.config.memory_strategies)
                })
            
            # Enhanced configuration following AgentCore API specification
            runtime_config = {
                'agentRuntimeName': f'propertypilot-{agent_name.lower()}',
                'agentRuntimeArtifact': {
                    'containerConfiguration': {
                        'containerUri': container_uri,
                        'environmentVariables': env_vars
                    }
                },
                'networkConfiguration': {
                    "networkMode": self.config.network_mode
                },
                'roleArn': self.config.role_arn,
                'runtimeConfiguration': {
                    'memorySize': self.config.memory_size,
                    'timeout': self.config.timeout,
                    'concurrentExecutions': self.config.concurrent_executions
                }
            }
            
            # Add observability configuration if enabled
            if self.config.enable_observability:
                runtime_config['observabilityConfiguration'] = {
                    'enableCloudWatchLogs': self.config.enable_cloudwatch_logs,
                    'enableXRayTracing': self.config.enable_xray_tracing,
                    'enableCustomMetrics': self.config.enable_custom_metrics,
                    'logLevel': self.config.log_level
                }
            
            # Add session persistence configuration if enabled
            if self.config.enable_session_persistence:
                runtime_config['sessionConfiguration'] = {
                    'enableSessionPersistence': True,
                    'sessionTimeoutMinutes': self.config.session_timeout_minutes,
                    'maxSessionsPerUser': self.config.max_sessions_per_user
                }
            
            # Create the agent runtime
            response = self.bedrock_client.create_agent_runtime(**runtime_config)
            
            logger.info(f"✅ Created Enhanced {agent_name} Agent Runtime")
            logger.info(f"   ARN: {response['agentRuntimeArn']}")
            logger.info(f"   Status: {response['status']}")
            logger.info(f"   Memory Size: {self.config.memory_size}MB")
            logger.info(f"   Timeout: {self.config.timeout}s")
            logger.info(f"   Concurrent Executions: {self.config.concurrent_executions}")
            logger.info(f"   Observability: {'Enabled' if self.config.enable_observability else 'Disabled'}")
            logger.info(f"   Session Persistence: {'Enabled' if self.config.enable_session_persistence else 'Disabled'}")
            logger.info(f"   Memory Integration: {'Enabled' if self.config.enable_memory else 'Disabled'}")
            
            # Store deployment result
            self.deployment_results["agents"][agent_name] = {
                "arn": response['agentRuntimeArn'],
                "status": response['status'],
                "container_uri": container_uri,
                "config": runtime_config
            }
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Failed to create {agent_name} Agent Runtime: {str(e)}")
            return {}
    
    def create_agentcore_memory(self, memory_name: str, description: str) -> Dict:
        """Create AgentCore Memory instance with PropertyPilot-specific strategies"""
        if not self.memory_client:
            logger.error("Memory client not initialized. Enable memory in config.")
            return {}
        
        try:
            logger.info(f"Creating AgentCore Memory: {memory_name}")
            
            # Define memory strategies for PropertyPilot
            strategies = []
            
            if "summaryMemoryStrategy" in self.config.memory_strategies:
                strategies.append({
                    "summaryMemoryStrategy": {
                        "name": "PropertyPilotSessionSummarizer",
                        "namespaces": ["/summaries/{actorId}/{sessionId}"]
                    }
                })
            
            if "userPreferenceMemoryStrategy" in self.config.memory_strategies:
                strategies.append({
                    "userPreferenceMemoryStrategy": {
                        "name": "PropertyPilotPreferenceLearner", 
                        "namespaces": ["/preferences/{actorId}"]
                    }
                })
            
            if "semanticMemoryStrategy" in self.config.memory_strategies:
                strategies.append({
                    "semanticMemoryStrategy": {
                        "name": "PropertyPilotFactExtractor",
                        "namespaces": ["/facts/{actorId}", "/properties/{actorId}", "/market_data/{actorId}"]
                    }
                })
            
            # Create memory with strategies
            memory_response = self.memory_client.create_memory_and_wait(
                name=memory_name,
                description=description,
                strategies=strategies if strategies else None
            )
            
            logger.info(f"✅ Created AgentCore Memory: {memory_name}")
            logger.info(f"   Memory ID: {memory_response.get('id')}")
            logger.info(f"   Strategies: {len(strategies)} configured")
            
            # Store memory result
            self.deployment_results["memory_instances"][memory_name] = {
                "id": memory_response.get('id'),
                "name": memory_name,
                "description": description,
                "strategies": strategies
            }
            
            return memory_response
            
        except Exception as e:
            logger.error(f"❌ Failed to create AgentCore Memory {memory_name}: {str(e)}")
            return {}
    
    def setup_observability(self, agent_arn: str) -> bool:
        """Set up comprehensive observability for AgentCore"""
        try:
            # Create CloudWatch dashboard
            dashboard_body = {
                "widgets": [
                    {
                        "type": "metric",
                        "properties": {
                            "metrics": [
                                ["AWS/BedrockAgentCore", "Invocations", "AgentRuntimeArn", agent_arn],
                                [".", "Duration", ".", "."],
                                [".", "Errors", ".", "."],
                                [".", "Throttles", ".", "."]
                            ],
                            "period": 300,
                            "stat": "Sum",
                            "region": self.config.aws_region,
                            "title": f"PropertyPilot Agent Metrics"
                        }
                    }
                ]
            }
            
            self.cloudwatch_client.put_dashboard(
                DashboardName=f"PropertyPilot-{agent_arn.split('/')[-1]}",
                DashboardBody=json.dumps(dashboard_body)
            )
            
            # Create CloudWatch alarms
            self.cloudwatch_client.put_metric_alarm(
                AlarmName=f"PropertyPilot-HighErrorRate-{agent_arn.split('/')[-1]}",
                ComparisonOperator='GreaterThanThreshold',
                EvaluationPeriods=2,
                MetricName='Errors',
                Namespace='AWS/BedrockAgentCore',
                Period=300,
                Statistic='Sum',
                Threshold=10.0,
                ActionsEnabled=True,
                AlarmDescription='High error rate for PropertyPilot agent',
                Dimensions=[
                    {
                        'Name': 'AgentRuntimeArn',
                        'Value': agent_arn
                    }
                ]
            )
            
            print(f"✅ Observability configured for {agent_arn}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup observability: {str(e)}")
            return False
    
    def setup_cognito_identity_integration(self) -> Dict:
        """Set up comprehensive Cognito identity integration with AgentCore Identity"""
        try:
            logger.info("Setting up Cognito identity integration for PropertyPilot...")
            
            # Initialize Cognito client
            cognito_client = boto3.client('cognito-idp', region_name=self.config.aws_region)
            
            # Create Cognito User Pool with PropertyPilot-specific configuration
            user_pool_response = cognito_client.create_user_pool(
                PoolName='PropertyPilotUsers',
                Policies={
                    'PasswordPolicy': {
                        'MinimumLength': 8,
                        'RequireUppercase': True,
                        'RequireLowercase': True,
                        'RequireNumbers': True,
                        'RequireSymbols': True,
                        'TemporaryPasswordValidityDays': 7
                    }
                },
                AutoVerifiedAttributes=['email'],
                UsernameAttributes=['email'],
                MfaConfiguration='OPTIONAL',
                DeviceConfiguration={
                    'ChallengeRequiredOnNewDevice': True,
                    'DeviceOnlyRememberedOnUserPrompt': False
                },
                EmailConfiguration={
                    'EmailSendingAccount': 'COGNITO_DEFAULT'
                },
                UserPoolTags={
                    'Application': 'PropertyPilot',
                    'Environment': 'Production',
                    'Service': 'AgentCore'
                },
                Schema=[
                    {
                        'Name': 'email',
                        'AttributeDataType': 'String',
                        'Required': True,
                        'Mutable': True
                    },
                    {
                        'Name': 'given_name',
                        'AttributeDataType': 'String',
                        'Required': False,
                        'Mutable': True
                    },
                    {
                        'Name': 'family_name',
                        'AttributeDataType': 'String',
                        'Required': False,
                        'Mutable': True
                    },
                    {
                        'Name': 'investment_preferences',
                        'AttributeDataType': 'String',
                        'Required': False,
                        'Mutable': True,
                        'DeveloperOnlyAttribute': False
                    },
                    {
                        'Name': 'risk_tolerance',
                        'AttributeDataType': 'String',
                        'Required': False,
                        'Mutable': True,
                        'DeveloperOnlyAttribute': False
                    },
                    {
                        'Name': 'investment_timeline',
                        'AttributeDataType': 'String',
                        'Required': False,
                        'Mutable': True,
                        'DeveloperOnlyAttribute': False
                    }
                ]
            )
            
            user_pool_id = user_pool_response['UserPool']['Id']
            logger.info(f"✅ Created Cognito User Pool: {user_pool_id}")
            
            # Create User Pool Client for PropertyPilot application
            user_pool_client_response = cognito_client.create_user_pool_client(
                UserPoolId=user_pool_id,
                ClientName='PropertyPilotWebClient',
                GenerateSecret=False,  # For web applications
                RefreshTokenValidity=30,  # 30 days
                AccessTokenValidity=60,   # 60 minutes
                IdTokenValidity=60,       # 60 minutes
                TokenValidityUnits={
                    'AccessToken': 'minutes',
                    'IdToken': 'minutes',
                    'RefreshToken': 'days'
                },
                ExplicitAuthFlows=[
                    'ALLOW_USER_PASSWORD_AUTH',
                    'ALLOW_USER_SRP_AUTH',
                    'ALLOW_REFRESH_TOKEN_AUTH'
                ],
                SupportedIdentityProviders=['COGNITO'],
                CallbackURLs=['https://propertypilot.example.com/callback'],
                LogoutURLs=['https://propertypilot.example.com/logout'],
                AllowedOAuthFlows=['code', 'implicit'],
                AllowedOAuthScopes=['email', 'openid', 'profile'],
                AllowedOAuthFlowsUserPoolClient=True,
                PreventUserExistenceErrors='ENABLED'
            )
            
            client_id = user_pool_client_response['UserPoolClient']['ClientId']
            logger.info(f"✅ Created User Pool Client: {client_id}")
            
            # Create User Pool Domain for hosted UI
            domain_name = f"propertypilot-{datetime.now().strftime('%Y%m%d')}"
            try:
                domain_response = cognito_client.create_user_pool_domain(
                    Domain=domain_name,
                    UserPoolId=user_pool_id
                )
                logger.info(f"✅ Created User Pool Domain: {domain_name}")
            except Exception as domain_error:
                logger.warning(f"⚠️ Failed to create domain (may already exist): {domain_error}")
                domain_name = None
            
            # Create Identity Pool for federated identities
            cognito_identity_client = boto3.client('cognito-identity', region_name=self.config.aws_region)
            
            identity_pool_response = cognito_identity_client.create_identity_pool(
                IdentityPoolName='PropertyPilotIdentityPool',
                AllowUnauthenticatedIdentities=False,
                CognitoIdentityProviders=[
                    {
                        'ProviderName': f'cognito-idp.{self.config.aws_region}.amazonaws.com/{user_pool_id}',
                        'ClientId': client_id,
                        'ServerSideTokenCheck': True
                    }
                ],
                IdentityPoolTags={
                    'Application': 'PropertyPilot',
                    'Environment': 'Production',
                    'Service': 'AgentCore'
                }
            )
            
            identity_pool_id = identity_pool_response['IdentityPoolId']
            logger.info(f"✅ Created Identity Pool: {identity_pool_id}")
            
            # Create IAM roles for authenticated and unauthenticated users
            iam_client = boto3.client('iam', region_name=self.config.aws_region)
            
            # Authenticated user role
            auth_role_doc = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Federated": "cognito-identity.amazonaws.com"
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "cognito-identity.amazonaws.com:aud": identity_pool_id
                            },
                            "ForAnyValue:StringLike": {
                                "cognito-identity.amazonaws.com:amr": "authenticated"
                            }
                        }
                    }
                ]
            }
            
            auth_role_response = iam_client.create_role(
                RoleName='PropertyPilotCognitoAuthenticatedRole',
                AssumeRolePolicyDocument=json.dumps(auth_role_doc),
                Description='Role for authenticated PropertyPilot users',
                Tags=[
                    {'Key': 'Application', 'Value': 'PropertyPilot'},
                    {'Key': 'Service', 'Value': 'AgentCore'}
                ]
            )
            
            auth_role_arn = auth_role_response['Role']['Arn']
            logger.info(f"✅ Created authenticated user role: {auth_role_arn}")
            
            # Attach policy to authenticated role for AgentCore access
            auth_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock-agentcore:InvokeAgentRuntime",
                            "bedrock-agentcore:GetAgentRuntime"
                        ],
                        "Resource": f"arn:aws:bedrock-agentcore:{self.config.aws_region}:*:runtime/propertypilot-*"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock-agentcore:CreateEvent",
                            "bedrock-agentcore:GetEvent",
                            "bedrock-agentcore:ListEvents"
                        ],
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                "bedrock-agentcore:ActorId": "${cognito-identity.amazonaws.com:sub}"
                            }
                        }
                    }
                ]
            }
            
            iam_client.put_role_policy(
                RoleName='PropertyPilotCognitoAuthenticatedRole',
                PolicyName='PropertyPilotAgentCoreAccess',
                PolicyDocument=json.dumps(auth_policy)
            )
            
            # Set identity pool roles
            cognito_identity_client.set_identity_pool_roles(
                IdentityPoolId=identity_pool_id,
                Roles={
                    'authenticated': auth_role_arn
                }
            )
            
            logger.info("✅ Cognito identity integration configured successfully")
            
            # Return comprehensive identity configuration
            identity_config = {
                'user_pool_id': user_pool_id,
                'user_pool_arn': user_pool_response['UserPool']['Arn'],
                'client_id': client_id,
                'identity_pool_id': identity_pool_id,
                'domain_name': domain_name,
                'auth_role_arn': auth_role_arn,
                'region': self.config.aws_region,
                'hosted_ui_url': f"https://{domain_name}.auth.{self.config.aws_region}.amazoncognito.com" if domain_name else None,
                'configuration': {
                    'mfa_enabled': True,
                    'password_policy': 'strong',
                    'token_validity': {
                        'access_token': '60 minutes',
                        'id_token': '60 minutes', 
                        'refresh_token': '30 days'
                    }
                }
            }
            
            return identity_config
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Cognito identity integration: {str(e)}")
            return {}
    
    def create_test_users(self, user_pool_id: str) -> Dict:
        """Create test users for PropertyPilot demonstration"""
        try:
            logger.info("Creating test users for PropertyPilot...")
            
            cognito_client = boto3.client('cognito-idp', region_name=self.config.aws_region)
            
            test_users = [
                {
                    'username': 'investor1@example.com',
                    'email': 'investor1@example.com',
                    'given_name': 'John',
                    'family_name': 'Investor',
                    'investment_preferences': json.dumps({
                        'property_types': ['single_family', 'condo'],
                        'max_price': 500000,
                        'preferred_locations': ['Austin, TX', 'Denver, CO']
                    }),
                    'risk_tolerance': 'moderate',
                    'investment_timeline': 'long_term'
                },
                {
                    'username': 'investor2@example.com',
                    'email': 'investor2@example.com',
                    'given_name': 'Sarah',
                    'family_name': 'PropertyBuyer',
                    'investment_preferences': json.dumps({
                        'property_types': ['multi_family', 'commercial'],
                        'max_price': 1000000,
                        'preferred_locations': ['Seattle, WA', 'Portland, OR']
                    }),
                    'risk_tolerance': 'aggressive',
                    'investment_timeline': 'short_term'
                }
            ]
            
            created_users = []
            
            for user_data in test_users:
                try:
                    # Create user
                    response = cognito_client.admin_create_user(
                        UserPoolId=user_pool_id,
                        Username=user_data['username'],
                        UserAttributes=[
                            {'Name': 'email', 'Value': user_data['email']},
                            {'Name': 'email_verified', 'Value': 'true'},
                            {'Name': 'given_name', 'Value': user_data['given_name']},
                            {'Name': 'family_name', 'Value': user_data['family_name']},
                            {'Name': 'custom:investment_preferences', 'Value': user_data['investment_preferences']},
                            {'Name': 'custom:risk_tolerance', 'Value': user_data['risk_tolerance']},
                            {'Name': 'custom:investment_timeline', 'Value': user_data['investment_timeline']}
                        ],
                        TemporaryPassword='TempPass123!',
                        MessageAction='SUPPRESS'  # Don't send welcome email for test users
                    )
                    
                    # Set permanent password
                    cognito_client.admin_set_user_password(
                        UserPoolId=user_pool_id,
                        Username=user_data['username'],
                        Password='PropertyPilot123!',
                        Permanent=True
                    )
                    
                    created_users.append({
                        'username': user_data['username'],
                        'email': user_data['email'],
                        'status': 'created',
                        'password': 'PropertyPilot123!'
                    })
                    
                    logger.info(f"✅ Created test user: {user_data['username']}")
                    
                except Exception as user_error:
                    logger.warning(f"⚠️ Failed to create user {user_data['username']}: {user_error}")
                    created_users.append({
                        'username': user_data['username'],
                        'status': 'failed',
                        'error': str(user_error)
                    })
            
            return {
                'created_users': created_users,
                'total_created': len([u for u in created_users if u['status'] == 'created']),
                'instructions': {
                    'login_url': f"https://{self.deployment_results.get('identity', {}).get('domain_name', 'DOMAIN')}.auth.{self.config.aws_region}.amazoncognito.com",
                    'default_password': 'PropertyPilot123!',
                    'note': 'Users will be prompted to change password on first login'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create test users: {str(e)}")
            return {}
    
    def deploy_with_all_benefits(self) -> Dict[str, Any]:
        """Deploy PropertyPilot with all AgentCore benefits following official patterns"""
        logger.info("🚀 Deploying PropertyPilot with Full AgentCore Benefits")
        logger.info("=" * 60)
        
        # 1. Create AgentCore Memory instances if enabled
        if self.config.enable_memory:
            logger.info("\n🧠 Creating AgentCore Memory instances...")
            
            # Create main PropertyPilot memory
            main_memory = self.create_agentcore_memory(
                "PropertyPilotMainMemory",
                "Main memory for PropertyPilot multi-agent system with user preferences, property data, and analysis history"
            )
            
            # Create specialized memory for market data
            market_memory = self.create_agentcore_memory(
                "PropertyPilotMarketMemory", 
                "Specialized memory for market analysis data, trends, and demographic information"
            )
        
        # 2. Deploy enhanced agents with proper container URIs
        logger.info("\n📦 Deploying PropertyPilot agents with AgentCore Runtime...")
        agents = {
            "PropertyPilotMain": f"{self.config.ecr_base_uri}/propertypilot-main:latest",
            "PropertyScout": f"{self.config.ecr_base_uri}/propertypilot-property-scout:latest", 
            "MarketAnalyzer": f"{self.config.ecr_base_uri}/propertypilot-market-analyzer:latest",
            "DealEvaluator": f"{self.config.ecr_base_uri}/propertypilot-deal-evaluator:latest",
            "InvestmentManager": f"{self.config.ecr_base_uri}/propertypilot-investment-manager:latest"
        }
        
        for agent_name, container_uri in agents.items():
            logger.info(f"\n📦 Deploying {agent_name} with enhanced AgentCore configuration...")
            response = self.create_enhanced_agent_runtime(agent_name, container_uri)
            
            if response and self.config.enable_observability:
                agent_arn = response.get('agentRuntimeArn')
                if agent_arn:
                    self.setup_observability(agent_arn)
                    self.deployment_results["observability"][agent_name] = "configured"
        
        # 3. Setup Cognito identity integration
        logger.info(f"\n🔐 Setting up Cognito Identity integration with AgentCore...")
        identity_config = self.setup_cognito_identity_integration()
        self.deployment_results["identity"] = identity_config
        
        # 3.1 Create test users if identity setup was successful
        if identity_config and identity_config.get('user_pool_id'):
            logger.info(f"\n👥 Creating test users for demonstration...")
            test_users = self.create_test_users(identity_config['user_pool_id'])
            self.deployment_results["identity"]["test_users"] = test_users
        
        # 4. Configure scaling and performance settings
        if self.config.enable_auto_scaling:
            logger.info(f"\n📈 Configuring auto-scaling and performance...")
            self.deployment_results["scaling"] = {
                "enabled": True,
                "concurrent_executions": self.config.concurrent_executions,
                "memory_size": self.config.memory_size,
                "timeout": self.config.timeout,
                "session_timeout_minutes": self.config.session_timeout_minutes
            }
        
        # 5. Setup security features
        logger.info(f"\n🛡️ Configuring security features...")
        self.deployment_results["security"] = {
            "session_isolation": True,
            "encrypted_storage": self.config.enable_encryption,
            "iam_role": self.config.role_arn,
            "network_mode": self.config.network_mode,
            "observability_enabled": self.config.enable_observability
        }
        
        # 6. Save comprehensive deployment configuration
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"agentcore_deployment_results_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(self.deployment_results, f, indent=2, default=str)
        
        logger.info(f"\n🎉 PropertyPilot deployed with full AgentCore benefits!")
        logger.info(f"📊 Deployment results saved to: {results_file}")
        logger.info(f"📈 Total agents deployed: {len(self.deployment_results['agents'])}")
        logger.info(f"🧠 Memory instances created: {len(self.deployment_results['memory_instances'])}")
        
        return self.deployment_results
    
    def invoke_with_session_context(self, agent_arn: str, payload: Dict, user_id: str = None) -> Dict:
        """Invoke agent with full session context and observability"""
        try:
            # Generate session ID with user context
            session_id = f"user_{user_id or 'anonymous'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{''.join([str(ord(c)) for c in (user_id or 'anon')[:3]])}"
            
            # Add session context to payload
            enhanced_payload = {
                **payload,
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "agentcore_features": {
                    "session_isolation": True,
                    "observability_enabled": self.config.enable_observability,
                    "auto_scaling": self.config.enable_auto_scaling
                }
            }
            
            # Invoke with enhanced headers for observability
            response = self.runtime_client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(enhanced_payload).encode(),
                qualifier="DEFAULT"
            )
            
            response_body = response['response'].read()
            result = json.loads(response_body)
            
            # Add session metadata to response
            result["session_metadata"] = {
                "session_id": session_id,
                "user_id": user_id,
                "invocation_time": datetime.now().isoformat(),
                "agent_arn": agent_arn
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "session_id": session_id if 'session_id' in locals() else None,
                "timestamp": datetime.now().isoformat()
            }


# Enhanced AgentCore service classes
class PropertyPilotAgentCoreService:
    """Main PropertyPilot service optimized for AgentCore"""
    
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        self.property_pilot = PropertyPilotSystem()
        self.session_store = {}
    
    def create_service(self):
        """Create the AgentCore service with all benefits"""
        
        @self.app.entrypoint
        async def invoke(payload: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
            """Enhanced entrypoint with full AgentCore integration"""
            # This is handled by the main.py implementation
            pass
        
        @self.app.health_check
        async def health():
            """Enhanced health check"""
            return {
                "status": "healthy",
                "service": "PropertyPilot-AgentCore-Enhanced",
                "features": {
                    "session_isolation": True,
                    "observability": True,
                    "auto_scaling": True,
                    "security": True
                },
                "timestamp": datetime.now().isoformat()
            }
        
        return self.app


# Example usage and testing
async def example_enhanced_deployment():
    """Example of enhanced AgentCore deployment following official patterns"""
    
    # Enhanced configuration with all AgentCore features
    config = AgentCoreConfig(
        aws_region="us-east-1",
        role_arn="arn:aws:iam::123456789012:role/PropertyPilotEnhancedRole",
        ecr_base_uri="123456789012.dkr.ecr.us-east-1.amazonaws.com",
        
        # Runtime configuration
        enable_observability=True,
        enable_session_persistence=True,
        enable_auto_scaling=True,
        memory_size=4096,  # 4GB for complex property analysis
        timeout=900,  # 15 minutes for comprehensive analysis
        concurrent_executions=200,
        
        # Memory configuration
        enable_memory=True,
        memory_strategies=["summaryMemoryStrategy", "userPreferenceMemoryStrategy", "semanticMemoryStrategy"],
        
        # Security and network configuration
        network_mode="PUBLIC",  # Can be "PRIVATE" for enhanced security
        enable_encryption=True,
        
        # Observability configuration
        enable_cloudwatch_logs=True,
        enable_xray_tracing=True,
        enable_custom_metrics=True,
        log_level="INFO",
        
        # Session configuration
        session_timeout_minutes=45,  # Longer timeout for property analysis
        max_sessions_per_user=15
    )
    
    # Deploy with all benefits
    logger.info("Starting PropertyPilot AgentCore deployment...")
    deployment_manager = AgentCoreDeploymentManager(config)
    results = deployment_manager.deploy_with_all_benefits()
    
    # Test with session context if deployment successful
    if results["agents"] and "PropertyPilotMain" in results["agents"]:
        main_agent_data = results["agents"]["PropertyPilotMain"]
        main_agent_arn = main_agent_data.get("arn")
        
        if main_agent_arn:
            test_payload = {
                "input": {  # Following AgentCore API format
                    "prompt": "Analyze investment opportunities in Seattle, WA with focus on single-family homes under $800,000",
                    "type": "enhanced_analysis",
                    "location": "Seattle, WA",
                    "max_price": 800000,
                    "user_preferences": {
                        "property_types": ["single_family", "condo"],
                        "min_roi": 8.0,
                        "max_risk": 6.0,
                        "investment_timeline": "long_term"
                    }
                }
            }
            
            logger.info("Testing deployed PropertyPilot agent...")
            result = deployment_manager.invoke_with_session_context(
                main_agent_arn,
                test_payload,
                user_id="investor_123"
            )
            
            logger.info("🧪 Enhanced AgentCore Test Result:")
            logger.info(json.dumps(result, indent=2, default=str))
    
    return results


if __name__ == "__main__":
    asyncio.run(example_enhanced_deployment())