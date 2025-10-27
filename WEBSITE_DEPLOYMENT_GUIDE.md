# PropertyPilot Real Estate Investment Website Deployment Guide

This guide shows you how to deploy PropertyPilot as a professional real estate investment website using AWS Bedrock AgentCore.

## 🏗️ Architecture Overview

```
Real Estate Investors → Website (investor_dashboard.html) → AWS AgentCore → PropertyPilot AI Agents
```

## 📋 Prerequisites

1. **AWS Account** with Bedrock access
2. **PropertyPilot AgentCore Runtime** deployed
3. **Web hosting** (AWS S3, Netlify, Vercel, or any web server)
4. **Domain name** (optional but recommended)

## 🚀 Step 1: Deploy PropertyPilot to AgentCore

### Deploy the AgentCore Runtime

```bash
# 1. Configure your environment
cp .env.example .env
# Edit .env with your API keys

# 2. Deploy to AgentCore
python build_and_deploy.py

# 3. Note the AgentCore Runtime ARN from output
# Example: arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/propertypilot-runtime
```

### Get Your AgentCore Endpoint URL

After deployment, your endpoint will be:
```
https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{runtime-id}/invoke
```

Example:
```
https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/propertypilot-runtime/invoke
```

## 🌐 Step 2: Deploy the Website

### Option A: AWS S3 + CloudFront (Recommended)

1. **Create S3 Bucket for Website**
```bash
aws s3 mb s3://propertypilot-website-{your-unique-id}
aws s3 website s3://propertypilot-website-{your-unique-id} --index-document investor_dashboard.html
```

2. **Upload Website Files**
```bash
aws s3 cp investor_dashboard.html s3://propertypilot-website-{your-unique-id}/
aws s3 cp investor_dashboard.html s3://propertypilot-website-{your-unique-id}/index.html
```

3. **Configure Bucket Policy**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::propertypilot-website-{your-unique-id}/*"
        }
    ]
}
```

4. **Create CloudFront Distribution**
```bash
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

### Option B: Netlify (Easiest)

1. **Create netlify.toml**
```toml
[build]
  publish = "."

[[redirects]]
  from = "/*"
  to = "/investor_dashboard.html"
  status = 200
```

2. **Deploy to Netlify**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir .
```

### Option C: Vercel

1. **Create vercel.json**
```json
{
  "rewrites": [
    { "source": "/", "destination": "/investor_dashboard.html" },
    { "source": "/(.*)", "destination": "/investor_dashboard.html" }
  ]
}
```

2. **Deploy to Vercel**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

## 🔐 Step 3: Configure Authentication (Optional)

### AWS Cognito Integration

1. **Create Cognito User Pool**
```bash
aws cognito-idp create-user-pool --pool-name PropertyPilotUsers
```

2. **Create User Pool Client**
```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id us-west-2_XXXXXXXXX \
  --client-name PropertyPilotWebClient \
  --generate-secret
```

3. **Update Website with Cognito**
Add to your HTML:
```html
<script src="https://sdk.amazonaws.com/js/aws-sdk-2.1.24.min.js"></script>
<script>
// Configure Cognito
AWS.config.region = 'us-west-2';
const userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool({
    UserPoolId: 'us-west-2_XXXXXXXXX',
    ClientId: 'your-client-id'
});
</script>
```

## 🎯 Step 4: Configure the Website

### Update AgentCore Endpoint

In `investor_dashboard.html`, users will configure:

1. **AgentCore Endpoint URL**
   ```
   https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/propertypilot-runtime/invoke
   ```

2. **Authentication Token** (if using Cognito)
   ```
   Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Environment-Specific Configuration

Create different versions for different environments:

**Production (investor_dashboard.html)**
```javascript
const DEFAULT_ENDPOINT = 'https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/propertypilot-prod/invoke';
```

**Staging (investor_dashboard_staging.html)**
```javascript
const DEFAULT_ENDPOINT = 'https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/propertypilot-staging/invoke';
```

## 📊 Step 5: Add Analytics and Monitoring

### Google Analytics
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### AWS CloudWatch RUM
```html
<script>
(function (n,i,v,r,s,c,x,z){x=window.AwsRumClient={q:[],n:n,i:i,v:v,r:r,c:c};window[n]=function(c,p){x.q.push({c:c,p:p});};z=document.createElement('script');z.async=true;z.src=s;document.head.appendChild(z)})(
'cwr','your-app-id','1.0.0','us-west-2','https://client.rum.us-west-2.amazonaws.com/1.x.x/cwr.js',{sessionSampleRate:1,guestRoleArn:'arn:aws:iam::123456789012:role/RUM-Monitor-us-west-2-123456789012-role',identityPoolId:'us-west-2:12345678-1234-1234-1234-123456789012',endpoint:'https://dataplane.rum.us-west-2.amazonaws.com',telemetries:['performance','errors','http'],allowCookies:true,enableXRay:false}
);
</script>
```

## 🔒 Step 6: Security Configuration

### CORS Configuration for AgentCore

Update your AgentCore deployment to allow your website domain:

```python
# In main.py, add CORS headers
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://your-website-domain.com"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response
```

### Content Security Policy

Add to your HTML head:
```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com;
    style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com;
    connect-src 'self' https://bedrock-agentcore.*.amazonaws.com;
    font-src 'self' https://fonts.gstatic.com;
">
```

## 🎨 Step 7: Customization for Real Estate Investors

### Branding Customization

1. **Update Logo and Colors**
```css
:root {
    --primary-color: #your-brand-color;
    --secondary-color: #your-secondary-color;
}

.logo {
    background-image: url('your-logo.png');
}
```

2. **Add Your Company Information**
```html
<div class="logo">
    <img src="your-logo.png" alt="Your Company"> PropertyPilot
</div>
```

### Investment-Specific Features

1. **Add Investment Calculators**
2. **Portfolio Tracking**
3. **Market Reports**
4. **Property Comparison Tools**

## 📈 Step 8: Advanced Features

### Real-Time Updates with WebSockets

```javascript
// Add WebSocket connection for real-time updates
const ws = new WebSocket('wss://your-websocket-endpoint');
ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    updateDashboard(update);
};
```

### Progressive Web App (PWA)

Create `manifest.json`:
```json
{
    "name": "PropertyPilot Investment Platform",
    "short_name": "PropertyPilot",
    "description": "AI-Powered Real Estate Investment Analysis",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#667eea",
    "theme_color": "#667eea",
    "icons": [
        {
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        }
    ]
}
```

## 🚀 Step 9: Go Live

### Final Checklist

- [ ] AgentCore runtime deployed and tested
- [ ] Website deployed to hosting platform
- [ ] Domain configured (if using custom domain)
- [ ] SSL certificate installed
- [ ] Analytics configured
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Authentication working (if enabled)
- [ ] All features tested with real AgentCore endpoint

### Launch Commands

```bash
# Test the complete flow
curl -X POST https://your-website.com/test \
  -H "Content-Type: application/json" \
  -d '{"test": "connection"}'

# Monitor AgentCore logs
aws logs tail /aws/bedrock-agentcore/propertypilot-runtime --follow
```

## 📞 Support and Monitoring

### Monitoring Dashboard

Set up CloudWatch dashboards to monitor:
- AgentCore invocation count
- Response times
- Error rates
- Website traffic
- User engagement

### Support Channels

- **Technical Issues**: Check AgentCore logs in CloudWatch
- **API Errors**: Review AgentCore runtime status
- **Website Issues**: Check browser console and network tab

## 🎯 Success Metrics

Track these KPIs for your real estate investment platform:
- **User Engagement**: Analysis requests per user
- **Analysis Quality**: User satisfaction with AI insights
- **Conversion**: Users who act on investment recommendations
- **Performance**: Average response time for analysis
- **Reliability**: Uptime and error rates

---

Your PropertyPilot real estate investment website is now ready to serve professional investors with AI-powered property analysis!

## 🔗 Quick Links

- **Website**: `https://your-domain.com`
- **AgentCore Console**: AWS Bedrock AgentCore Console
- **Monitoring**: CloudWatch Dashboards
- **Logs**: CloudWatch Logs for debugging

**Next Steps**: Consider adding advanced features like portfolio management, automated reporting, and integration with MLS systems.