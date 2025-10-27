#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

def test_gemini_basic():
    """Test basic Gemini API functionality"""
    print("🤖 Testing Gemini 2.5 Pro Integration")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not set or using placeholder")
        print("Please provide your Gemini API key")
        return False
    
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not found")
    
    try:
        # Create Gemini client
        client = genai.Client(api_key=api_key)
        
        # Test basic generation - try different models
        models_to_try = ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-2.5-pro"]
        
        for model in models_to_try:
            print(f"Trying model: {model}")
            try:
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text="Hello! Can you help me analyze real estate investments? Just say 'Yes, I can help with real estate analysis.'"),
                        ],
                    ),
                ]
                
                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=-1,
                    ),
                )
                
                print("📤 Sending test request to Gemini...")
                
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                )
                
                print(f"✅ Gemini API test successful with {model}!")
                print(f"Response: {response.text}")
                return True
                
            except Exception as model_error:
                print(f"❌ Model {model} failed: {model_error}")
                continue
        
        print("❌ All models failed")
        return False
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_gemini_with_tools():
    """Test Gemini with Google Search tools"""
    print("\n🔍 Testing Gemini with Google Search")
    print("=" * 50)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not set")
        return False
    
    try:
        client = genai.Client(api_key=api_key)
        
        model = "gemini-2.5-pro"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="What are the current real estate market trends in Austin, Texas?"),
                ],
            ),
        ]
        
        tools = [
            types.Tool(googleSearch=types.GoogleSearch()),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=-1,
            ),
            tools=tools,
        )
        
        print("📤 Sending search request to Gemini...")
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        print("✅ Gemini with tools test successful!")
        print(f"Response: {response.text[:500]}...")
        return True
        
    except Exception as e:
        print(f"❌ Gemini with tools test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏠 PropertyPilot Gemini Integration Test")
    print("=" * 60)
    
    # Test basic functionality
    basic_success = test_gemini_basic()
    
    # Test with tools if basic works
    if basic_success:
        tools_success = test_gemini_with_tools()
    else:
        tools_success = False
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"Basic Gemini API: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Gemini with Tools: {'✅ PASS' if tools_success else '❌ FAIL'}")
    
    if basic_success and tools_success:
        print("\n🎉 Gemini integration is ready!")
        print("PropertyPilot can now use Google's Gemini 2.5 Pro model")
    else:
        print("\n⚠️ Gemini integration needs setup")
        print("Please provide a valid GEMINI_API_KEY")