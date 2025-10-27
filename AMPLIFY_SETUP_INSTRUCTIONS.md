# AWS Amplify Setup Instructions

## 🚀 Connect GitHub Repository to AWS Amplify

### Step 1: Go to AWS Amplify Console
Open: https://console.aws.amazon.com/amplify/

### Step 2: Create New App
1. Click "New app" → "Host web app"
2. Choose "GitHub" as the source
3. Click "Continue"

### Step 3: Authorize GitHub
1. Click "Authorize AWS Amplify"
2. Grant permissions to access your repositories

### Step 4: Select Repository
1. Repository: `AbinjithTK/PropertyPilot.git`
2. Branch: `main` (or `master`)
3. Click "Next"

### Step 5: Configure Build Settings
1. App name: `PropertyPilot-RealEstate-Platform`
2. Environment name: `production`
3. Build settings should auto-detect from `amplify.yml`
4. Click "Next"

### Step 6: Review and Deploy
1. Review all settings
2. Click "Save and deploy"
3. Wait 2-3 minutes for deployment

### Step 7: Get Your URL
After deployment, you'll get a URL like:
```
https://main.d1234567890.amplifyapp.com
```

## 🎯 What Happens Next

✅ **Automatic Deployments** - Every push to GitHub triggers a new deployment
✅ **Global CDN** - Your site is served from 200+ edge locations worldwide
✅ **SSL Certificate** - Automatic HTTPS with valid SSL certificate
✅ **Custom Domain** - Add your own domain name (optional)
✅ **Branch Deployments** - Deploy different branches to different URLs

## 🔧 Post-Deployment Configuration

1. **Open Your Amplify URL**
2. **Configure AgentCore Endpoint** in the website interface
3. **Test Real Estate Analysis** with sample queries
4. **Share with Investors** - Your platform is ready!

## 📊 Monitoring

Monitor your deployment:
- **Amplify Console**: https://console.aws.amazon.com/amplify/
- **Build Logs**: Check deployment status and logs
- **Analytics**: Built-in visitor analytics
- **Performance**: Monitor load times and errors

## 🌐 Custom Domain (Optional)

To add a custom domain:
1. In Amplify Console, go to "Domain management"
2. Click "Add domain"
3. Enter your domain (e.g., propertypilot.com)
4. Follow DNS configuration steps
5. SSL certificate is automatically provisioned

## 💰 Cost Estimate

For a real estate investment platform:
- **Small usage** (< 1,000 visitors/month): ~$5-15/month
- **Medium usage** (< 10,000 visitors/month): ~$25-50/month
- **Large usage** (< 100,000 visitors/month): ~$100-200/month

Includes hosting, CDN, SSL, and auto-scaling.

## 🔄 Updates

To update your website:
1. Make changes to your files
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update PropertyPilot platform"
   git push
   ```
3. Amplify automatically deploys the changes

## 🆘 Troubleshooting

**Build Failures:**
- Check build logs in Amplify Console
- Verify `amplify.yml` configuration
- Ensure all required files are in repository

**AgentCore Connection Issues:**
- Verify endpoint URL format
- Check AWS credentials and permissions
- Test endpoint manually

---

🎉 **Your PropertyPilot real estate investment platform is ready to serve professional investors worldwide!**

Repository: https://github.com/AbinjithTK/PropertyPilot.git
