import boto3

bedrock = boto3.client('bedrock', region_name='us-east-1')
try:
    response = bedrock.list_foundation_models()
    claude_models = [m for m in response['modelSummaries'] if 'claude' in m['modelId'].lower()]
    print(f'Available Claude models: {len(claude_models)}')
    for model in claude_models[:5]:
        model_id = model['modelId']
        status = model.get('modelLifecycle', {}).get('status', 'Unknown')
        print(f'  - {model_id} (Status: {status})')
except Exception as e:
    print(f'Error: {e}')