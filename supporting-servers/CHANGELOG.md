# Changelog - Swagger Server URL Configuration

## Changes Made

### Updated Files

1. **`payment_gateway.py`**
   - Added `import os`
   - Added `BASE_URL` environment variable reading
   - Updated `FastAPI()` initialization to include `servers` parameter with full URLs

2. **`erp_system.py`**
   - Added `import os`
   - Added `BASE_URL` environment variable reading
   - Updated `FastAPI()` initialization to include `servers` parameter with full URLs

3. **`email_server.py`**
   - Added `import os`
   - Added `BASE_URL` environment variable reading
   - Updated `FastAPI()` initialization to include `servers` parameter with full URLs

4. **`README.md`**
   - Added documentation for the `BASE_URL` environment variable
   - Added instructions on how to set it in Railway

5. **`DEPLOYMENT.md`**
   - Added detailed section on setting `BASE_URL` for Swagger documentation
   - Added examples for both Railway Dashboard and CLI

### What Changed in Swagger Docs

**Before:**
```json
"servers": [
  {
    "url": "/payment"
  }
]
```

**After:**
```json
"servers": [
  {
    "url": "https://your-app.railway.app/payment",
    "description": "Payment Gateway Server"
  },
  {
    "url": "http://localhost:8000/payment",
    "description": "Local Development Server"
  }
]
```

### Benefits

1. **Full URLs in Swagger**: The Swagger/OpenAPI documentation now shows complete URLs including the hosting domain
2. **Configurable**: Uses the `BASE_URL` environment variable for flexibility
3. **Works Locally and in Production**: Defaults to `localhost:8000` for local development, can be set to the Railway URL for production
4. **Better Developer Experience**: API consumers can see and select the correct server URL directly in the Swagger UI

### Usage

#### Local Development (no changes needed)
```bash
python main.py
# Swagger docs will use http://localhost:8000
```

#### Railway Deployment
```bash
# Set the BASE_URL environment variable
railway variables set BASE_URL=https://your-app.railway.app

# Or in Railway Dashboard:
# Variables → Add Variable → BASE_URL = https://your-app.railway.app
```

### Testing

To test the changes:

1. Start the server: `python main.py`
2. Visit the Swagger docs:
   - http://localhost:8000/payment/docs
   - http://localhost:8000/erp/docs
   - http://localhost:8000/email/docs
3. Look at the "Servers" dropdown - it should now show full URLs with descriptions

### Rollback

If needed, these changes are backward compatible. The server will work exactly as before if `BASE_URL` is not set (defaults to localhost).

