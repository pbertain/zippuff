# API Credentials Management

This document explains how to securely store your USPS API credentials.

## 🔐 Credential Storage Options

### 1. Environment Variables (Recommended)

**For Development:**
1. Copy the example file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```bash
   # USPS API Credentials
   USPS_USERID=your_actual_usps_userid_here
   USPS_CONSUMER_KEY=your_consumer_key_here
   USPS_CONSUMER_SECRET=your_consumer_secret_here
   
   # API Configuration
   USPS_TEST_MODE=true  # Set to false for production
   ```

**For Production:**
Set environment variables directly:
```bash
export USPS_USERID=your_actual_usps_userid_here
export USPS_CONSUMER_KEY=your_consumer_key_here
export USPS_CONSUMER_SECRET=your_consumer_secret_here
export USPS_TEST_MODE=false
```

### 2. System Environment Variables

**Linux/macOS:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export USPS_USERID="your_userid"
export USPS_CONSUMER_KEY="your_consumer_key"
export USPS_CONSUMER_SECRET="your_consumer_secret"
```

**Windows:**
```cmd
set USPS_USERID=your_userid
set USPS_CONSUMER_KEY=your_consumer_key
set USPS_CONSUMER_SECRET=your_consumer_secret
```

### 3. Docker Environment Variables

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  zippuff:
    build: .
    environment:
      - USPS_USERID=${USPS_USERID}
      - USPS_CONSUMER_KEY=${USPS_CONSUMER_KEY}
      - USPS_CONSUMER_SECRET=${USPS_CONSUMER_SECRET}
      - USPS_TEST_MODE=false
```

### 4. Kubernetes Secrets

**Create a secret:**
```bash
kubectl create secret generic usps-api-credentials \
  --from-literal=USPS_USERID=your_userid \
  --from-literal=USPS_CONSUMER_KEY=your_consumer_key \
  --from-literal=USPS_CONSUMER_SECRET=your_consumer_secret
```

**Deployment YAML:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zippuff
spec:
  template:
    spec:
      containers:
      - name: zippuff
        image: zippuff:latest
        env:
        - name: USPS_USERID
          valueFrom:
            secretKeyRef:
              name: usps-api-credentials
              key: USPS_USERID
        - name: USPS_CONSUMER_KEY
          valueFrom:
            secretKeyRef:
              name: usps-api-credentials
              key: USPS_CONSUMER_KEY
        - name: USPS_CONSUMER_SECRET
          valueFrom:
            secretKeyRef:
              name: usps-api-credentials
              key: USPS_CONSUMER_SECRET
```

### 5. AWS Secrets Manager

**Store secrets:**
```bash
aws secretsmanager create-secret \
  --name "zippuff/usps-api" \
  --description "USPS API credentials for Zippuff" \
  --secret-string '{
    "USPS_USERID": "your_userid",
    "USPS_CONSUMER_KEY": "your_consumer_key",
    "USPS_CONSUMER_SECRET": "your_consumer_secret"
  }'
```

**Retrieve in application:**
```python
import boto3
import json

def get_secrets():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='zippuff/usps-api')
    return json.loads(response['SecretString'])
```

### 6. HashiCorp Vault

**Store secrets:**
```bash
vault kv put secret/zippuff/usps-api \
  USPS_USERID=your_userid \
  USPS_CONSUMER_KEY=your_consumer_key \
  USPS_CONSUMER_SECRET=your_consumer_secret
```

**Retrieve in application:**
```python
import hvac

def get_secrets():
    client = hvac.Client(url='http://vault:8200')
    response = client.secrets.kv.v2.read_secret_version(
        path='zippuff/usps-api'
    )
    return response['data']['data']
```

## 🛡️ Security Best Practices

### 1. Never Commit Credentials
- Add `.env` to your `.gitignore`
- Use environment variables in production
- Rotate credentials regularly

### 2. Use Different Credentials
- Use test credentials for development
- Use production credentials only in production
- Never share credentials between environments

### 3. Monitor Usage
- Log API calls (without sensitive data)
- Set up alerts for unusual usage patterns
- Monitor for credential exposure

### 4. Access Control
- Limit who has access to credentials
- Use least privilege principle
- Audit credential access regularly

## 🔧 Configuration Priority

The application loads credentials in this order:
1. Environment variables
2. `.env` file (if dotenv is installed)
3. Configuration file
4. Default values

## 🚨 Troubleshooting

### Credential Not Found
```bash
# Check if environment variable is set
echo $USPS_USERID

# Test the application
python src/cli.py test
```

### Invalid Credentials
```bash
# Verify your USPS API credentials
# Contact USPS if credentials are invalid
```

### Permission Denied
```bash
# Check file permissions
ls -la .env

# Fix permissions if needed
chmod 600 .env
```

## 📋 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `USPS_USERID` | USPS API User ID | Yes | None |
| `USPS_CONSUMER_KEY` | USPS Consumer Key | No | None |
| `USPS_CONSUMER_SECRET` | USPS Consumer Secret | No | None |
| `USPS_TEST_MODE` | Use test mode | No | true |
| `APP_HOST` | Application host | No | 0.0.0.0 |
| `APP_PORT` | Application port | No | 59080 |
| `APP_DEBUG` | Debug mode | No | false |
| `LOG_LEVEL` | Logging level | No | INFO | 