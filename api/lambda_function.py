
import os
from mangum import Mangum
from main import app

# Set environment variables for Lambda
os.environ['AGENTCORE_ENDPOINT'] = 'https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/PropertyPilotGeminiEnhanced-A9pB9q790m/invoke'
os.environ['AWS_REGION'] = 'us-east-1'

# Create Lambda handler
handler = Mangum(app, lifespan="off")
