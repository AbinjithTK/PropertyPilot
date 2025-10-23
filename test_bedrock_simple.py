import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# Try with Claude 3.5 Sonnet
model_id = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
body = json.dumps({
    'anthropic_version': 'bedrock-2023-05-31',
    'max_tokens': 100,
    'messages': [{'role': 'user', 'content': 'Hello, can you respond with just OK?'}]
})

try:
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=body,
        contentType='application/json'
    )
    result = json.loads(response['body'].read())
    print('✅ SUCCESS: Model invocation worked!')
    content = result['content'][0]['text']
    print(f'Response: {content}')
except Exception as e:
    print(f'❌ ERROR: {e}')