# PropertyPilot API Integration Guide

PropertyPilot now uses **real APIs only** - no mock data. This guide explains how to configure and use all integrated APIs.

## 🔑 Required API Keys (FREE ONLY)

### 1. Zillow Data (HasData Service)
- **API**: HasData Zillow Scraping API
- **Key**: `HASDATA_API_KEY=2e36da63-82a5-488b-ba4a-f93c79800e53`
- **Usage**: Property details, market data, agent information
- **Endpoint**: `https://api.hasdata.com/scrape/zillow/property`
- **Cost**: FREE (provided key)

### 2. US Census Bureau
- **API**: US Census Bureau API
- **Key**: `CENSUS_API_KEY=ea42819f6babc899faf5359311120ee0e706fadd`
- **Usage**: Demographics, income, education, housing data
- **Signup**: https://api.census.gov/data/key_signup.html
- **Cost**: FREE (unlimited)

### 3. AWS Services (Optional)
- **DynamoDB**: Property data storage
- **Cognito**: User authentication
- **AgentCore**: Runtime and memory services
- **Cost**: Pay-per-use (AWS Free Tier available)

## 📊 Data Sources by Feature

### Property Discovery
- **Primary**: HasData Zillow API
- **Data**: Property listings, prices, details, agent info
- **Format**: JSON with comprehensive property data

### Demographics & Market Analysis
- **Primary**: US Census Bureau API (FREE)
- **Secondary**: Public economic estimates
- **Data**: Income, population, education, general economic indicators

### Neighborhood Scoring
- **Census**: Demographics and housing data (FREE)
- **Public Sources**: Basic school and safety estimates (FREE)
- **Calculated**: Composite neighborhood desirability score

### Market Trends
- **Public Data**: General economic indicators
- **Estimates**: Current market conditions based on public information
- **Analysis**: Market sentiment and investment outlook

## 🛠️ API Integration Details

### HasData Zillow Integration
```python
# Get property details
property_details = zillow_client.get_property_details(zillow_url)

# Returns comprehensive data:
{
    "zpid": "property_id",
    "address": "full_address",
    "price": 450000,
    "zestimate": 465000,
    "rentZestimate": 2800,
    "bedrooms": 3,
    "bathrooms": 2,
    "livingArea": 1800,
    "lotSize": 0.25,
    "yearBuilt": 2015,
    "priceHistory": [...],
    "taxHistory": [...],
    "schools": [...],
    "neighborhood": "...",
    "walkScore": 75,
    "agentInfo": {...},
    "listingAgentEmails": [...]
}
```

### Census Bureau Integration
```python
# Get demographic data
census_data = census_client.get_demographic_data("Austin, TX")

# Returns real Census data:
{
    "median_income": 75000,
    "population": 965000,
    "median_home_value": 450000,
    "homeownership_rate": 65.2,
    "education_rate": 45.8,
    "total_commuters": 450000
}
```

### Neighborhood Scoring Algorithm
```python
# Multi-factor scoring using real data
scores = {
    "income_score": (median_income / 70000) * 7.5,      # 25% weight
    "education_score": (education_rate / 35) * 10,      # 20% weight  
    "school_score": greatschools_rating,                # 25% weight
    "safety_score": crime_safety_score,                 # 20% weight
    "housing_score": (homeownership_rate / 70) * 10     # 10% weight
}
overall_score = weighted_average(scores)
```

## 🚀 Setup Instructions

### 1. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

### 2. API Key Setup (Already Configured)

**Census Bureau (FREE - Already Set)**
- Key already provided: `ea42819f6babc899faf5359311120ee0e706fadd`
- No additional setup required
- Unlimited free access to US demographic data

**HasData Zillow (FREE - Already Set)**
- Key already provided: `2e36da63-82a5-488b-ba4a-f93c79800e53`
- No additional setup required
- Access to real Zillow property data

### 3. AWS Configuration
```bash
# Configure AWS credentials
aws configure

# Set region
export AWS_REGION=us-east-1
```

### 4. DynamoDB Table Setup
```bash
# Create PropertyPilot table
aws dynamodb create-table \
    --table-name PropertyPilot-Properties \
    --attribute-definitions AttributeName=PropertyId,AttributeType=S \
    --key-schema AttributeName=PropertyId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

## 📈 Usage Examples

### Complete Property Analysis
```python
# Initialize PropertyPilot with real APIs
property_pilot = PropertyPilotSystem()

# Analyze using real Zillow data
result = await property_pilot.analyze_property_investment(
    location="Austin, TX",
    max_price=500000
)

# Get detailed property analysis
zillow_url = "https://www.zillow.com/homedetails/..."
analysis = analyze_zillow_investment_opportunity(zillow_url, target_roi=8.0)
```

### Market Research with Real Data
```python
# Get real Census demographics
demographics = get_census_data("Austin, TX")

# Calculate neighborhood score using multiple APIs
neighborhood_score = calculate_neighborhood_score("Austin, TX")

# Get economic trends
market_trends = get_market_trends("Austin, TX")
```

## 🔍 Data Quality & Reliability

### Data Sources Reliability
- **Census Bureau**: Official government data, highly reliable
- **Zillow (HasData)**: Real-time property data, market estimates
- **Alpha Vantage**: Financial data from Federal Reserve, BLS
- **GreatSchools**: Crowdsourced + official school data

### Error Handling
- All APIs have proper error handling
- Failed API calls return empty results (no mock data)
- Comprehensive logging for debugging
- Graceful degradation when APIs unavailable

### Rate Limits (FREE APIs Only)
- **Census**: No official limit (FREE)
- **HasData**: Based on provided key
- **Public Data**: No limits on estimates and public sources

## 🎯 Benefits of Real API Integration

### Accurate Investment Analysis
- Real property prices and Zestimates
- Actual rental market data
- Current economic conditions
- Verified demographic information

### Data-Driven Decisions
- No assumptions or estimates
- Current market conditions
- Real neighborhood metrics
- Actual school ratings and crime data

### Professional Grade Analysis
- Institutional-quality data sources
- Comprehensive market research
- Reliable investment metrics
- Audit trail of data sources

## 🔧 Troubleshooting

### Common Issues

**API Key Not Working**
- Verify key is correct in `.env` file
- Check API key permissions and limits
- Ensure proper environment variable loading

**No Data Returned**
- Check API rate limits
- Verify location format (City, State)
- Check API service status
- Review logs for specific errors

**DynamoDB Access Issues**
- Verify AWS credentials
- Check IAM permissions
- Ensure table exists and is accessible
- Verify region configuration

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python property_pilot_agents.py
```

## 📞 Support

For API-specific issues:
- **Census Bureau**: https://www.census.gov/data/developers/guidance.html
- **HasData**: Check your account dashboard

For PropertyPilot integration issues, check the logs and ensure all environment variables are properly configured.