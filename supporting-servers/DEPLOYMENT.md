# Railway Deployment Guide

This guide will help you deploy the Supporting Services application to Railway.

## Prerequisites

- A [Railway account](https://railway.app/) (free tier available)
- Your code in a Git repository (GitHub, GitLab, or Bitbucket)
- OR Railway CLI installed locally

## Quick Deploy (GitHub)

This is the easiest method:

1. **Push your code to GitHub** (if not already there)
   ```bash
   git add .
   git commit -m "Add Railway deployment config"
   git push
   ```

2. **Go to Railway**
   - Visit [railway.app](https://railway.app/)
   - Sign in with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `supporting-servers` directory (if it's a monorepo)

3. **Wait for deployment**
   - Railway will automatically detect the configuration
   - Build and deployment logs will be shown
   - Once complete, you'll get a URL (e.g., `https://your-app.railway.app`)

4. **Access your application**
   - Main page: `https://your-app.railway.app/`
   - Health check: `https://your-app.railway.app/health`
   - Email docs: `https://your-app.railway.app/email/docs`
   - ERP docs: `https://your-app.railway.app/erp/docs`
   - Payment docs: `https://your-app.railway.app/payment/docs`

## Deploy with Railway CLI

If you prefer command-line deployment:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Navigate to the supporting-servers directory**
   ```bash
   cd supporting-servers
   ```

4. **Initialize Railway project**
   ```bash
   railway init
   ```
   - Select "Create a new project"
   - Give it a name (e.g., "supporting-services")

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get your deployment URL**
   ```bash
   railway domain
   ```
   Or open directly in browser:
   ```bash
   railway open
   ```

## Configuration Files

The following files enable Railway deployment:

### `Procfile`
Tells Railway how to start the application:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### `railway.json`
Railway-specific configuration with:
- Build settings (using Nixpacks)
- Health check endpoint (`/health`)
- Restart policy
- Start command

### `runtime.txt`
Specifies Python version:
```
python-3.11
```

### `.railwayignore`
Excludes unnecessary files from deployment (similar to `.gitignore`)

## Environment Variables

The application automatically uses Railway's `PORT` environment variable. No additional configuration needed!

### Optional: Setting BASE_URL for Swagger Documentation

To display the correct hosting domain in Swagger/OpenAPI documentation instead of just relative paths:

**Via Railway Dashboard:**
1. Go to your project
2. Click on your service
3. Go to "Variables" tab
4. Add variable: `BASE_URL` = `https://your-app.railway.app` (replace with your actual Railway URL)
5. Redeploy the service

**Via Railway CLI:**
```bash
railway variables set BASE_URL=https://your-app.railway.app
```

This will update the Swagger docs server URLs from just `/payment`, `/erp`, `/email` to include the full domain like `https://your-app.railway.app/payment`.

If not set, the documentation will default to `http://localhost:8000` which works fine for local development.

### Other Environment Variables

If you need to add other environment variables (e.g., API keys):

**Via Railway Dashboard:**
1. Go to your project
2. Click on your service
3. Go to "Variables" tab
4. Add your variables

**Via Railway CLI:**
```bash
railway variables set KEY=value
```

## Monitoring

### View Logs
**Dashboard:**
- Go to your project → Service → "Deployments" tab
- Click on any deployment to see logs

**CLI:**
```bash
railway logs
```

### Health Check
The application provides a health check endpoint at `/health`:
```bash
curl https://your-app.railway.app/health
```

Response:
```json
{
  "status": "healthy",
  "services": {
    "email": {"status": "running", "docs": "/email/docs"},
    "erp": {"status": "running", "docs": "/erp/docs"},
    "payment": {"status": "running", "docs": "/payment/docs"}
  }
}
```

## Troubleshooting

### Deployment fails
- Check build logs in Railway dashboard
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility

### Application not responding
- Check application logs: `railway logs`
- Verify the health check endpoint
- Ensure the PORT environment variable is being used

### Port issues
The application must bind to `0.0.0.0` and use Railway's `PORT` environment variable. This is already configured in `main.py`:
```python
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

## Updating Your Deployment

### With GitHub (Automatic)
Once connected, Railway automatically deploys on every push to your main branch:
```bash
git add .
git commit -m "Update application"
git push
```

### With CLI
```bash
railway up
```

## Rollback

If something goes wrong:

**Via Dashboard:**
1. Go to "Deployments" tab
2. Find a previous successful deployment
3. Click "Redeploy"

**Via CLI:**
```bash
railway status  # View recent deployments
railway rollback  # Rollback to previous deployment
```

## Costs

Railway offers:
- **Free tier**: $5 worth of usage per month
- **Hobby plan**: $5/month for small projects
- **Pro plan**: Pay-as-you-go for production apps

Your application should fit comfortably in the free tier for development/testing.

## Custom Domain

To add a custom domain:

1. Go to your service in Railway dashboard
2. Click "Settings"
3. Scroll to "Domains"
4. Click "Add Domain"
5. Enter your custom domain
6. Add the provided DNS records to your domain provider

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app/)

---

Happy deploying! 🚀

