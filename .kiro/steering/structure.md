# Project Structure & Organization

## Root Directory Layout

```
propertypilot/
├── main.py                     # AgentCore main service entrypoint
├── property_pilot_agents.py    # Core multi-agent system definitions
├── automated_web_research.py   # Enhanced web research capabilities
├── bedrock_deployment.py       # AWS Bedrock deployment configuration
├── agentcore_deployment.py     # Enhanced AgentCore deployment
├── requirements.txt            # Python dependencies
├── Makefile                   # Build automation and common commands
├── README.md                  # Project documentation
├── .env.example               # Environment template
├── .env                       # Local environment (not in git)
└── .gitignore                 # Git ignore patterns
```

## Agent Architecture

### Individual Agent Files
- Each agent has specialized tools and instructions
- Agents communicate through the Strands framework
- All agents are defined in `property_pilot_agents.py`

### Deployment Structure
- **Individual Services**: Each agent can run as separate service (ports 8081-8084)
- **Main Service**: Unified service orchestrating all agents (port 8080)
- **Docker Images**: Separate Dockerfiles for each agent plus main service

## Testing Organization

```
test_agents.py              # Main agent testing suite
test_automated_research.py  # Web research testing
test_agentcore_benefits.py  # AgentCore-specific testing
```

## Deployment Scripts

```
deploy.sh                   # Standard AWS deployment
deploy_agentcore.sh        # Enhanced AgentCore deployment with observability
```

## Docker Configuration

```
Dockerfile.main            # Main service container
Dockerfile.property-scout  # Property Scout agent
Dockerfile.market-analyzer # Market Analyzer agent  
Dockerfile.deal-evaluator  # Deal Evaluator agent
Dockerfile.investment-manager # Investment Manager agent
```

## Code Organization Patterns

### Agent Definition Pattern
- Each agent created with `create_*_agent()` function
- Tools defined with `@tool` decorator
- Instructions as docstrings in agent creation

### Service Pattern
- AgentCore entrypoint with `@app.entrypoint` decorator
- Session management for user context
- Error handling with structured responses

### Testing Pattern
- Local testing before deployment
- Bedrock testing for deployed agents
- Performance testing for load validation

## File Naming Conventions

- Snake_case for Python files
- Descriptive names indicating purpose
- Agent-specific files prefixed with agent type
- Test files prefixed with `test_`
- Deployment files suffixed with `_deployment` or `.sh`