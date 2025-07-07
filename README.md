# Zippuff - USPS ZIP Code Lookup Tool

A tool for looking up ZIP codes and city/state information using the USPS API. Features both CLI and web API interfaces with proper credential management and Ansible deployment support.

## Features

- 🔐 **Secure Credential Management**: Environment variables and encrypted configuration
- 🌐 **Web API Interface**: RESTful API with JSON responses
- 💻 **CLI Interface**: Command-line tool for direct usage
- 🚀 **Production Ready**: Systemd service, nginx reverse proxy, logging
- 🔧 **Ansible Deployment**: Automated deployment with proper security
- 📊 **Comprehensive Logging**: Structured logging with file and console output

## Quick Start

### 1. Set up credentials

Copy the environment template and configure your USPS API credentials:

```bash
cp env.template .env
# Edit .env and set your USPS_USERID
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Test the tool

```bash
# Test CLI
python src/cli.py test

# Look up city/state from ZIP
python src/cli.py zip-to-city 95618

# Look up ZIP from city/state
python src/cli.py city-to-zip "Davis" CA
```

### 4. Run the web application

```bash
python src/web_app.py
```

The web application will be available at `http://localhost:59080`

## API Endpoints

### Health Check
```
GET /health
```

### ZIP to City/State
```
GET /api/zip-to-city?zipcode=95618
```

### City/State to ZIP
```
GET /api/city-to-zip?city=Davis&state=CA
```

### Validate ZIP Code
```
GET /api/validate-zip?zipcode=95618
```

### Configuration Info
```
GET /api/config
```

## CLI Usage

```bash
# Test API connection
python src/cli.py test

# ZIP to city/state lookup
python src/cli.py zip-to-city 95618

# City/state to ZIP lookup
python src/cli.py city-to-zip "Davis" CA

# Validate ZIP code
python src/cli.py validate 95618

# Show configuration
python src/cli.py config
```

## Deployment with Ansible

### 1. Configure deployment variables

Set environment variables for your deployment:

```bash
export ZIPPUFF_HOST=your-server-ip
export ZIPPUFF_USER=www-data
export ZIPPUFF_SSH_KEY=~/.ssh/your-key
export USPS_USERID=your-usps-userid
export NGINX_SERVER_NAME=zippuff.net
```

### 2. Run the deployment

```bash
cd ansible
ansible-playbook -i inventory.yml playbook.yml
```

### 3. Verify deployment

```bash
# Check service status
sudo systemctl status zippuff

# Test API
curl http://your-server-ip/health
```

## Security Features

- 🔒 **Environment Variables**: Credentials stored in environment variables
- 🛡️ **Systemd Security**: Restricted service with security settings
- 🔐 **Nginx SSL Support**: Optional HTTPS with proper security headers
- 📝 **Audit Logging**: Comprehensive logging for security monitoring
- 🚫 **No Hardcoded Secrets**: All credentials externalized

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USPS_USERID` | USPS API User ID | Required |
| `USPS_TEST_MODE` | Use test mode | `true` |
| `APP_HOST` | Application host | `0.0.0.0` |
| `APP_PORT` | Application port | `59080` |
| `APP_DEBUG` | Debug mode | `false` |

### Configuration Files

- `config/config.yaml`: Base configuration
- `.env`: Environment-specific settings
- `ansible/vars/main.yml`: Deployment variables

## Development

### Project Structure

```
zippuff/
├── src/
│   ├── usps_client.py      # USPS API client
│   ├── config_manager.py   # Configuration management
│   ├── cli.py             # Command-line interface
│   └── web_api.py         # Web API interface
├── config/
│   └── config.yaml        # Base configuration
├── ansible/               # Deployment automation
│   ├── playbook.yml
│   ├── inventory.yml
│   ├── vars/
│   └── templates/
├── requirements.txt       # Python dependencies
└── env.template          # Environment template
```

### Adding New Features

1. **New API Endpoints**: Add routes to `src/web_api.py`
2. **New CLI Commands**: Add subparsers to `src/cli.py`
3. **Configuration**: Update `src/config_manager.py`
4. **Deployment**: Update Ansible playbooks as needed

## Troubleshooting

### Common Issues

1. **USPS API Errors**: Verify your UserID and test mode settings
2. **Port Conflicts**: Change `APP_PORT` in configuration
3. **Permission Errors**: Check file permissions and user setup
4. **Service Won't Start**: Check logs with `journalctl -u zippuff`

### Logs

- Application logs: `logs/zippuff.log`
- Systemd logs: `journalctl -u zippuff`
- Nginx logs: `/var/log/nginx/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
