# PropertyPilot Test Suite

## 🧪 Test Organization

This directory contains all tests for PropertyPilot with Google Gemini integration.

### Core Tests

- **`test_gemini_integration.py`** - Basic Google Gemini API integration test
- **`test_strands_gemini.py`** - Strands framework with Gemini integration test
- **`test_agents_functionality.py`** - Complete PropertyPilot agents functionality test
- **`test_tools_only.py`** - Individual tool functionality tests (no AI required)

### Integration Tests

- **`test_zillow_integration.py`** - Zillow API integration via HasData
- **`test_core_functionality.py`** - Core system functionality
- **`test_automated_research.py`** - Web research capabilities
- **`test_local_service.py`** - Local service testing

### Infrastructure Tests

- **`test_aws_setup.py`** - AWS configuration and credentials
- **`test_agentcore_benefits.py`** - AgentCore capabilities testing
- **`test_agents.py`** - Legacy agent tests

## 🚀 Running Tests

### Run All Tests
```bash
# From project root
python run_tests.py
```

### Run Individual Tests
```bash
# Run specific test
python tests/test_gemini_integration.py

# Run tools test (no API keys needed)
python tests/test_tools_only.py

# Run agents test (requires GEMINI_API_KEY)
python tests/test_agents_functionality.py
```

### Prerequisites

1. **Environment Variables**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   AWS_REGION=us-west-2
   HASDATA_API_KEY=2e36da63-82a5-488b-ba4a-f93c79800e53
   ```

2. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Test Results

The test runner generates:
- Console output with real-time results
- JSON report with detailed results
- Summary statistics and timing

### Expected Results

✅ **All tests should pass** for a successful deployment:
- Gemini integration working
- All PropertyPilot tools functional
- Agents responding correctly
- APIs accessible

## 🔧 Test Configuration

Tests are designed to:
- Work with free/demo API keys where possible
- Provide meaningful error messages
- Run independently without dependencies
- Complete within reasonable time limits (5 minutes max)

## 📝 Adding New Tests

To add a new test:
1. Create `test_[feature].py` in this directory
2. Follow the existing test patterns
3. Add to the test suite in `../run_tests.py`
4. Update this README