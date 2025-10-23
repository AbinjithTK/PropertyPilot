import boto3
import json

bedrock = boto3.client('bedrock', region_name='us-east-1')

try:
    # List inference profiles
    response = bedrock.list_inference_profiles()
    profiles = response.get('inferenceProfileSummaries', [])
    
    print(f"Available inference profiles: {len(profiles)}")
    for profile in profiles:
        profile_id = profile['inferenceProfileId']
        profile_name = profile.get('inferenceProfileName', 'N/A')
        status = profile.get('status', 'Unknown')
        print(f"  - {profile_id} ({profile_name}) - Status: {status}")
        
        # Check if it's Claude
        if 'claude' in profile_id.lower():
            print(f"    ✅ Claude profile found: {profile_id}")
            
except Exception as e:
    print(f"Error listing inference profiles: {e}")