# Deployment Guide for Retention Demo API

## Repository Information
- **GitHub Repository**: https://github.com/mattsun23/soccer
- **Status**: ✅ Public (accessible for deployment)

## Prerequisites
Before deploying, ensure you have:
1. WatsonX API credentials
2. Resend API key
3. Access to Railway or IBM Code Engine

---

## Option 1: Deploy to Railway

### Step 1: Push Latest Changes to GitHub
```bash
cd retention-demo-api
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 2: Deploy on Railway
1. Go to [Railway.app](https://railway.app/)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose repository: `mattsun23/soccer`
5. Railway will auto-detect the Dockerfile

### Step 3: Configure Environment Variables
In Railway dashboard, add these environment variables:
```
WATSONX_API_KEY=MvDGviPn3j1InmYgYe-0E9YD-_ezMAIiuCjJLGnSAfcU
WATSONX_PROJECT_ID=fe2f56aa-2731-4076-b726-2d1a2766455b
WATSONX_URL=https://us-south.ml.cloud.ibm.com
RESEND_API_KEY=re_izPKbjMp_9aU3pk4LQYJoauQGFDnpgivF
```

### Step 4: Deploy
- Railway will automatically build and deploy
- You'll get a public URL like: `https://your-app.railway.app`

---

## Option 2: Deploy to IBM Code Engine

### Step 1: Install IBM Cloud CLI
```bash
# If not already installed
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
```

### Step 2: Login to IBM Cloud
```bash
ibmcloud login --sso
ibmcloud target -r us-south
```

### Step 3: Create Code Engine Project (if needed)
```bash
ibmcloud ce project create --name retention-api
ibmcloud ce project select --name retention-api
```

### Step 4: Deploy from GitHub
```bash
ibmcloud ce application create \
  --name retention-demo-api \
  --build-source https://github.com/mattsun23/soccer \
  --build-context-dir retention-demo-api \
  --strategy dockerfile \
  --port 8000 \
  --min-scale 1 \
  --max-scale 3 \
  --cpu 0.5 \
  --memory 1G \
  --env WATSONX_API_KEY=MvDGviPn3j1InmYgYe-0E9YD-_ezMAIiuCjJLGnSAfcU \
  --env WATSONX_PROJECT_ID=fe2f56aa-2731-4076-b726-2d1a2766455b \
  --env WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  --env RESEND_API_KEY=re_izPKbjMp_9aU3pk4LQYJoauQGFDnpgivF
```

### Step 5: Get Application URL
```bash
ibmcloud ce application get --name retention-demo-api
```

---

## Option 3: Deploy Using Docker (Manual)

### Build and Push to Container Registry
```bash
cd retention-demo-api

# Build image
docker build -t retention-demo-api:latest .

# Tag for registry (example: Docker Hub)
docker tag retention-demo-api:latest yourusername/retention-demo-api:latest

# Push to registry
docker push yourusername/retention-demo-api:latest
```

Then deploy the image to Railway or Code Engine using the registry URL.

---

## Troubleshooting

### Issue: "Repository not found" or "Not public"
**Solution**: The repository is already public. Make sure you're using the correct URL:
- ✅ Correct: `https://github.com/mattsun23/soccer`
- ❌ Wrong: `https://github.com/mattsun23/retention-demo-api`

### Issue: Build fails on Railway/Code Engine
**Possible causes**:
1. **Missing Dockerfile**: ✅ Already present
2. **Wrong context directory**: For Code Engine, use `--build-context-dir retention-demo-api`
3. **Port mismatch**: Ensure PORT environment variable is set (Railway does this automatically)

### Issue: Application starts but crashes
**Check**:
1. Environment variables are set correctly
2. WatsonX credentials are valid
3. Check logs: `ibmcloud ce application logs --name retention-demo-api`

### Issue: .env file not loading
**Note**: The Dockerfile copies `.env` file, but for production:
- ⚠️ **DO NOT** commit `.env` to git (it's in `.gitignore`)
- ✅ **DO** set environment variables in Railway/Code Engine dashboard
- The app will use platform environment variables over `.env` file

---

## Testing Deployment

Once deployed, test the endpoints:

```bash
# Replace YOUR_URL with your deployment URL
export API_URL="https://your-app.railway.app"

# Health check
curl $API_URL/health

# Send batch emails
curl -X POST $API_URL/send-retention-emails

# Send single email
curl -X POST $API_URL/send-single-email/matt.acosta@ibm.com
```

---

## Security Notes

⚠️ **IMPORTANT**: Your `.env` file contains sensitive credentials:
- WatsonX API Key
- Resend API Key

**Recommendations**:
1. ✅ `.env` is already in `.gitignore` - good!
2. ✅ Use platform environment variables for production
3. 🔄 Consider rotating API keys after deployment
4. 🔒 Restrict API access using Railway/Code Engine authentication

---

## Next Steps

1. **Push changes to GitHub**:
   ```bash
   cd retention-demo-api
   git add railway.json DEPLOYMENT.md
   git commit -m "Add deployment configuration and guide"
   git push origin main
   ```

2. **Choose deployment platform** (Railway or Code Engine)

3. **Follow the steps above** for your chosen platform

4. **Test the deployed API**

5. **Monitor logs and performance**

---

## Support

- Railway Docs: https://docs.railway.app/
- IBM Code Engine Docs: https://cloud.ibm.com/docs/codeengine
- GitHub Repository: https://github.com/mattsun23/soccer