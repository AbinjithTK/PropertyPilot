# Technology Stack & Build System

## Core Framework
- **Python 3.9+** - Primary language
- **Strands Agents** - Multi-agent orchestration framework
- **AWS Bedrock** - Claude 3.5 Sonnet for AI processing
- **FastAPI** - REST API framework for agent services

## AWS Infrastructure
- **AWS Bedrock AgentCore** - Serverless agent runtime with session isolation
- **DynamoDB** - Property data and search indexes
- **RDS PostgreSQL** - Financial calculations and portfolio tracking
- **S3** - Property images, documents, and reports
- **ElastiCache Redis** - Caching for frequent queries
- **CloudWatch** - Logging and monitoring
- **ADOT** - Distributed tracing and observability

## Key Dependencies
- `strands-agents>=1.0.0` - Agent framework
- `boto3>=1.34.0` - AWS SDK
- `fastapi>=0.104.0` - Web framework
- `bedrock-agentcore>=1.0.0` - AgentCore runtime
- `nova-act>=1.0.0` - Enhanced web research
- `pandas>=2.1.0`, `numpy>=1.24.0` - Data processing
- `selenium>=4.15.0` - Web scraping

## Build & Development Commands

### Setup
```bash
make install          # Install dependencies
make setup-env        # Create .env from template
make dev-setup        # Complete development setup
```

### Testing
```bash
make test             # Run all tests
make test-local       # Test agents locally
make test-bedrock     # Test deployed agents
make test-performance # Performance testing
```

### Deployment
```bash
make deploy           # Deploy to AWS Bedrock AgentCore
make deploy-agentcore # Enhanced deployment with full benefits
make run-local        # Run locally for development
```

### Docker
```bash
make docker-build     # Build all Docker images
make docker-test      # Test Docker images locally
```

### Code Quality
```bash
make lint             # Run flake8 linting
make format           # Format with black (100 char line length)
make clean            # Clean temporary files
```

## Environment Configuration
- Copy `.env.example` to `.env` and configure API keys
- AWS credentials required for Bedrock and other services
- External API keys needed: Google Maps, Zillow, Census, Alpha Vantage