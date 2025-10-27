#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from strands import Agent
from strands.models.gemini import GeminiModel

# Load environment variables
load_dotenv()

def test_strands_gemini():
    """Test Strands Gemini integration"""
    print("🤖 Testing Strands Gemini Integration")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: Not found")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    try:
        # Create Gemini model with Strands
        model = GeminiModel(
            client_args={
                "api_key": api_key,
            },
            model_id="gemini-2.5-pro",
            params={
                "temperature": 0.3,
                "max_output_tokens": 1024,
                "top_p": 0.9
            }
        )
        
        print("✅ Gemini model created successfully")
        
        # Create agent
        agent = Agent(model=model)
        print("✅ Agent created successfully")
        
        # Test simple query
        print("📤 Testing simple query...")
        response = agent("Hello! Can you help me analyze real estate investments? Just say 'Yes, I can help.'")
        
        print("✅ Strands Gemini integration successful!")
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Strands Gemini integration failed: {e}")
        return False

if __name__ == "__main__":
    test_strands_gemini()