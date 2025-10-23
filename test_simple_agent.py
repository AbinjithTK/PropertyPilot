from strands import Agent
from strands.models import BedrockModel
import os

# Test with the working Claude Opus 4 model
model_id = "arn:aws:bedrock:us-east-1:476114109859:inference-profile/us.anthropic.claude-opus-4-20250514-v1:0"

try:
    print("🧪 Testing simple Strands agent with Claude Opus 4...")
    
    # Create BedrockModel with the working model ID
    bedrock_model = BedrockModel(
        model_id=model_id,
        region_name="us-east-1",
        temperature=0.3,
        streaming=False  # Try non-streaming first
    )
    
    # Create simple agent
    agent = Agent(
        model=bedrock_model,
        name="TestAgent"
    )
    
    # Test the agent
    response = agent("Hello! Please respond with 'PropertyPilot agent is working!' to confirm.")
    
    print("✅ SUCCESS: Strands agent is working!")
    print(f"Response: {response.message}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nTrying with streaming disabled...")
    
    try:
        # Try with different configuration
        bedrock_model = BedrockModel(
            model_id="us.anthropic.claude-opus-4-20250514-v1:0",  # Try without ARN
            region_name="us-east-1",
            temperature=0.3,
            streaming=False
        )
        
        agent = Agent(model=bedrock_model)
        response = agent("Hello! Please respond with 'PropertyPilot agent is working!'")
        
        print("✅ SUCCESS: Strands agent is working with simplified model ID!")
        print(f"Response: {response.message}")
        
    except Exception as e2:
        print(f"❌ ERROR with simplified model: {e2}")