# PropertyPilot - Multi-Agent Real Estate Investment System

PropertyPilot is a sophisticated multi-agent system built with **Strands Agents** framework for AWS Bedrock deployment. It automates real estate investment analysis through specialized AI agents that work together to find, analyze, and evaluate property investment opportunities.

## 🏗️ System Architecture

PropertyPilot consists of 4 specialized agents plus an automated web research system working in coordination:

### 1. **Property Scout Agent** (Port 8081)
- **Purpose**: Property discovery and data collection
- **Capabilities**:
  - Web scraping from Zillow, Realtor.com, MLS feeds
  - Property filtering based on investment criteria
  - Real-time listing monitoring and alerts
  - Geocoding and property data normalization
  - DynamoDB storage integration

### 2. **Market Analyzer Agent** (Port 8082)  
- **Purpose**: Market research and valuation analysis
- **Capabilities**:
  - Demographic and economic data analysis (Census API)
  - Comparable sales research and valuation
  - Neighborhood trend identification and scoring
  - School district and amenity evaluation
  - Market timing recommendations

### 3. **Deal Evaluator Agent** (Port 8083)
- **Purpose**: Financial analysis and ROI calculations
- **Capabilities**:
  - Cash flow and ROI calculations
  - Risk assessment and scoring algorithms
  - Repair cost estimation from property images
  - Rental yield analysis and projections
  - Investment recommendation generation

### 4. **Investment Manager Agent** (Port 8084)
- **Purpose**: Multi-agent orchestration and portfolio management
- **Capabilities**:
  - Coordinates all other agents using Strands Swarm pattern
  - Manages investment pipeline and opportunities
  - Generates comprehensive investment reports
  - Portfolio optimization and tracking
  - Strategic investment decision making

### 5. **Automated Web Research System**
- **Purpose**: Intelligent web research and market data collection
- **Capabilities**:
  - Automated market conditions research across multiple sources
  - Property-specific research and neighborhood analysis
  - Investment opportunity identification and analysis
  - Real-time market sentiment and trend analysis
  - Integration with NovaAct for intelligent web interaction
  - Enhanced analysis combining AI agents with web research

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- AWS Account with Bedrock access
- Docker (for deployment)
- AWS CLI configured

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd propertypilot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and AWS configuration
```

### 2. Local Testing

```bash
# Test all agents locally
python test_agents.py

# Test specific functionality
python property_pilot_agents.py

# Run performance tests
python test_agents.py performance
```

### 3. AWS Bedrock Deployment

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy all agents to AWS Bedrock AgentCore
./deploy.sh

# Test deployed agents
python test_agents.py bedrock
```

## 🛠️ Technology Stack

### Core Framework
- **Strands Agents**: Multi-agent orchestration and AI framework
- **AWS Bedrock**: Claude 3.5 Sonnet for primary AI processing
- **FastAPI**: REST API framework for agent services

### Data & Storage
- **DynamoDB**: Property data and search indexes
- **RDS PostgreSQL**: Financial calculations and portfolio tracking
- **S3**: Property images, documents, and reports
- **ElastiCache Redis**: Caching for frequent queries

### External Integrations
- **Property APIs**: Zillow, Realtor.com, MLS feeds
- **Market Data**: Census API, BLS API, Fred Economic Data
- **Geospatial**: AWS Location Service, Google Maps API
- **Financial**: Yahoo Finance, Alpha Vantage APIs

### Infrastructure
- **AWS Bedrock AgentCore**: Serverless agent runtime
- **Docker**: Containerized deployment
- **CloudWatch**: Logging and monitoring
- **ADOT**: Distributed tracing and observability

## 📋 Agent Interaction Patterns

PropertyPilot uses **Strands Swarm** pattern for collaborative multi-agent analysis enhanced with automated web research:

```python
# Example: Enhanced investment analysis with web research
result = await enhanced_analysis({
    "type": "enhanced_analysis",
    "location": "Austin, TX",
    "max_price": 400000
})
```

The enhanced system workflow:
1. **Automated Web Research** gathers real-time market data
2. **Property Scout** finds and filters properties
3. **Market Analyzer** analyzes conditions with web insights
4. **Deal Evaluator** calculates metrics with enhanced data
5. **Investment Manager** synthesizes comprehensive recommendations

## 🔧 Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# External API Keys
GOOGLE_MAPS_API_KEY=your_maps_key
ZILLOW_API_KEY=your_zillow_key
CENSUS_API_KEY=your_census_key
ALPHA_VANTAGE_API_KEY=your_av_key

# Database Configuration
RDS_HOST=your_rds_endpoint
RDS_DATABASE=propertypilot
REDIS_HOST=localhost
REDIS_PORT=6379

# Application Settings
LOG_LEVEL=INFO
MAX_CONCURRENT_SCRAPES=5
PROPERTY_CACHE_TTL=3600
```

### Agent Prompts

Each agent has specialized instructions optimized for their role:

- **Property Scout**: Focuses on finding high-potential investment properties
- **Market Analyzer**: Emphasizes accurate market valuations and trends
- **Deal Evaluator**: Conservative financial analysis with risk assessment
- **Investment Manager**: Strategic coordination and decision making

## 🧪 Testing

### Local Testing
```bash
# Test all agents locally
python test_agents.py

# Test individual components
python -c "from property_pilot_agents import PropertyPilotSystem; system = PropertyPilotSystem(); print(system.property_scout('Find properties in Austin'))"
```

### Bedrock Testing
```bash
# Test deployed agents
python test_agents.py bedrock

# Performance testing
python test_agents.py performance

# Complete test suite
python test_agents.py all
```

## 📊 Monitoring & Observability

### CloudWatch Integration
- Agent execution logs
- Performance metrics
- Error tracking and alerts

### ADOT Tracing
```bash
# Enable distributed tracing
opentelemetry-instrument python bedrock_deployment.py main
```

### Custom Metrics
- Property analysis completion rates
- Agent response times
- Investment recommendation accuracy

## 🏗️ Deployment Options

### 1. AWS Bedrock AgentCore (Recommended)
```bash
./deploy.sh
```

### 2. Individual Agent Services
```bash
# Deploy specific agents
python bedrock_deployment.py property-scout
python bedrock_deployment.py market-analyzer
python bedrock_deployment.py deal-evaluator
python bedrock_deployment.py investment-manager
```

### 3. Local Development
```bash
# Run main service locally
python bedrock_deployment.py main
```

## 📈 Usage Examples

### Enhanced Property Analysis with Web Research
```python
# Enhanced analysis with automated web research
payload = {
    "type": "enhanced_analysis",
    "location": "Austin, TX",
    "max_price": 400000
}

result = await invoke(payload)
print(f"Enhanced Analysis: {result['enhanced_analysis']}")
```

### Automated Market Research
```python
# Comprehensive market research
payload = {
    "type": "market_research",
    "location": "Denver, CO",
    "property_type": "residential"
}

market_data = await invoke(payload)
print(f"Market Insights: {market_data['actionable_insights']}")
```

### Investment Opportunity Research
```python
# Research investment opportunities
payload = {
    "type": "investment_opportunities",
    "criteria": {
        "location": "Phoenix, AZ",
        "max_price": 350000,
        "min_roi": 10.0,
        "strategy": "buy and hold"
    }
}

opportunities = await invoke(payload)
print(f"Opportunities: {opportunities['recommendations']}")
```

### Property-Specific Research
```python
# Research specific property details
payload = {
    "type": "automated_research",
    "research_focus": "property_specific",
    "address": "123 Main St, Austin, TX",
    "property_details": {
        "price": 450000,
        "bedrooms": 3,
        "bathrooms": 2
    }
}

property_research = await invoke(payload)
```

### Bedrock Agent Invocation
```python
import boto3
import json

client = boto3.client('bedrock-agentcore')

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/propertypilot-main',
    runtimeSessionId='session-12345678901234567890123456789012',
    payload=json.dumps({
        "prompt": "Analyze investment opportunities in Miami, FL",
        "location": "Miami, FL",
        "max_price": 600000
    })
)
```

## 🔒 Security & Best Practices

### IAM Permissions
- Least privilege access for agent roles
- Separate roles for each agent service
- Secure API key management

### Data Protection
- Encrypted data storage (DynamoDB, RDS)
- Secure API communications (HTTPS)
- PII data handling compliance

### Error Handling
- Graceful degradation for API failures
- Retry logic with exponential backoff
- Comprehensive logging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [Strands Agents Docs](https://strandsagents.com/latest/)
- **AWS Bedrock**: [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- **Issues**: Create an issue in this repository

## 🎯 Roadmap

- [ ] Integration with additional MLS feeds
- [ ] Advanced machine learning for property valuation
- [ ] Mobile app for property scouting
- [ ] Integration with property management systems
- [ ] Automated offer generation and submission
- [ ] Portfolio optimization algorithms

---

**PropertyPilot** - Intelligent Real Estate Investment Analysis with Multi-Agent AI 🏠🤖