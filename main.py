"""
PropertyPilot AgentCore Main Service
AWS Bedrock AgentCore deployment with full observability and session management
Following official AgentCore patterns and Strands Agents integration
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import uuid
import jwt
import base64

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from nova_act import NovaAct
from dotenv import load_dotenv
from property_pilot_agents import PropertyPilotSystem
from automated_web_research import EnhancedWebResearchAgent, AutomatedWebResearcher
from opentelemetry import baggage, context
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize AgentCore app with observability
app = BedrockAgentCoreApp()

# Initialize PropertyPilot system with Gemini
logger.info("Initializing PropertyPilot with Google Gemini 2.5 Pro...")
property_pilot = PropertyPilotSystem()
logger.info("PropertyPilot system initialized successfully")

# Initialize Enhanced Web Research Agent
web_research_agent = EnhancedWebResearchAgent()

# Initialize AgentCore Memory client
memory_client = None
if os.getenv("AGENTCORE_MEMORY_ENABLED", "false").lower() == "true":
    try:
        memory_client = MemoryClient(region_name=os.getenv("AWS_REGION", "us-east-1"))
        logger.info("AgentCore Memory client initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize AgentCore Memory client: {e}")

# Request/Response models following AgentCore patterns
class PropertyPilotRequest(BaseModel):
    input: Dict[str, Any]

class PropertyPilotResponse(BaseModel):
    output: Dict[str, Any]

# Cognito Authentication Helper
class CognitoAuthHelper:
    """Helper class for Cognito authentication and user management"""
    
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        self.client_id = os.getenv("COGNITO_CLIENT_ID")
        
    def extract_user_from_token(self, auth_token: str) -> Optional[Dict]:
        """Extract user information from Cognito JWT token"""
        try:
            if not auth_token:
                return None
            
            # Remove 'Bearer ' prefix if present
            if auth_token.startswith('Bearer '):
                auth_token = auth_token[7:]
            
            # Decode JWT token (without verification for now - in production, verify signature)
            decoded_token = jwt.decode(auth_token, options={"verify_signature": False})
            
            return {
                'user_id': decoded_token.get('sub'),
                'username': decoded_token.get('cognito:username'),
                'email': decoded_token.get('email'),
                'given_name': decoded_token.get('given_name'),
                'family_name': decoded_token.get('family_name'),
                'investment_preferences': decoded_token.get('custom:investment_preferences'),
                'risk_tolerance': decoded_token.get('custom:risk_tolerance'),
                'investment_timeline': decoded_token.get('custom:investment_timeline'),
                'token_use': decoded_token.get('token_use'),
                'exp': decoded_token.get('exp')
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract user from token: {e}")
            return None
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences from Cognito user attributes"""
        try:
            if not self.user_pool_id:
                return {}
            
            response = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=user_id
            )
            
            preferences = {}
            for attr in response.get('UserAttributes', []):
                name = attr['Name']
                value = attr['Value']
                
                if name == 'custom:investment_preferences':
                    try:
                        preferences['investment_preferences'] = json.loads(value)
                    except:
                        preferences['investment_preferences'] = value
                elif name == 'custom:risk_tolerance':
                    preferences['risk_tolerance'] = value
                elif name == 'custom:investment_timeline':
                    preferences['investment_timeline'] = value
                elif name in ['email', 'given_name', 'family_name']:
                    preferences[name] = value
            
            return preferences
            
        except Exception as e:
            logger.warning(f"Failed to get user preferences for {user_id}: {e}")
            return {}
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with Cognito and return tokens"""
        try:
            if not self.client_id:
                logger.error("Cognito client ID not configured")
                return None
            
            response = self.cognito_client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            auth_result = response.get('AuthenticationResult', {})
            
            return {
                'access_token': auth_result.get('AccessToken'),
                'id_token': auth_result.get('IdToken'),
                'refresh_token': auth_result.get('RefreshToken'),
                'expires_in': auth_result.get('ExpiresIn'),
                'token_type': auth_result.get('TokenType', 'Bearer')
            }
            
        except ClientError as e:
            logger.error(f"Cognito authentication failed: {e}")
            return None

# Initialize Cognito helper
cognito_helper = CognitoAuthHelper()

# Enhanced Session management for AgentCore with Memory integration
class PropertyPilotSessionManager:
    """Enhanced session manager with AgentCore Memory integration"""
    
    def __init__(self):
        self.sessions = {}
        self.memory_managers = {}
    
    def get_session(self, session_id: str) -> Dict:
        """Get or create session data"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "properties_analyzed": [],
                "user_preferences": {},
                "analysis_history": [],
                "memory_enabled": False
            }
        return self.sessions[session_id]
    
    def update_session(self, session_id: str, data: Dict):
        """Update session with new data"""
        session = self.get_session(session_id)
        session.update(data)
        session["last_updated"] = datetime.now().isoformat()
    
    def get_memory_manager(self, session_id: str, user_id: str = None) -> Optional[AgentCoreMemorySessionManager]:
        """Get or create AgentCore Memory session manager"""
        if not memory_client:
            return None
        
        memory_key = f"{session_id}_{user_id or 'anonymous'}"
        
        if memory_key not in self.memory_managers:
            try:
                # Get memory ID from environment or use default
                memory_id = os.getenv("PROPERTYPILOT_MEMORY_ID")
                if not memory_id:
                    logger.warning("No PROPERTYPILOT_MEMORY_ID found, memory features disabled")
                    return None
                
                # Configure memory with PropertyPilot-specific retrieval settings
                config = AgentCoreMemoryConfig(
                    memory_id=memory_id,
                    session_id=session_id,
                    actor_id=user_id or f"user_{session_id}",
                    retrieval_config={
                        "/preferences/{actorId}": RetrievalConfig(
                            top_k=5,
                            relevance_score=0.7
                        ),
                        "/facts/{actorId}": RetrievalConfig(
                            top_k=10,
                            relevance_score=0.3
                        ),
                        "/properties/{actorId}": RetrievalConfig(
                            top_k=8,
                            relevance_score=0.5
                        ),
                        "/market_data/{actorId}": RetrievalConfig(
                            top_k=6,
                            relevance_score=0.4
                        ),
                        "/summaries/{actorId}/{sessionId}": RetrievalConfig(
                            top_k=3,
                            relevance_score=0.6
                        )
                    }
                )
                
                self.memory_managers[memory_key] = AgentCoreMemorySessionManager(
                    agentcore_memory_config=config,
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                
                logger.info(f"Created AgentCore Memory session manager for {memory_key}")
                
            except Exception as e:
                logger.error(f"Failed to create memory session manager: {e}")
                return None
        
        return self.memory_managers.get(memory_key)

session_manager = PropertyPilotSessionManager()

@app.entrypoint
async def invoke(payload: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main AgentCore entrypoint for PropertyPilot following official patterns
    Leverages AgentCore session isolation, observability, memory, and Cognito authentication
    """
    try:
        # Extract input following AgentCore API format
        input_data = payload.get("input", payload)  # Support both formats
        
        # Extract authentication information
        auth_token = input_data.get('auth_token') or input_data.get('authorization')
        user_info = None
        user_preferences = {}
        
        # Authenticate user with Cognito if token provided
        if auth_token:
            user_info = cognito_helper.extract_user_from_token(auth_token)
            if user_info:
                logger.info(f"Authenticated user: {user_info.get('username', 'unknown')}")
                # Get additional user preferences from Cognito
                user_preferences = cognito_helper.get_user_preferences(user_info['user_id'])
            else:
                logger.warning("Invalid or expired authentication token")
        
        # Extract session information from AgentCore context or generate
        session_id = None
        user_id = None
        
        if context and hasattr(context, 'session_id'):
            session_id = context.session_id
        elif input_data.get('session_id'):
            session_id = input_data.get('session_id')
        else:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Extract user ID for memory personalization (prefer authenticated user)
        if user_info:
            user_id = user_info['user_id']
        else:
            user_id = input_data.get('user_id') or input_data.get('actor_id')
        
        # Set session ID and user info in OTEL baggage for distributed tracing
        ctx = baggage.set_baggage("session.id", session_id)
        if user_id:
            ctx = baggage.set_baggage("user.id", user_id, ctx)
        if user_info:
            ctx = baggage.set_baggage("user.authenticated", "true", ctx)
            ctx = baggage.set_baggage("user.email", user_info.get('email', ''), ctx)
        context.attach(ctx)
        
        logger.info(f"Processing PropertyPilot request - Session: {session_id}, User: {user_id or 'anonymous'}, Authenticated: {user_info is not None}")
        
        # Get session data and memory manager
        session_data = session_manager.get_session(session_id)
        memory_manager = session_manager.get_memory_manager(session_id, user_id)
        
        # Store user information in session
        if user_info:
            session_data["authenticated_user"] = user_info
            session_data["user_preferences"] = user_preferences
        
        if memory_manager:
            session_data["memory_enabled"] = True
            logger.info("AgentCore Memory integration active")
        
        # Extract request parameters
        user_message = input_data.get("prompt", "")
        request_type = input_data.get("type", "general")
        location = input_data.get("location", "Austin, TX")
        max_price = input_data.get("max_price", 500000)
        
        # Validate required parameters
        if not user_message:
            raise ValueError("No prompt found in input. Please provide a 'prompt' key in the input.")
        
        # Route request based on type with memory integration
        result = None
        if request_type == "automated_research":
            result = await handle_automated_research(input_data, session_data, memory_manager)
        elif request_type == "market_research":
            result = await handle_market_research(input_data, session_data, memory_manager)
        elif request_type == "property_analysis":
            result = await handle_property_analysis(input_data, session_data, memory_manager)
        elif request_type == "enhanced_analysis":
            result = await handle_enhanced_analysis(input_data, session_data, memory_manager)
        elif request_type == "investment_opportunities":
            result = await handle_investment_opportunities(input_data, session_data, memory_manager)
        else:
            result = await handle_intelligent_routing(input_data, session_data, memory_manager)
        
        # Update session with results
        session_manager.update_session(session_id, {
            "last_request": input_data,
            "last_response": result,
            "request_count": session_data.get("request_count", 0) + 1
        })
        
        # Return AgentCore-compatible response following official format
        return {
            "output": {
                "message": result.get("message", result),
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "user_id": user_id,
                "request_type": request_type,
                "location": location,
                "service": "PropertyPilot-AgentCore",
                "memory_enabled": session_data.get("memory_enabled", False),
                "authentication": {
                    "authenticated": user_info is not None,
                    "username": user_info.get('username') if user_info else None,
                    "email": user_info.get('email') if user_info else None,
                    "preferences_loaded": bool(user_preferences)
                },
                "analysis_metadata": {
                    "session_requests": session_data.get("request_count", 1),
                    "properties_analyzed": len(session_data.get("properties_analyzed", [])),
                    "analysis_history_count": len(session_data.get("analysis_history", [])),
                    "personalized": user_info is not None
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing PropertyPilot request: {str(e)}", exc_info=True)
        return {
            "output": {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id if 'session_id' in locals() else "unknown",
                "status": "error",
                "service": "PropertyPilot-AgentCore"
            }
        }

async def handle_automated_research(payload: Dict, session_data: Dict, memory_manager: Optional[AgentCoreMemorySessionManager] = None) -> Dict:
    """Handle automated web research requests"""
    try:
        location = payload.get("location", "Austin, TX")
        research_type = payload.get("research_focus", "market_conditions")
        
        logger.info(f"Starting automated research for {location}, focus: {research_type}")
        
        researcher = AutomatedWebResearcher()
        
        if research_type == "market_conditions":
            result = await researcher.research_market_conditions(location)
        elif research_type == "property_specific":
            address = payload.get("address", "")
            property_details = payload.get("property_details", {})
            result = await researcher.research_property_specifics(address, property_details)
        elif research_type == "investment_opportunities":
            criteria = payload.get("criteria", {"location": location})
            result = await researcher.research_investment_opportunities(criteria)
        else:
            # Default to market conditions research
            result = await researcher.research_market_conditions(location)
        
        # Store research in session
        if "research_history" not in session_data:
            session_data["research_history"] = []
        
        session_data["research_history"].append({
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "research_type": research_type,
            "confidence": result.get("confidence_score", 0.0)
        })
        
        return {
            "type": "automated_research",
            "research_focus": research_type,
            "location": location,
            "result": result,
            "session_context": {
                "total_research_sessions": len(session_data.get("research_history", [])),
                "research_locations": list(set([r["location"] for r in session_data.get("research_history", [])]))
            }
        }
        
    except Exception as e:
        logger.error(f"Automated research error: {str(e)}")
        return {
            "type": "automated_research",
            "error": str(e),
            "status": "failed"
        }

async def handle_market_research(payload: Dict, session_data: Dict, memory_manager: Optional[AgentCoreMemorySessionManager] = None) -> Dict:
    """Handle comprehensive market research"""
    try:
        location = payload.get("location", "Austin, TX")
        property_type = payload.get("property_type", "residential")
        
        logger.info(f"Starting comprehensive market research for {location}")
        
        researcher = AutomatedWebResearcher()
        market_data = await researcher.research_market_conditions(location, property_type)
        
        return {
            "type": "market_research",
            "location": location,
            "property_type": property_type,
            "market_data": market_data,
            "actionable_insights": _extract_actionable_insights(market_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market research error: {str(e)}")
        return {
            "type": "market_research",
            "error": str(e),
            "status": "failed"
        }

async def handle_enhanced_analysis(payload: Dict, session_data: Dict, memory_manager: Optional[AgentCoreMemorySessionManager] = None) -> Dict:
    """Handle enhanced property analysis with web research and memory integration"""
    try:
        location = payload.get("location", "Austin, TX")
        max_price = payload.get("max_price", 500000)
        user_preferences = payload.get("user_preferences", {})
        
        logger.info(f"Starting enhanced analysis for {location} with memory integration: {memory_manager is not None}")
        
        # Create PropertyPilot agent with memory if available
        if memory_manager:
            # Create agent with AgentCore Memory integration
            from strands import Agent
            enhanced_agent = Agent(
                name="PropertyPilotEnhanced",
                instructions="""
                You are an enhanced PropertyPilot agent with memory capabilities for real estate investment analysis.
                Use your memory to:
                - Remember user preferences and investment criteria
                - Recall previous property analyses and market research
                - Build upon past conversations and insights
                - Provide personalized recommendations based on user history
                
                Always consider the user's investment timeline, risk tolerance, and property preferences.
                """,
                session_manager=memory_manager
            )
            
            # Use memory-enabled agent for analysis
            analysis_prompt = f"""
            Analyze investment opportunities in {location} with maximum price ${max_price:,}.
            
            User preferences: {json.dumps(user_preferences, indent=2)}
            
            Please provide:
            1. Property recommendations based on criteria and past preferences
            2. Market analysis considering previous research
            3. Investment recommendations tailored to user profile
            4. Risk assessment based on user's risk tolerance
            """
            
            memory_enhanced_result = enhanced_agent(analysis_prompt)
            
            # Also run standard PropertyPilot analysis
            property_analysis = await property_pilot.analyze_property_investment(
                location=location,
                max_price=max_price
            )
            
            # Combine results
            enhanced_result = {
                "memory_enhanced_analysis": memory_enhanced_result.message,
                "standard_analysis": property_analysis,
                "memory_integration": "enabled"
            }
            
        else:
            # Standard analysis without memory
            property_analysis = await property_pilot.analyze_property_investment(
                location=location,
                max_price=max_price
            )
            
            # Enhance with web research
            enhanced_result = await web_research_agent.enhance_property_analysis(
                property_analysis, location
            )
            enhanced_result["memory_integration"] = "disabled"
        
        # Store analysis in session
        analysis_record = {
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "max_price": max_price,
            "analysis_type": "enhanced",
            "user_preferences": user_preferences,
            "memory_enabled": memory_manager is not None,
            "confidence": enhanced_result.get("web_research", {}).get("market_conditions", {}).get("confidence_score", 0.8)
        }
        
        session_data["analysis_history"].append(analysis_record)
        session_data["properties_analyzed"].append(f"{location}_{max_price}")
        
        return {
            "message": f"Enhanced analysis completed for {location}",
            "type": "enhanced_analysis",
            "location": location,
            "max_price": max_price,
            "enhanced_analysis": enhanced_result,
            "session_context": {
                "total_analyses": len(session_data["analysis_history"]),
                "enhanced_analyses": sum(1 for a in session_data["analysis_history"] if a.get("analysis_type") == "enhanced"),
                "memory_enabled": memory_manager is not None,
                "unique_locations": len(set(session_data.get("properties_analyzed", [])))
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced analysis error: {str(e)}")
        return {
            "message": f"Enhanced analysis failed: {str(e)}",
            "type": "enhanced_analysis",
            "error": str(e),
            "status": "failed"
        }

async def handle_investment_opportunities(payload: Dict, session_data: Dict, memory_manager: Optional[AgentCoreMemorySessionManager] = None) -> Dict:
    """Handle investment opportunity research"""
    try:
        criteria = payload.get("criteria", {})
        location = criteria.get("location", payload.get("location", "Austin, TX"))
        
        logger.info(f"Researching investment opportunities for {location}")
        
        researcher = AutomatedWebResearcher()
        opportunities = await researcher.research_investment_opportunities(criteria)
        
        return {
            "type": "investment_opportunities",
            "criteria": criteria,
            "location": location,
            "opportunities": opportunities,
            "recommendations": _generate_opportunity_recommendations(opportunities),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Investment opportunities research error: {str(e)}")
        return {
            "type": "investment_opportunities",
            "error": str(e),
            "status": "failed"
        }

async def handle_property_analysis(payload: Dict, session_data: Dict, memory_manager: Optional[AgentCoreMemorySessionManager] = None) -> Dict:
    """Handle property analysis using PropertyPilot agents"""
    try:
        location = payload.get("location", "Austin, TX")
        max_price = payload.get("max_price", 500000)
        
        logger.info(f"Starting property analysis: {location}, max_price: ${max_price}")
        
        # Run PropertyPilot analysis
        analysis_result = await property_pilot.analyze_property_investment(
            location=location,
            max_price=max_price
        )
        
        # Store in session history
        session_data["analysis_history"].append({
            "timestamp": datetime.now().isoformat(),
            "location": location,
            "max_price": max_price,
            "result_summary": analysis_result["analysis_result"][:200] + "..."
        })
        
        return {
            "type": "property_analysis",
            "analysis": analysis_result,
            "session_context": {
                "total_analyses": len(session_data["analysis_history"]),
                "preferred_locations": list(set([a["location"] for a in session_data["analysis_history"]]))
            }
        }
        
    except Exception as e:
        logger.error(f"Property analysis error: {str(e)}")
        return {
            "type": "property_analysis",
            "error": str(e),
            "status": "failed"
        }

def _extract_actionable_insights(market_data: Dict) -> List[str]:
    """Extract actionable insights from market research data"""
    insights = []
    
    summary = market_data.get("summary", {})
    confidence = market_data.get("confidence_score", 0.0)
    
    # Market temperature insights
    market_temp = summary.get("market_overview", {}).get("temperature", "unknown")
    if market_temp == "hot":
        insights.append("Market is competitive - prepare strong offers and act quickly")
    elif market_temp == "cold":
        insights.append("Buyer's market conditions - negotiate aggressively and take time for analysis")
    elif market_temp == "balanced":
        insights.append("Balanced market - standard negotiation strategies apply")
    
    # Price analysis insights
    price_analysis = summary.get("price_analysis", {})
    if price_analysis:
        median_price = price_analysis.get("median_price_estimate")
        if median_price:
            insights.append(f"Estimated median price: ${median_price:,.0f}")
    
    # Confidence-based insights
    if confidence > 0.7:
        insights.append("High confidence in market data - reliable for decision making")
    elif confidence < 0.4:
        insights.append("Limited market data available - conduct additional research before investing")
    
    # Investment sentiment
    sentiment = summary.get("investment_indicators", {}).get("overall_sentiment", "neutral")
    if sentiment == "positive":
        insights.append("Positive market sentiment - favorable conditions for investment")
    elif sentiment == "negative":
        insights.append("Negative market sentiment - exercise caution and consider timing")
    
    return insights

def _generate_opportunity_recommendations(opportunities: Dict) -> List[str]:
    """Generate recommendations from investment opportunities research"""
    recommendations = []
    
    if opportunities.get("status") == "failed":
        recommendations.append("Unable to research opportunities - try alternative research methods")
        return recommendations
    
    opportunity_count = len(opportunities.get("opportunities", []))
    
    if opportunity_count > 0:
        recommendations.append(f"Found {opportunity_count} potential opportunity sources")
        recommendations.append("Review each opportunity source for specific investment leads")
        recommendations.append("Cross-reference findings with local market analysis")
    else:
        recommendations.append("No specific opportunities identified - consider broadening search criteria")
    
    # Add timing recommendations
    recommendations.append("Monitor market conditions regularly for optimal timing")
    recommendations.append("Consider seasonal trends in real estate activity")
    
    return recommendations

async def handle_intelligent_routing(payload: Dict, session_data: Dict, memory_manager: Optional[AgentCoreMemorySessionManager] = None) -> Dict:
    """Intelligently route requests based on content"""
    try:
        user_message = payload.get("prompt", "").lower()
        location = payload.get("location", "Austin, TX")
        
        # Enhanced intent detection
        if any(keyword in user_message for keyword in ["market research", "market conditions", "market analysis"]):
            return await handle_market_research(payload, session_data)
        elif any(keyword in user_message for keyword in ["opportunities", "investment opportunities", "find investments"]):
            return await handle_investment_opportunities(payload, session_data)
        elif any(keyword in user_message for keyword in ["enhanced analysis", "comprehensive analysis", "detailed analysis"]):
            return await handle_enhanced_analysis(payload, session_data)
        elif any(keyword in user_message for keyword in ["research", "web research", "automated research"]):
            return await handle_automated_research(payload, session_data)
        elif any(keyword in user_message for keyword in ["property", "real estate", "investment", "roi"]):
            return await handle_property_analysis(payload, session_data)
        else:
            # Default to enhanced analysis for comprehensive results
            return await handle_enhanced_analysis(payload, session_data)
            
    except Exception as e:
        logger.error(f"Intelligent routing error: {str(e)}")
        return {
            "type": "intelligent_routing",
            "error": str(e),
            "status": "failed"
        }

def calculate_confidence_score(web_result: Dict, property_result: Dict) -> float:
    """Calculate confidence score based on available data"""
    score = 0.5  # Base score
    
    if web_result.get("status") != "failed":
        score += 0.2
    if property_result.get("status") != "failed":
        score += 0.3
    
    return min(1.0, score)

# Initialize PropertyPilot components on startup
async def initialize_components():
    """Initialize PropertyPilot components"""
    logger.info("🚀 PropertyPilot AgentCore service starting up...")
    logger.info(f"   AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    logger.info(f"   Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info(f"   Memory Integration: {'Enabled' if memory_client else 'Disabled'}")
    logger.info(f"   Observability: {'Enabled' if os.getenv('ENABLE_AGENTCORE_OBSERVABILITY') == 'true' else 'Disabled'}")
    
    # Test memory integration if enabled
    if memory_client:
        try:
            memories = memory_client.list_memories(maxResults=1)
            logger.info("✅ AgentCore Memory integration verified")
        except Exception as e:
            logger.warning(f"⚠️ AgentCore Memory integration warning: {e}")
    
    logger.info("🎉 PropertyPilot AgentCore service startup complete")

# Add required endpoints and Cognito authentication
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Create a separate FastAPI app for additional endpoints
fastapi_app = FastAPI(title="PropertyPilot-AgentCore-API", version="1.0.0")

# Security scheme for JWT tokens
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]

@fastapi_app.get("/ping")
async def ping():
    """Required ping endpoint for AgentCore health checks"""
    return {"status": "healthy", "service": "PropertyPilot-AgentCore"}

@fastapi_app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate user with Cognito and return JWT tokens"""
    try:
        # Authenticate with Cognito
        auth_result = cognito_helper.authenticate_user(request.username, request.password)
        
        if not auth_result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Extract user info from ID token
        user_info = cognito_helper.extract_user_from_token(auth_result['id_token'])
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Failed to extract user information")
        
        # Get user preferences
        user_preferences = cognito_helper.get_user_preferences(user_info['user_id'])
        user_info.update(user_preferences)
        
        return AuthResponse(
            access_token=auth_result['access_token'],
            token_type=auth_result['token_type'],
            expires_in=auth_result['expires_in'],
            user_info=user_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")

@fastapi_app.get("/auth/user")
async def get_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information from JWT token"""
    try:
        user_info = cognito_helper.extract_user_from_token(credentials.credentials)
        
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        # Get fresh user preferences
        user_preferences = cognito_helper.get_user_preferences(user_info['user_id'])
        user_info.update(user_preferences)
        
        return {
            "user_info": user_info,
            "authenticated": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user information")

@fastapi_app.get("/auth/status")
async def auth_status():
    """Get authentication service status"""
    return {
        "service": "PropertyPilot-Cognito-Auth",
        "cognito_configured": bool(cognito_helper.user_pool_id and cognito_helper.client_id),
        "user_pool_id": cognito_helper.user_pool_id,
        "region": os.getenv("AWS_REGION", "us-east-1"),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Run the AgentCore app
    logger.info("Starting PropertyPilot AgentCore service on port 8080...")
    app.run(host="0.0.0.0", port=8080)