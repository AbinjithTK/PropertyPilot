# PropertyPilot Multi-Agent System Makefile
# Simplifies development, testing, and deployment workflows

.PHONY: help install test test-local test-bedrock test-performance deploy deploy-local clean lint format docker-build docker-push setup-aws

# Default target
help:
	@echo "PropertyPilot Multi-Agent System"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@echo "  install          - Install Python dependencies"
	@echo "  setup-env        - Set up environment configuration"
	@echo "  test             - Run all tests"
	@echo "  test-local       - Test agents locally"
	@echo "  test-bedrock     - Test deployed Bedrock agents"
	@echo "  test-performance - Run performance tests"
	@echo "  deploy           - Deploy to AWS Bedrock AgentCore"
	@echo "  deploy-local     - Run agents locally for development"
	@echo "  docker-build     - Build all Docker images"
	@echo "  docker-push      - Push images to ECR"
	@echo "  setup-aws        - Set up AWS resources"
	@echo "  lint             - Run code linting"
	@echo "  format           - Format code with black"
	@echo "  clean            - Clean up temporary files"
	@echo "  logs             - View CloudWatch logs"

# Installation and setup
install:
	@echo "📦 Installing PropertyPilot dependencies..."
	pip install -r requirements.txt
	@echo "✅ Installation complete!"

setup-env:
	@echo "🔧 Setting up environment configuration..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 Created .env file from template"; \
		echo "⚠️  Please edit .env with your actual API keys and configuration"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Testing
test: test-local test-performance
	@echo "🧪 All tests completed!"

test-local:
	@echo "🧪 Testing PropertyPilot agents locally..."
	python test_agents.py
	@echo "✅ Local tests completed!"

test-bedrock:
	@echo "🚀 Testing deployed Bedrock agents..."
	python test_agents.py bedrock
	@echo "✅ Bedrock tests completed!"

test-performance:
	@echo "⚡ Running performance tests..."
	python test_agents.py performance
	@echo "✅ Performance tests completed!"

test-all:
	@echo "🧪 Running complete test suite..."
	python test_agents.py all
	@echo "✅ All tests completed!"

# Development
run-local:
	@echo "🏃 Starting PropertyPilot locally..."
	python bedrock_deployment.py main

run-scout:
	@echo "🔍 Starting Property Scout agent..."
	python bedrock_deployment.py property-scout

run-analyzer:
	@echo "📊 Starting Market Analyzer agent..."
	python bedrock_deployment.py market-analyzer

run-evaluator:
	@echo "💰 Starting Deal Evaluator agent..."
	python bedrock_deployment.py deal-evaluator

run-manager:
	@echo "🎯 Starting Investment Manager agent..."
	python bedrock_deployment.py investment-manager

# Deployment
deploy:
	@echo "🚀 Deploying PropertyPilot to AWS Bedrock AgentCore..."
	chmod +x deploy.sh
	./deploy.sh
	@echo "✅ Deployment completed!"

deploy-test:
	@echo "🧪 Testing deployment..."
	python bedrock_deployment.py deploy
	@echo "✅ Deployment test completed!"

# Docker operations
docker-build:
	@echo "🐳 Building Docker images..."
	docker buildx create --use --name propertypilot-builder 2>/dev/null || docker buildx use propertypilot-builder
	docker buildx build --platform linux/arm64 -f Dockerfile.property-scout -t propertypilot-property-scout:latest --load .
	docker buildx build --platform linux/arm64 -f Dockerfile.market-analyzer -t propertypilot-market-analyzer:latest --load .
	docker buildx build --platform linux/arm64 -f Dockerfile.deal-evaluator -t propertypilot-deal-evaluator:latest --load .
	docker buildx build --platform linux/arm64 -f Dockerfile.investment-manager -t propertypilot-investment-manager:latest --load .
	docker buildx build --platform linux/arm64 -f Dockerfile.main -t propertypilot-main:latest --load .
	@echo "✅ Docker images built successfully!"

docker-test:
	@echo "🧪 Testing Docker images locally..."
	docker run --rm -p 8080:8080 -e AWS_REGION=us-east-1 propertypilot-main:latest &
	sleep 10
	curl -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d '{"prompt": "Test message"}' || true
	docker stop $$(docker ps -q --filter ancestor=propertypilot-main:latest) || true
	@echo "✅ Docker test completed!"

# AWS setup
setup-aws:
	@echo "☁️ Setting up AWS resources..."
	@echo "Creating IAM role for PropertyPilot agents..."
	@aws iam create-role --role-name PropertyPilotAgentRole --assume-role-policy-document file://trust-policy.json 2>/dev/null || echo "Role already exists"
	@aws iam attach-role-policy --role-name PropertyPilotAgentRole --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess 2>/dev/null || true
	@aws iam attach-role-policy --role-name PropertyPilotAgentRole --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess 2>/dev/null || true
	@echo "✅ AWS setup completed!"

# Code quality
lint:
	@echo "🔍 Running code linting..."
	flake8 --max-line-length=100 --ignore=E203,W503 *.py
	@echo "✅ Linting completed!"

format:
	@echo "🎨 Formatting code..."
	black --line-length=100 *.py
	@echo "✅ Code formatting completed!"

# Monitoring
logs:
	@echo "📋 Viewing CloudWatch logs..."
	aws logs describe-log-groups --log-group-name-prefix "/aws/bedrock-agentcore/propertypilot"

logs-tail:
	@echo "📋 Tailing CloudWatch logs..."
	aws logs tail /aws/bedrock-agentcore/propertypilot --follow

# Cleanup
clean:
	@echo "🧹 Cleaning up temporary files..."
	rm -f *.pyc
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -f test_results.json
	rm -f performance_results.json
	rm -f deployed_agents.json
	rm -f deployment_config.json
	rm -f trust-policy.json
	@echo "✅ Cleanup completed!"

clean-docker:
	@echo "🧹 Cleaning up Docker resources..."
	docker system prune -f
	docker builder prune -f
	@echo "✅ Docker cleanup completed!"

# Development workflow shortcuts
dev-setup: install setup-env
	@echo "🚀 Development environment ready!"

dev-test: test-local
	@echo "✅ Development tests passed!"

prod-deploy: lint test deploy
	@echo "🎉 Production deployment completed!"

# Status and info
status:
	@echo "📊 PropertyPilot System Status"
	@echo "=============================="
	@echo "Python version: $$(python --version)"
	@echo "AWS CLI version: $$(aws --version)"
	@echo "Docker version: $$(docker --version)"
	@echo "Environment file: $$([ -f .env ] && echo "✅ Present" || echo "❌ Missing")"
	@echo "Dependencies: $$(pip list | grep -E "(strands|boto3|fastapi)" | wc -l) key packages installed"

info:
	@echo "ℹ️  PropertyPilot Multi-Agent System"
	@echo "===================================="
	@echo "A sophisticated real estate investment analysis system"
	@echo "built with Strands Agents framework for AWS Bedrock."
	@echo ""
	@echo "Agents:"
	@echo "  🔍 Property Scout    - Property discovery and data collection"
	@echo "  📊 Market Analyzer   - Market research and valuation"
	@echo "  💰 Deal Evaluator    - Financial analysis and ROI calculations"
	@echo "  🎯 Investment Manager - Multi-agent orchestration"
	@echo ""
	@echo "For more information, see README.md"

# Quick start for new developers
quickstart: dev-setup dev-test
	@echo "🎉 PropertyPilot is ready for development!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env with your API keys"
	@echo "2. Run 'make run-local' to start the system"
	@echo "3. Run 'make deploy' when ready for production"
# Enhanc
ed AgentCore deployment
deploy-agentcore:
	@echo "🚀 Deploying PropertyPilot with full AgentCore benefits..."
	chmod +x deploy_agentcore.sh
	./deploy_agentcore.sh
	@echo "✅ Enhanced AgentCore deployment completed!"

test-agentcore:
	@echo "🧪 Testing AgentCore benefits..."
	python test_agentcore_benefits.py comprehensive
	@echo "✅ AgentCore benefits testing completed!"

test-agentcore-session:
	@echo "🔒 Testing session isolation..."
	python test_agentcore_benefits.py session

test-agentcore-observability:
	@echo "📊 Testing observability features..."
	python test_agentcore_benefits.py observability

test-agentcore-scaling:
	@echo "⚡ Testing auto-scaling..."
	python test_agentcore_benefits.py scaling

test-agentcore-security:
	@echo "🛡️ Testing security features..."
	python test_agentcore_benefits.py security

# AgentCore monitoring
agentcore-logs:
	@echo "📋 Viewing AgentCore logs..."
	aws logs describe-log-groups --log-group-name-prefix "/aws/bedrock-agentcore/propertypilot"

agentcore-metrics:
	@echo "📊 Viewing AgentCore metrics..."
	aws cloudwatch list-metrics --namespace "AWS/BedrockAgentCore"

agentcore-traces:
	@echo "🔍 Viewing X-Ray traces..."
	aws xray get-trace-summaries --time-range-type TimeRangeByStartTime --start-time $(shell date -d '1 hour ago' -u +%Y-%m-%dT%H:%M:%S) --end-time $(shell date -u +%Y-%m-%dT%H:%M:%S)

# Enhanced development workflow
agentcore-setup: install setup-env
	@echo "🚀 AgentCore development environment ready!"
	@echo "Next steps:"
	@echo "1. Edit .env with your API keys"
	@echo "2. Run 'make deploy-agentcore' for full deployment"
	@echo "3. Run 'make test-agentcore' to validate all benefits"

agentcore-full-deploy: lint test deploy-agentcore test-agentcore
	@echo "🎉 Full AgentCore deployment with testing completed!"