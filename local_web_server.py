#!/usr/bin/env python3
"""
PropertyPilot Local Web Server
Simple Flask server for testing PropertyPilot with web interface
"""

import os
import json
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import PropertyPilot components
try:
    from property_pilot_agents import PropertyPilotSystem
    from automated_web_research import EnhancedWebResearchAgent, AutomatedWebResearcher
    print("✅ PropertyPilot components loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: Could not import PropertyPilot components: {e}")
    PropertyPilotSystem = None
    EnhancedWebResearchAgent = None
    AutomatedWebResearcher = None

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

# Initialize PropertyPilot system
property_pilot = None
web_research_agent = None

if PropertyPilotSystem:
    try:
        property_pilot = PropertyPilotSystem()
        web_research_agent = EnhancedWebResearchAgent()
        print("✅ PropertyPilot system initialized")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize PropertyPilot: {e}")

@app.route('/')
def index():
    """Serve the web interface"""
    try:
        with open('web_interface.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <h1>PropertyPilot Local Server</h1>
        <p>Web interface not found. Please ensure web_interface.html exists.</p>
        <p>API endpoint available at: <code>/invoke</code></p>
        """

@app.route('/invoke', methods=['POST'])
def invoke_agent():
    """Main PropertyPilot invocation endpoint"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Extract input
        input_data = data.get('input', data)
        
        # Validate required fields
        prompt = input_data.get('prompt', '')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Extract parameters
        request_type = input_data.get('type', 'enhanced_analysis')
        location = input_data.get('location', 'Austin, TX')
        max_price = input_data.get('max_price', 500000)
        property_type = input_data.get('property_type', 'residential')
        
        print(f"🔍 Processing request: {request_type} for {location}")
        
        # Check if PropertyPilot is available
        if not property_pilot:
            return jsonify({
                "output": {
                    "error": "PropertyPilot system not available. Please check your environment configuration.",
                    "message": "Demo mode: This would analyze properties in " + location,
                    "timestamp": datetime.now().isoformat(),
                    "status": "demo_mode",
                    "demo_data": {
                        "location": location,
                        "max_price": max_price,
                        "property_type": property_type,
                        "analysis_type": request_type,
                        "sample_properties": [
                            {
                                "address": f"123 Sample St, {location}",
                                "price": max_price * 0.8,
                                "estimated_roi": "8.5%",
                                "rental_yield": "6.2%"
                            },
                            {
                                "address": f"456 Demo Ave, {location}",
                                "price": max_price * 0.9,
                                "estimated_roi": "7.8%",
                                "rental_yield": "5.9%"
                            }
                        ]
                    }
                }
            })
        
        # Route request based on type
        if request_type == 'enhanced_analysis':
            result = handle_enhanced_analysis_sync(input_data)
        elif request_type == 'property_analysis':
            result = handle_property_analysis_sync(input_data)
        elif request_type == 'market_research':
            result = handle_market_research_sync(input_data)
        elif request_type == 'investment_opportunities':
            result = handle_investment_opportunities_sync(input_data)
        else:
            result = handle_property_analysis_sync(input_data)
        
        # Return AgentCore-compatible response
        return jsonify({
            "output": {
                "message": f"Analysis completed for {location}",
                "timestamp": datetime.now().isoformat(),
                "location": location,
                "request_type": request_type,
                "service": "PropertyPilot-Local",
                "analysis": result,
                "session_id": f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "memory_enabled": False
            }
        })
        
    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        return jsonify({
            "output": {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "service": "PropertyPilot-Local"
            }
        }), 500

def handle_enhanced_analysis_sync(input_data):
    """Handle enhanced analysis synchronously"""
    try:
        location = input_data.get('location', 'Austin, TX')
        max_price = input_data.get('max_price', 500000)
        
        # Run PropertyPilot analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            analysis_result = loop.run_until_complete(
                property_pilot.analyze_property_investment(
                    location=location,
                    max_price=max_price
                )
            )
            
            # Enhance with web research if available
            if web_research_agent:
                enhanced_result = loop.run_until_complete(
                    web_research_agent.enhance_property_analysis(
                        analysis_result, location
                    )
                )
                return enhanced_result
            else:
                return analysis_result
                
        finally:
            loop.close()
            
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "analysis_type": "enhanced"
        }

def handle_property_analysis_sync(input_data):
    """Handle basic property analysis synchronously"""
    try:
        location = input_data.get('location', 'Austin, TX')
        max_price = input_data.get('max_price', 500000)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                property_pilot.analyze_property_investment(
                    location=location,
                    max_price=max_price
                )
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "analysis_type": "property"
        }

def handle_market_research_sync(input_data):
    """Handle market research synchronously"""
    try:
        location = input_data.get('location', 'Austin, TX')
        property_type = input_data.get('property_type', 'residential')
        
        if not web_research_agent:
            return {
                "error": "Web research agent not available",
                "status": "failed"
            }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            researcher = AutomatedWebResearcher()
            result = loop.run_until_complete(
                researcher.research_market_conditions(location, property_type)
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "analysis_type": "market_research"
        }

def handle_investment_opportunities_sync(input_data):
    """Handle investment opportunities research synchronously"""
    try:
        criteria = input_data.get('criteria', {})
        location = criteria.get('location', input_data.get('location', 'Austin, TX'))
        
        if not web_research_agent:
            return {
                "error": "Web research agent not available",
                "status": "failed"
            }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            researcher = AutomatedWebResearcher()
            result = loop.run_until_complete(
                researcher.research_investment_opportunities(criteria)
            )
            return result
        finally:
            loop.close()
            
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "analysis_type": "investment_opportunities"
        }

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "PropertyPilot-Local",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "property_pilot": property_pilot is not None,
            "web_research": web_research_agent is not None,
            "gemini_api_key": bool(os.getenv('GEMINI_API_KEY'))
        }
    })

@app.route('/status')
def status():
    """Detailed status endpoint"""
    return jsonify({
        "service": "PropertyPilot Local Web Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "gemini_api_key_configured": bool(os.getenv('GEMINI_API_KEY')),
            "aws_region": os.getenv('AWS_REGION', 'not-set'),
            "log_level": os.getenv('LOG_LEVEL', 'INFO')
        },
        "components": {
            "property_pilot_system": property_pilot is not None,
            "web_research_agent": web_research_agent is not None,
            "enhanced_web_researcher": AutomatedWebResearcher is not None
        },
        "endpoints": {
            "/": "Web interface",
            "/invoke": "PropertyPilot analysis endpoint",
            "/health": "Health check",
            "/status": "Detailed status"
        }
    })

if __name__ == '__main__':
    print("🚀 Starting PropertyPilot Local Web Server...")
    print(f"   Environment: {os.getenv('GEMINI_API_KEY', 'Not configured')[:10]}...")
    print(f"   Components: PropertyPilot={property_pilot is not None}, WebResearch={web_research_agent is not None}")
    print("   Web Interface: http://localhost:5000")
    print("   API Endpoint: http://localhost:5000/invoke")
    print("   Health Check: http://localhost:5000/health")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )