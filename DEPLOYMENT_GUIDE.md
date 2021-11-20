# Vercel Deployment Guide for ACO TSP Visualizer

## Overview

This guide walks you through deploying the Advanced Ant Colony Optimization TSP Visualizer to Vercel with a custom subdomain `tsp.samuelanari-rsg.com`.

---

## Prerequisites

### 1. Accounts & Access

- **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
- **GitHub Account**: Repository access for deployment
- **Namecheap Account**: Access to `samuelanari-rsg.com` DNS settings

### 2. Required Tools

- **Git**: Version control
- **Vercel CLI** (optional but recommended):
  ```bash
  npm install -g vercel
  ```

---

## Step 1: Prepare the Repository

### Files Created for Vercel Deployment

The following files have been added to enable Vercel deployment:

#### 1. `vercel.json` - Vercel Configuration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/socket.io/(.*)",
      "dest": "wsgi.py"
    },
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
```

**Purpose**:
- Configures Vercel to use Python runtime
- Routes all requests (including WebSocket) to the WSGI application
- Sets production environment variables

#### 2. `wsgi.py` - WSGI Entry Point
```python
from app import app, socketio

application = app

if __name__ == "__main__":
    socketio.run(app, debug=False)
```

**Purpose**:
- Provides the WSGI application object Vercel expects
- Maintains SocketIO compatibility

#### 3. `.vercelignore` - Deployment Exclusions
```
venv/
__pycache__/
*.pyc
node_modules/
aco-explorer-main/
tests/
.git/
```

**Purpose**:
- Excludes unnecessary files from deployment
- Reduces deployment size
- Speeds up build time

---

## Step 2: Push Changes to GitHub

### Commit the Vercel Configuration Files

```bash
cd "c:\Users\Samuel O. Anari\Downloads\files"

# Add all Vercel configuration files
git add vercel.json wsgi.py .vercelignore DEPLOYMENT_GUIDE.md

# Commit with message
git commit -m "Add Vercel deployment configuration

- Add vercel.json for Vercel platform configuration
- Add wsgi.py as WSGI entry point
- Add .vercelignore to exclude unnecessary files
- Add deployment documentation"

# Push to GitHub
git push origin master
```

---

## Step 3: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Login to Vercel**
   - Go to [vercel.com/dashboard](https://vercel.com/dashboard)
   - Sign in with your GitHub account

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Choose `SI_ant-colony-optimization-tsp` repository
   - Click "Import"

3. **Configure Project**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: Leave empty (Python apps don't need build)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables** (Optional)
   - Add any environment variables if needed
   - For this project, none are required

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (2-3 minutes)
   - You'll get a URL like: `https://si-ant-colony-optimization-tsp.vercel.app`

### Option B: Deploy via Vercel CLI

```bash
# Login to Vercel
vercel login

# Navigate to project directory
cd "c:\Users\Samuel O. Anari\Downloads\files"

# Deploy to production
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name: aco-tsp-visualizer
# - Directory: ./
# - Override settings? No
```

---

## Step 4: Configure Custom Domain (tsp.samuelanari-rsg.com)

### Part A: Add Domain in Vercel

1. **Navigate to Project Settings**
   - Open your deployed project in Vercel dashboard
   - Go to "Settings" → "Domains"

2. **Add Custom Domain**
   - Click "Add"
   - Enter: `tsp.samuelanari-rsg.com`
   - Click "Add"

3. **Note the DNS Records**
   - Vercel will show you the required DNS configuration
   - Typically one of these:
     - **CNAME Record**: `cname.vercel-dns.com`
     - **A Record**: `76.76.21.21`
     - **AAAA Record**: `2606:4700:10::6816:1515`

### Part B: Configure DNS in Namecheap

1. **Login to Namecheap**
   - Go to [namecheap.com](https://www.namecheap.com)
   - Login to your account

2. **Access Domain Settings**
   - Click "Domain List" in the sidebar
   - Find `samuelanari-rsg.com`
   - Click "Manage"

3. **Configure DNS**
   - Go to "Advanced DNS" tab
   - Click "Add New Record"

4. **Add CNAME Record** (Recommended Method)
   - **Type**: CNAME Record
   - **Host**: `tsp`
   - **Value**: `cname.vercel-dns.com`
   - **TTL**: Automatic
   - Click "Save Changes"

   **Alternative: A Record Method**
   - **Type**: A Record
   - **Host**: `tsp`
   - **Value**: `76.76.21.21` (Vercel's IP)
   - **TTL**: Automatic
   - Click "Save Changes"

5. **Wait for DNS Propagation**
   - DNS changes can take 5 minutes to 48 hours
   - Usually propagates within 15-30 minutes
   - Check status: [dnschecker.org](https://dnschecker.org)

### Part C: Verify in Vercel

1. **Check Domain Status**
   - Return to Vercel dashboard → Settings → Domains
   - Status should change from "Pending" to "Valid"
   - May take a few minutes after DNS propagation

2. **SSL Certificate**
   - Vercel automatically provisions SSL certificate
   - Your site will be available at `https://tsp.samuelanari-rsg.com`
   - Certificate is free and auto-renews

---

## Step 5: Verify Deployment

### Test the Application

1. **Access the Website**
   ```
   https://tsp.samuelanari-rsg.com
   ```

2. **Test Features**
   - ✅ Canvas loads and displays correctly
   - ✅ Generate random cities button works
   - ✅ Start optimization runs algorithm
   - ✅ Real-time updates appear (WebSocket working)
   - ✅ World map toggle functions
   - ✅ Zoom and pan controls work
   - ✅ Start/End city indicators appear
   - ✅ Hamiltonian cycle arrows display

3. **Check Browser Console**
   - Open Developer Tools (F12)
   - Console tab should show no errors
   - Network tab should show successful WebSocket connection

4. **Test WebSocket Connection**
   - Watch for Socket.IO connection messages
   - Should see: `Transport: websocket` or `Transport: polling`
   - No connection errors

---

## Troubleshooting

### Issue 1: 404 Not Found

**Symptoms**: Page shows "404: NOT_FOUND"

**Solutions**:
1. Check `vercel.json` routes are correct
2. Ensure `wsgi.py` is in root directory
3. Verify deployment logs in Vercel dashboard
4. Re-deploy: `vercel --prod --force`

### Issue 2: WebSocket Connection Failed

**Symptoms**: Real-time updates don't work

**Solutions**:
1. Check browser console for WebSocket errors
2. Verify Socket.IO routes in `vercel.json`
3. Ensure CORS is enabled in `app.py`:
   ```python
   socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
   ```
4. Note: Vercel serverless functions have limitations with WebSockets
   - May need to use polling transport as fallback
   - Socket.IO automatically handles this

### Issue 3: Domain Not Resolving

**Symptoms**: `tsp.samuelanari-rsg.com` doesn't load

**Solutions**:
1. Verify DNS records in Namecheap:
   ```bash
   nslookup tsp.samuelanari-rsg.com
   ```
2. Check DNS propagation: [dnschecker.org](https://dnschecker.org)
3. Wait 30 minutes for propagation
4. Ensure CNAME points to `cname.vercel-dns.com`
5. Check Vercel domain status (Settings → Domains)

### Issue 4: SSL Certificate Pending

**Symptoms**: HTTPS doesn't work, shows "Not Secure"

**Solutions**:
1. Wait 5-10 minutes for Vercel to provision certificate
2. Ensure domain status is "Valid" in Vercel
3. Check DNS is properly configured
4. Force refresh: Vercel → Settings → Domains → Refresh

### Issue 5: Python Dependencies Failed

**Symptoms**: Build fails with import errors

**Solutions**:
1. Verify `requirements.txt` exists
2. Check all dependencies are compatible with Vercel's Python runtime
3. Review build logs in Vercel dashboard
4. Ensure NumPy version is compatible:
   ```
   numpy==1.26.2
   ```

### Issue 6: Template Not Found

**Symptoms**: "TemplateNotFound: index.html"

**Solutions**:
1. Ensure `templates/index.html` exists
2. Verify folder structure is correct:
   ```
   .
   ├── wsgi.py
   ├── app.py
   ├── templates/
   │   └── index.html
   └── requirements.txt
   ```
3. Check `.vercelignore` doesn't exclude templates
4. Re-deploy with fresh build

---

## Vercel Deployment Architecture

### How Vercel Handles Python Apps

```
User Request (https://tsp.samuelanari-rsg.com)
         ↓
Vercel Edge Network (CDN + SSL)
         ↓
Serverless Function (Python Runtime)
         ↓
wsgi.py → app.py → Flask Application
         ↓
Response (HTML + WebSocket upgrade)
```

### Key Characteristics

1. **Serverless Functions**
   - Each request spawns a serverless function
   - Cold start: ~1-2 seconds (first request)
   - Warm: <100ms (subsequent requests)

2. **WebSocket Support**
   - Limited support in serverless environment
   - Socket.IO handles fallback to long-polling
   - Real-time updates work but may use polling

3. **Automatic Scaling**
   - Scales automatically with traffic
   - No manual server management
   - Pay only for actual usage

4. **Global CDN**
   - Static assets cached at edge
   - Low latency worldwide
   - Automatic HTTPS

---

## Cost Estimate

### Vercel Free Tier (Hobby Plan)

**Included Free**:
- ✅ 100 GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Unlimited custom domains
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments

**Limits**:
- 100 GB bandwidth (sufficient for demo/portfolio)
- 100 hours serverless function execution time/month
- Typical ACO TSP usage: <1 hour/month

**Estimated Cost**: $0/month (within free tier)

### Namecheap Domain

**Already Owned**: `samuelanari-rsg.com`
- No additional cost for subdomain
- DNS management included

**Total Estimated Cost**: $0/month

---

## Performance Optimization Tips

### 1. Enable Compression

Add to `app.py`:
```python
from flask_compress import Compress
compress = Compress(app)
```

Add to `requirements.txt`:
```
flask-compress==1.14
```

### 2. Cache Static Assets

Vercel automatically caches:
- Images
- CSS files
- JavaScript files
- Any files in `static/` folder

### 3. Optimize NumPy Operations

Already implemented:
- Vectorized operations
- Pre-allocated arrays
- Efficient matrix calculations

### 4. WebSocket Optimization

In `app.py`:
```python
# Configure Socket.IO for production
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)
```

---

## Monitoring & Analytics

### Vercel Analytics (Optional)

1. **Enable Analytics**
   - Vercel Dashboard → Project → Analytics
   - Free tier includes basic analytics
   - Tracks: Page views, unique visitors, top pages

2. **Real-Time Logs**
   - Vercel Dashboard → Deployments → Select deployment → Logs
   - View function execution logs
   - Debug errors in production

### Error Tracking

Add to `app.py`:
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server Error: {error}")
    return "Internal Server Error", 500
```

---

## Continuous Deployment

### Automatic Deployments

Vercel automatically deploys when you push to GitHub:

1. **Production Deployments**
   - Push to `master` branch
   - Automatically deploys to `tsp.samuelanari-rsg.com`

2. **Preview Deployments**
   - Push to any other branch
   - Gets unique preview URL
   - Test before merging to master

### Manual Deployment

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel

# Rollback to previous deployment
vercel rollback
```

---

## Security Best Practices

### 1. Environment Variables

Store sensitive data as Vercel environment variables:
```bash
# Via CLI
vercel env add SECRET_KEY production

# Via Dashboard
Settings → Environment Variables → Add
```

### 2. CORS Configuration

Update for production in `app.py`:
```python
# Development
CORS(app, origins="*")

# Production (recommended)
CORS(app, origins=["https://tsp.samuelanari-rsg.com"])
```

### 3. Rate Limiting

Add Flask-Limiter:
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## Maintenance

### Update Application

```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push origin master

# Vercel automatically deploys
# Check deployment status in dashboard
```

### Monitor Deployments

```bash
# Via CLI
vercel ls

# Check deployment logs
vercel logs <deployment-url>
```

### Domain Management

- Renew `samuelanari-rsg.com` annually in Namecheap
- Vercel SSL certificates auto-renew
- No manual certificate management needed

---

## Support & Resources

### Official Documentation

- **Vercel Python**: [vercel.com/docs/functions/serverless-functions/runtimes/python](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- **Custom Domains**: [vercel.com/docs/custom-domains](https://vercel.com/docs/custom-domains)
- **Flask on Vercel**: [vercel.com/guides/using-flask-with-vercel](https://vercel.com/guides/using-flask-with-vercel)

### Community

- Vercel Discord: [vercel.com/discord](https://vercel.com/discord)
- GitHub Discussions: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)

### DNS Tools

- DNS Checker: [dnschecker.org](https://dnschecker.org)
- What's My DNS: [whatsmydns.net](https://whatsmydns.net)
- DNS Lookup: [mxtoolbox.com](https://mxtoolbox.com/DNSLookup.aspx)

---

## Quick Reference Commands

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy to production
vercel --prod

# View deployments
vercel ls

# View logs
vercel logs

# Open project in browser
vercel open

# Remove deployment
vercel rm <deployment-name>

# Check DNS
nslookup tsp.samuelanari-rsg.com

# Check project status
vercel inspect <deployment-url>
```

---

## Checklist

### Pre-Deployment
- [x] Create `vercel.json`
- [x] Create `wsgi.py`
- [x] Create `.vercelignore`
- [x] Verify `requirements.txt` is complete
- [ ] Test locally one more time
- [ ] Commit and push to GitHub

### Deployment
- [ ] Import project to Vercel
- [ ] Configure build settings
- [ ] Deploy to production
- [ ] Verify deployment URL works

### Custom Domain
- [ ] Add domain in Vercel
- [ ] Note DNS records from Vercel
- [ ] Add CNAME record in Namecheap
- [ ] Wait for DNS propagation (15-30 min)
- [ ] Verify SSL certificate

### Testing
- [ ] Test all features on production URL
- [ ] Verify WebSocket connection works
- [ ] Test on multiple devices/browsers
- [ ] Check browser console for errors
- [ ] Test world map zoom/pan
- [ ] Run complete ACO optimization

### Post-Deployment
- [ ] Update README with live URL
- [ ] Share demo link
- [ ] Monitor analytics
- [ ] Set up error tracking (optional)

---

## Next Steps After Deployment

1. **Update README.md**
   ```markdown
   ## Live Demo

   Visit the live application: [https://tsp.samuelanari-rsg.com](https://tsp.samuelanari-rsg.com)
   ```

2. **Share Your Work**
   - Add to portfolio
   - Share on LinkedIn
   - Include in resume
   - Showcase on GitHub profile

3. **Consider Enhancements**
   - Add Google Analytics
   - Implement user accounts
   - Add more algorithms
   - Create API documentation

---

## Summary

**Deployment URL**: `https://tsp.samuelanari-rsg.com`

**Key Files**:
- `vercel.json` - Vercel configuration
- `wsgi.py` - WSGI entry point
- `.vercelignore` - Exclude files

**DNS Configuration**:
- **Type**: CNAME
- **Host**: tsp
- **Value**: cname.vercel-dns.com

**Estimated Time**:
- GitHub push: 2 minutes
- Vercel deployment: 3-5 minutes
- DNS propagation: 15-30 minutes
- **Total**: ~20-40 minutes

---

**Last Updated**: 2025-11-18
**Deployment Platform**: Vercel
**Custom Domain**: tsp.samuelanari-rsg.com
**Cost**: $0/month (free tier)
