"""
AWS Bedrock AgentCore Deployment Configuration for PropertyPilot
Deploys the multi-agent system to AWS Bedrock AgentCore Runtime
"""

import os
import json
import boto3
from typing import Dict, Any
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from property_pilot_agents import PropertyPilotSystem
import asyncio


# Environment configuration
class Config:
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_AGENT_REGION = os.getenv("BEDROCK_AGENT_REGION", "us-east-1")
    
    # Agent Runtime Configuration
    PROPERTY_SCOUT_PORT = 8081
    MARKET_ANALYZER_PORT = 8082
    DEAL_EVALUATOR_PORT = 8083
    INVESTMENT_MANAGER_PORT = 8084
    MAIN_SERVICE_PORT = 8080


# Individual Agent Services for Bedrock Deployment
class PropertyScoutService:
    """Property Scout Agent as a Bedrock AgentCore service"""
    
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        self.property_pilot = PropertyPilotSystem()
        self.agent = self.property_pilot.property_scout
    
    @property
    def bedrock_app(self):
        @self.app.entrypoint
        def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Property Scout agent invocation endpoint"""
            try:
                user_message = payload.get("prompt", "Find investment properties")
                result = self.agent(user_message)
                
                return {
                    "agent": "PropertyScout",
                    "message": result.message,
                    "timestamp": result.timestamp.isoformat() if hasattr(result, 'timestamp') else None,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "agent": "PropertyScout", 
                    "error": str(e),
                    "status": "error"
                }
        
        return self.app


class MarketAnalyzerService:
    """Market Analyzer Agent as a Bedrock AgentCore service"""
    
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        self.property_pilot = PropertyPilotSystem()
        self.agent = self.property_pilot.market_analyzer
    
    @property
    def bedrock_app(self):
        @self.app.entrypoint
        def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Market Analyzer agent invocation endpoint"""
            try:
                user_message = payload.get("prompt", "Analyze real estate market conditions")
                result = self.agent(user_message)
                
                return {
                    "agent": "MarketAnalyzer",
                    "message": result.message,
                    "timestamp": result.timestamp.isoformat() if hasattr(result, 'timestamp') else None,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "agent": "MarketAnalyzer",
                    "error": str(e), 
                    "status": "error"
                }
        
        return self.app


class DealEvaluatorService:
    """Deal Evaluator Agent as a Bedrock AgentCore service"""
    
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        self.property_pilot = PropertyPilotSystem()
        self.agent = self.property_pilot.deal_evaluator
    
    @property
    def bedrock_app(self):
        @self.app.entrypoint
        def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Deal Evaluator agent invocation endpoint"""
            try:
                user_message = payload.get("prompt", "Evaluate investment deal metrics")
                result = self.agent(user_message)
                
                return {
                    "agent": "DealEvaluator",
                    "message": result.message,
                    "timestamp": result.timestamp.isoformat() if hasattr(result, 'timestamp') else None,
                    "status": "success"
                }
            except Exception as e:
                return {
                    "agent": "DealEvaluator",
                    "error": str(e),
                    "status": "error"
                }
        
        return self.app


class InvestmentManagerService:
    """Investment Manager Agent as a Bedrock AgentCore service"""
    
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        self.property_pilot = PropertyPilotSystem()
        self.agent = self.property_pilot.investment_manager
    
    @property
    def bedrock_app(self):
        @self.app.entrypoint
        async def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Investment Manager agent invocation endpoint with orchestration"""
            try:
                user_message = payload.get("prompt", "Coordinate investment analysis")
                
                # Check if this is a full analysis request
                if "full_analysis" in user_message.lower() or "complete_analysis" in user_message.lower():
                    # Run the complete multi-agent analysis
                    location = payload.get("location", "Austin, TX")
                    max_price = payload.get("max_price", 500000)
                    
                    analysis_result = await self.property_pilot.analyze_property_investment(
                        location=location,
                        max_price=max_price
                    )
                    
                    return {
                        "agent": "InvestmentManager",
                        "analysis_type": "full_analysis",
                        "result": analysis_result,
                        "status": "success"
                    }
                else:
                    # Regular agent invocation
                    result = self.agent(user_message)
                    return {
                        "agent": "InvestmentManager",
                        "message": result.message,
                        "timestamp": result.timestamp.isoformat() if hasattr(result, 'timestamp') else None,
                        "status": "success"
                    }
                    
            except Exception as e:
                return {
                    "agent": "InvestmentManager",
                    "error": str(e),
                    "status": "error"
                }
        
        return self.app


# Main PropertyPilot Service (Orchestrator)
class PropertyPilotMainService:
    """Main PropertyPilot service that coordinates all agents"""
    
    def __init__(self):
        self.app = BedrockAgentCoreApp()
        self.property_pilot = PropertyPilotSystem()
    
    @property
    def bedrock_app(self):
        @self.app.entrypoint
        async def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Main PropertyPilot service endpoint"""
            try:
                user_message = payload.get("prompt", "")
                agent_name = payload.get("agent", "auto")
                
                # Route to specific agent if requested
                if agent_name != "auto":
                    agent = self.property_pilot.get_agent_by_name(agent_name)
                    if agent:
                        result = agent(user_message)
                        return {
                            "service": "PropertyPilot",
                            "agent": agent_name,
                            "message": result.message,
                            "status": "success"
                        }
                
                # Run full analysis by default
                location = payload.get("location", "Austin, TX")
                max_price = payload.get("max_price", 500000)
                
                analysis_result = await self.property_pilot.analyze_property_investment(
                    location=location,
                    max_price=max_price
                )
                
                return {
                    "service": "PropertyPilot",
                    "analysis_type": "complete_investment_analysis",
                    "result": analysis_result,
                    "status": "success"
                }
                
            except Exception as e:
                return {
                    "service": "PropertyPilot",
                    "error": str(e),
                    "status": "error"
                }
        
        return self.app


# Deployment utilities
class BedrockDeploymentManager:
    """Manages deployment of PropertyPilot agents to AWS Bedrock AgentCore"""
    
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-agentcore-control', region_name=Config.AWS_REGION)
        self.runtime_client = boto3.client('bedrock-agentcore', region_name=Config.AWS_REGION)
    
    def create_agent_runtime(self, agent_name: str, container_uri: str, role_arn: str) -> Dict:
        """Create an agent runtime in Bedrock AgentCore"""
        try:
            response = self.bedrock_client.create_agent_runtime(
                agentRuntimeName=f'propertypilot-{agent_name.lower()}',
                agentRuntimeArtifact={
                    'containerConfiguration': {
                        'containerUri': container_uri
                    }
                },
                networkConfiguration={"networkMode": "PUBLIC"},
                roleArn=role_arn
            )
            
            print(f"✅ Created {agent_name} Agent Runtime")
            print(f"   ARN: {response['agentRuntimeArn']}")
            print(f"   Status: {response['status']}")
            
            return response
            
        except Exception as e:
            print(f"❌ Failed to create {agent_name} Agent Runtime: {str(e)}")
            return {}
    
    def invoke_agent(self, agent_arn: str, session_id: str, payload: Dict) -> Dict:
        """Invoke a deployed agent"""
        try:
            response = self.runtime_client.invoke_agent_runtime(
                agentRuntimeArn=agent_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(payload).encode()
            )
            
            response_body = response['response'].read()
            return json.loads(response_body)
            
        except Exception as e:
            print(f"❌ Failed to invoke agent: {str(e)}")
            return {"error": str(e)}
    
    def deploy_all_agents(self, ecr_base_uri: str, role_arn: str) -> Dict[str, str]:
        """Deploy all PropertyPilot agents to Bedrock AgentCore"""
        
        agents = {
            "PropertyScout": f"{ecr_base_uri}/property-scout:latest",
            "MarketAnalyzer": f"{ecr_base_uri}/market-analyzer:latest", 
            "DealEvaluator": f"{ecr_base_uri}/deal-evaluator:latest",
            "InvestmentManager": f"{ecr_base_uri}/investment-manager:latest",
            "PropertyPilotMain": f"{ecr_base_uri}/property-pilot-main:latest"
        }
        
        deployed_agents = {}
        
        for agent_name, container_uri in agents.items():
            response = self.create_agent_runtime(agent_name, container_uri, role_arn)
            if response:
                deployed_agents[agent_name] = response['agentRuntimeArn']
        
        return deployed_agents


# Service entry points for individual deployments
def run_property_scout():
    """Run Property Scout service"""
    service = PropertyScoutService()
    app = service.bedrock_app
    app.run(port=Config.PROPERTY_SCOUT_PORT)


def run_market_analyzer():
    """Run Market Analyzer service"""
    service = MarketAnalyzerService()
    app = service.bedrock_app
    app.run(port=Config.MARKET_ANALYZER_PORT)


def run_deal_evaluator():
    """Run Deal Evaluator service"""
    service = DealEvaluatorService()
    app = service.bedrock_app
    app.run(port=Config.DEAL_EVALUATOR_PORT)


def run_investment_manager():
    """Run Investment Manager service"""
    service = InvestmentManagerService()
    app = service.bedrock_app
    app.run(port=Config.INVESTMENT_MANAGER_PORT)


def run_main_service():
    """Run main PropertyPilot service"""
    service = PropertyPilotMainService()
    app = service.bedrock_app
    app.run(port=Config.MAIN_SERVICE_PORT)


# Example deployment script
async def example_deployment():
    """Example of how to deploy and test the system"""
    
    print("🚀 PropertyPilot Bedrock Deployment Example")
    print("=" * 50)
    
    # Initialize deployment manager
    deployment_manager = BedrockDeploymentManager()
    
    # Example deployment (replace with your actual values)
    ecr_base_uri = "123456789012.dkr.ecr.us-east-1.amazonaws.com"
    role_arn = "arn:aws:iam::123456789012:role/PropertyPilotAgentRole"
    
    print("Deploying all PropertyPilot agents...")
    deployed_agents = deployment_manager.deploy_all_agents(ecr_base_uri, role_arn)
    
    print(f"\n✅ Deployed {len(deployed_agents)} agents:")
    for agent_name, arn in deployed_agents.items():
        print(f"   {agent_name}: {arn}")
    
    # Example invocation
    if "PropertyPilotMain" in deployed_agents:
        print("\n🧪 Testing main service...")
        
        test_payload = {
            "prompt": "Analyze investment opportunities in Austin, TX",
            "location": "Austin, TX",
            "max_price": 400000
        }
        
        session_id = "propertypilot-test-session-12345678901234567890123"
        
        result = deployment_manager.invoke_agent(
            deployed_agents["PropertyPilotMain"],
            session_id,
            test_payload
        )
        
        print("Test Result:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        service = sys.argv[1]
        
        if service == "property-scout":
            run_property_scout()
        elif service == "market-analyzer":
            run_market_analyzer()
        elif service == "deal-evaluator":
            run_deal_evaluator()
        elif service == "investment-manager":
            run_investment_manager()
        elif service == "main":
            run_main_service()
        elif service == "deploy":
            asyncio.run(example_deployment())
        else:
            print("Usage: python bedrock_deployment.py [property-scout|market-analyzer|deal-evaluator|investment-manager|main|deploy]")
    else:
        # Run main service by default
        run_main_service()