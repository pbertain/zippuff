# Deployment Fixes Guide

## Issue 1: Port Conflict Between Services

### Problem
Both `zippuff.service` and `zippuff-api.service` were trying to run on the same port (59080) because they both used `web_app.py`.

### Solution Applied
- Updated `zippuff-api.service` to use `web_api.py` instead of `web_app.py`
- Configured different ports for each service:
  - `zippuff.service` → `web_app.py` (port 59080) - Full web interface
  - `zippuff-api.service` → `web_api.py` (port 59081) - API-only service
- Added `API_PORT` environment variable support

### To Apply the Fix
1. Redeploy the services:
   ```bash
   cd ansible
   ./deploy.sh
   ```

2. Check service status:
   ```bash
   ./check-status.sh
   ```

## Issue 2: OAuth Authentication Error

### Problem
The USPS API service is failing with OAuth 400 errors because:
- Missing or invalid OAuth credentials
- Using placeholder/test values instead of real USPS API credentials

### Solution Required

#### Step 1: Get Real USPS API Credentials
You need to obtain real USPS API credentials from the USPS developer portal:
1. Visit: https://www.usps.com/business/web-tools-apis/
2. Register for a USPS Web Tools API account
3. Request access to the Address Information APIs
4. Obtain your Consumer Key and Consumer Secret

#### Step 2: Configure Environment Variables
Set the following environment variables before deployment:

```bash
# Required USPS OAuth Credentials
export USPS_CONSUMER_KEY="your_real_consumer_key_here"
export USPS_CONSUMER_SECRET="your_real_consumer_secret_here"

# Optional: Set test mode (true for testing, false for production)
export USPS_TEST_MODE="true"

# Optional: Set debug mode
export APP_DEBUG="false"
```

#### Step 3: Verify Configuration
Create a `.env` file in the project root with your credentials:

```bash
# Copy the example file
cp env.example .env

# Edit with your real credentials
nano .env
```

Example `.env` file:
```env
# USPS API Credentials
USPS_CONSUMER_KEY=your_real_consumer_key_here
USPS_CONSUMER_SECRET=your_real_consumer_secret_here

# API Configuration
USPS_TEST_MODE=true  # Set to false for production

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=59080
APP_DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
```

#### Step 4: Redeploy with Real Credentials
```bash
cd ansible
./deploy.sh
```

## Verification Steps

### 1. Check Service Status
```bash
cd ansible
./check-status.sh
```

Expected output:
- `zippuff.service` should be active and running on port 59080
- `zippuff-api.service` should be active and running on port 59081
- No port conflicts should be reported

### 2. Test API Endpoints
```bash
# Test the web interface
curl http://your-server:59080/

# Test the API service
curl http://your-server:59081/api/health

# Test a ZIP code lookup
curl "http://your-server:59081/api/city-to-zip?city=Davis&state=CA"
```

### 3. Check Logs for OAuth Success
```bash
# Check service logs
sudo journalctl -u zippuff-api.service -f

# Look for successful OAuth token requests:
# "OAuth token obtained successfully"
```

## Troubleshooting

### If OAuth Still Fails
1. Verify your credentials are correct
2. Check if you're using the right test/production endpoints
3. Ensure your USPS API account has the necessary permissions
4. Check the USPS API status page for any service issues

### If Services Still Conflict
1. Check which ports are actually in use:
   ```bash
   sudo netstat -tlnp | grep 5908
   ```
2. Verify service configurations:
   ```bash
   sudo systemctl status zippuff.service
   sudo systemctl status zippuff-api.service
   ```

### If Services Won't Start
1. Check the service logs:
   ```bash
   sudo journalctl -u zippuff.service -n 50
   sudo journalctl -u zippuff-api.service -n 50
   ```
2. Verify the Python environment and dependencies
3. Check file permissions in `/opt/zippuff/`

## Next Steps
1. Obtain real USPS API credentials
2. Set the environment variables
3. Redeploy the services
4. Test the API endpoints
5. Monitor the logs for successful OAuth authentication 