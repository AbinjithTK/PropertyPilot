import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Try with Claude Opus 4 using full ARN
model_id = 'arn:aws:bedrock:us-east-1:476114109859:inference-profile/us.anthropic.claude-opus-4-20250514-v1:0'

# Use converse API instead of invoke_model
try:
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=[
            {
                'role': 'user',
                'content': [
                    {
                        'text': 'Hello! Please respond with just "PropertyPilot Opus 4 is ready!" to confirm the connection works.'
                    }
                ]
            }
        ],
        inferenceConfig={
            'maxTokens': 100,
            'temperature': 0.3
        }
    )
    
    print('✅ SUCCESS: Claude Opus 4 is working!')
    content = response['output']['message']['content'][0]['text']
    print(f'Claude Response: {content}')
    print('\n🎉 PropertyPilot can now run with Claude Opus 4!')
    
except Exception as e:
    print(f'❌ ERROR: {e}')