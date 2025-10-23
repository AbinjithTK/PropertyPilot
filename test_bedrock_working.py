import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Use the correct inference profile for Claude 3.5 Sonnet
model_id = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
body = json.dumps({
    'anthropic_version': 'bedrock-2023-05-31',
    'max_tokens': 100,
    'messages': [{'role': 'user', 'content': 'Hello! Please respond with just "PropertyPilot is ready!" to confirm the connection works.'}]
})

try:
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=body,
        contentType='application/json'
    )
    result = json.loads(response['body'].read())
    print('✅ SUCCESS: Bedrock Runtime is working!')
    content = result['content'][0]['text']
    print(f'Claude Response: {content}')
    print('\n🎉 PropertyPilot can now run on AWS Bedrock!')
except Exception as e:
    print(f'❌ ERROR: {e}')