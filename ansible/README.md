# Zippuff Ansible Deployment

This directory contains the Ansible configuration for deploying the Zippuff USPS API tool.

## Files

- `playbook.yml` - Main Ansible playbook for deployment
- `inventory.yml` - Host inventory configuration
- `deployment.env` - Environment variables for deployment
- `deploy.sh` - Deployment script (sources env and runs playbook)
- `check-status.sh` - Status check script
- `templates/` - Jinja2 templates for configuration files
- `vars/` - Variable definitions

## Quick Deployment

1. **Ensure your SSH key is set up**:
   ```bash
   # Your SSH key should be at ~/.ssh/keys/nirdclub__id_ed25519
   # and you should have access to the target hosts
   ```

2. **Run the deployment**:
   ```bash
   cd ansible
   ./deploy.sh
   ```

3. **Check the status**:
   ```bash
   ./check-status.sh
   ```

## Manual Deployment

If you prefer to run the playbook manually:

```bash
cd ansible
source deployment.env
ansible-playbook -i inventory.yml playbook.yml --ask-become-pass
```

## What Gets Deployed

### Services
- **zippuff-api**: The main API service running on port 59080
- **nginx**: Managed by separate Ansible playbook

### Files
- Application code: `/opt/zippuff/`
- Environment file: `/opt/zippuff/.env`
- Systemd service: `/etc/systemd/system/zippuff-api.service`

### Environment Variables
The deployment automatically loads these from `deployment.env`:
- `USPS_USERID`
- `USPS_CONSUMER_KEY`
- `USPS_CONSUMER_SECRET`
- `USPS_TEST_MODE`

## Troubleshooting

### Check Service Status
```bash
# On the target server
sudo systemctl status zippuff-api
```

### Check Logs
```bash
# On the target server
sudo journalctl -u zippuff-api -f
```

### Restart Services
```bash
# On the target server
sudo systemctl restart zippuff-api
```

### Check Application
```bash
# Test the API directly
curl http://localhost:59080/health

# Test through nginx
curl http://your-host/health
```

## Access Points

- **API Direct**: `http://your-host:59080/` (direct access)
- **Health Check**: `http://your-host:59080/health`
- **Web Interface**: Managed by your nginx configuration

## Configuration

### Adding New Hosts
Edit `inventory.yml` to add new hosts to the `zippuff_servers` group.

### Changing Environment Variables
Edit `deployment.env` and redeploy.

### Modifying Service Configuration
Edit the templates in `templates/` directory and redeploy. 