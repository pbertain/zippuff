"""
Configuration manager for secure credential and settings management
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration with secure credential handling"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path or "config/config.yaml"
        self.logger = logging.getLogger(__name__)
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables"""
        try:
            # Load base config from file if it exists
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = {}
            
            # Override with environment variables
            self._override_from_env()
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._config = {}
    
    def _override_from_env(self):
        """Override configuration with environment variables"""
        # USPS API settings
        if os.getenv('USPS_USERID'):
            if 'usps' not in self._config:
                self._config['usps'] = {}
            self._config['usps']['userid'] = os.getenv('USPS_USERID')
        
        if os.getenv('USPS_TEST_MODE'):
            if 'usps' not in self._config:
                self._config['usps'] = {}
            self._config['usps']['test_mode'] = os.getenv('USPS_TEST_MODE').lower() == 'true'
        
        # App settings
        if os.getenv('APP_HOST'):
            if 'app' not in self._config:
                self._config['app'] = {}
            self._config['app']['host'] = os.getenv('APP_HOST')
        
        if os.getenv('APP_PORT'):
            if 'app' not in self._config:
                self._config['app'] = {}
            self._config['app']['port'] = int(os.getenv('APP_PORT'))
        
        if os.getenv('APP_DEBUG'):
            if 'app' not in self._config:
                self._config['app'] = {}
            self._config['app']['debug'] = os.getenv('APP_DEBUG').lower() == 'true'
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'usps.userid')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_usps_config(self) -> Dict[str, Any]:
        """
        Get USPS API configuration
        
        Returns:
            Dictionary with USPS configuration
        """
        return {
            'userid': self.get('usps.userid'),
            'test_mode': self.get('usps.test_mode', True),
            'base_url': self.get('usps.base_url', 'http://production.shippingapis.com/ShippingAPI.dll')
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """
        Get application configuration
        
        Returns:
            Dictionary with app configuration
        """
        return {
            'name': self.get('app.name', 'zippuff'),
            'version': self.get('app.version', '1.0.0'),
            'debug': self.get('app.debug', False),
            'host': self.get('app.host', '0.0.0.0'),
            'port': self.get('app.port', 8080)
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration
        
        Returns:
            Dictionary with logging configuration
        """
        return {
            'level': self.get('logging.level', 'INFO'),
            'format': self.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            'file': self.get('logging.file', 'logs/zippuff.log')
        }
    
    def validate_config(self) -> bool:
        """
        Validate that required configuration is present
        
        Returns:
            True if configuration is valid
        """
        usps_userid = self.get('usps.userid')
        if not usps_userid or usps_userid == 'YOUR_USERID':
            self.logger.error("USPS UserID not configured")
            return False
        
        return True
    
    def create_env_template(self, output_path: str = ".env.template"):
        """
        Create environment variable template file
        
        Args:
            output_path: Path to output template file
        """
        template_content = """# USPS API Configuration
USPS_USERID=your_usps_userid_here
USPS_TEST_MODE=true

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8080
APP_DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
"""
        
        try:
            with open(output_path, 'w') as f:
                f.write(template_content)
            self.logger.info(f"Environment template created at {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to create environment template: {e}") 