#!/usr/bin/env python3
"""
Setup Lambda IAM Role for PropertyPilot API
Create the necessary IAM role and policies for Lambda deployment
"""

import boto3
import json
import time

def create_lambda_execution_role():
    """Create Lambda execution role"""
    
    iam = boto3.client('iam')
    
    # Trust policy for Lambda
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_name = 'PropertyPilot-Lambda-Role'
    
    try:
        # Create role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='PropertyPilot Lambda execution role'
        )
        
        print(f"✅ Created IAM role: {role_name}")
        
        # Attach basic Lambda execution policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        print("✅ Attached basic execution policy")
        
        # Wait for role to be available
        print("⏳ Waiting for role to be available...")
        time.sleep(10)
        
        role_arn = response['Role']['Arn']
        return role_arn
        
    except iam.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        response = iam.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_name}")
        return role_arn
    
    except Exception as e:
        print(f"❌ Failed to create IAM role: {e}")
        return None

if __name__ == "__main__":
    print("🔐 Setting up Lambda IAM role...")
    role_arn = create_lambda_execution_role()
    if role_arn:
        print(f"✅ Role ARN: {role_arn}")
    else:
        print("❌ Failed to setup IAM role")