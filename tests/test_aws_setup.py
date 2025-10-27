#!/usr/bin/env python3
"""
Test AWS Bedrock setup for PropertyPilot
"""

import os
import boto3
import json
from datetime import datetime

def test_aws_credentials():
    """Test AWS credentials configuration"""
    print("1. Testing AWS Credentials...")
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Credentials Valid")
        print(f"   Account: {identity.get('Account', 'Unknown')}")
        print(f"   User/Role: {identity.get('Arn', 'Unknown').split('/')[-1]}")
        return True
    except Exception as e:
        print(f"❌ AWS Credentials Failed: {e}")
        print("   💡 Run: aws configure")
        return False

def test_bedrock_access():
    """Test AWS Bedrock service access"""
    print("\n2. Testing Bedrock Service Access...")
    try:
        bedrock = boto3.client('bedrock', region_name='us-east-1')
        models = bedrock.list_foundation_models()
        print(f"✅ Bedrock Access Successful")
        print(f"   Available Models: {len(models['modelSummaries'])}")
        return True, models
    except Exception as e:
        print(f"❌ Bedrock Access Failed: {e}")
        print("   💡 Check region and permissions")
        return False, None

def test_claude_models(models_response):
    """Test Claude model availability"""
    print("\n3. Testing Claude Model Access...")
    
    if not models_response:
        print("❌ No models available to test")
        return False
    
    claude_models = []
    for model in models_response['modelSummaries']:
        if 'claude' in model['modelId'].lower():
            claude_models.append(model)
    
    if not claude_models:
        print("❌ No Claude models found")
        print("   💡 Enable Claude models in Bedrock console")
        return False
    
    print(f"✅ Found {len(claude_models)} Claude models:")
    for model in claude_models[:3]:  # Show first 3
        print(f"   - {model['modelId']}")
    
    return True

def test_bedrock_runtime():
    """Test Bedrock Runtime (actual model invocation)"""
    print("\n4. Testing Bedrock Runtime...")
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with Claude 3 Haiku (cheapest)
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        body = json.dumps({
            "messages": [
                {
                    "role": "user", 
                    "content": "Hello! Just testing the connection. Please respond with 'PropertyPilot connection successful!'"
                }
            ],
            "max_tokens": 50,
            "anthropic_version": "bedrock-2023-05-31"
        })
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        ai_response = response_body['content'][0]['text']
        
        print(f"✅ Bedrock Runtime Successful")
        print(f"   Model: {model_id}")
        print(f"   Response: {ai_response}")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock Runtime Failed: {e}")
        if "AccessDeniedException" in str(e):
            print("   💡 Enable Claude models in Bedrock console")
        elif "INVALID_PAYMENT_INSTRUMENT" in str(e):
            print("   💡 Add payment method to AWS account")
        return False

def test_propertypilot_agents():
    """Test PropertyPilot agents with AWS Bedrock"""
    print("\n5. Testing PropertyPilot Agents...")
    try:
        from property_pilot_agents import PropertyPilotSystem
        
        # Initialize PropertyPilot
        property_pilot = PropertyPilotSystem()
        print("✅ PropertyPilot System Initialized")
        
        # Test a simple agent call
        scout_result = property_pilot.property_scout("Hello, are you working?")
        print(f"✅ Property Scout Agent Responding")
        print(f"   Response length: {len(scout_result.message)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ PropertyPilot Agents Failed: {e}")
        return False

def main():
    """Main test function"""
    print("🏠 PropertyPilot AWS Bedrock Setup Test")
    print("=" * 50)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        test_aws_credentials(),
        *test_bedrock_access(),  # Returns tuple (success, models)
    ]
    
    credentials_ok = tests[0]
    bedrock_ok = tests[1]
    models_response = tests[2] if len(tests) > 2 else None
    
    claude_ok = test_claude_models(models_response) if bedrock_ok else False
    runtime_ok = test_bedrock_runtime() if bedrock_ok else False
    agents_ok = test_propertypilot_agents() if runtime_ok else False
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 AWS BEDROCK SETUP SUMMARY")
    print("=" * 50)
    
    results = {
        "AWS Credentials": "✅ PASS" if credentials_ok else "❌ FAIL",
        "Bedrock Service": "✅ PASS" if bedrock_ok else "❌ FAIL", 
        "Claude Models": "✅ PASS" if claude_ok else "❌ FAIL",
        "Bedrock Runtime": "✅ PASS" if runtime_ok else "❌ FAIL",
        "PropertyPilot Agents": "✅ PASS" if agents_ok else "❌ FAIL"
    }
    
    for test_name, result in results.items():
        print(f"   {test_name}: {result}")
    
    passed = sum(1 for result in results.values() if "✅ PASS" in result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 SETUP COMPLETE!")
        print("   PropertyPilot is ready with AWS Bedrock AI!")
        print("   You can now run: python test_agents_functionality.py")
    else:
        print(f"\n⚠️ Setup Issues Found")
        print("   📖 See AWS_BEDROCK_SETUP.md for detailed instructions")
        
        if not credentials_ok:
            print("   🔧 Fix: Run 'aws configure' with your credentials")
        if not claude_ok:
            print("   🔧 Fix: Enable Claude models in Bedrock console")
        if not runtime_ok:
            print("   🔧 Fix: Add payment method to AWS account")
    
    print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()