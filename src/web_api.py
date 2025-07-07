"""
Flask web API for USPS ZIP code lookup tool
"""
from flask import Flask, request, jsonify
import logging
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
from usps_client import USPSClient, AddressInfo


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Initialize configuration
    config = ConfigManager()
    
    # Setup logging
    log_config = config.get_logging_config()
    log_file = Path(log_config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format=log_config['format'],
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Initialize USPS client
    usps_config = config.get_usps_config()
    usps_client = USPSClient(
        userid=usps_config['userid'],
        test_mode=usps_config['test_mode']
    )
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'zippuff',
            'version': config.get('app.version', '1.0.0')
        })
    
    @app.route('/api/zip-to-city', methods=['GET'])
    def zip_to_city():
        """Look up city and state from ZIP code"""
        zipcode = request.args.get('zipcode')
        
        if not zipcode:
            return jsonify({
                'error': 'ZIP code parameter is required'
            }), 400
        
        result = usps_client.zip_to_city_state(zipcode)
        
        if result.error:
            return jsonify({
                'error': result.error
            }), 400
        
        return jsonify({
            'zipcode': result.zipcode,
            'city': result.city,
            'state': result.state
        })
    
    @app.route('/api/city-to-zip', methods=['GET'])
    def city_to_zip():
        """Look up ZIP code from city and state"""
        city = request.args.get('city')
        state = request.args.get('state')
        
        if not city or not state:
            return jsonify({
                'error': 'Both city and state parameters are required'
            }), 400
        
        result = usps_client.city_state_to_zip(city, state)
        
        if result.error:
            return jsonify({
                'error': result.error
            }), 400
        
        return jsonify({
            'zipcode': result.zipcode,
            'city': result.city,
            'state': result.state
        })
    
    @app.route('/api/validate-zip', methods=['GET'])
    def validate_zip():
        """Validate ZIP code format"""
        zipcode = request.args.get('zipcode')
        
        if not zipcode:
            return jsonify({
                'error': 'ZIP code parameter is required'
            }), 400
        
        is_valid = usps_client.validate_zipcode(zipcode)
        
        return jsonify({
            'zipcode': zipcode,
            'valid': is_valid
        })
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration (without sensitive data)"""
        return jsonify({
            'test_mode': usps_config['test_mode'],
            'base_url': usps_config['base_url'],
            'app_version': config.get('app.version', '1.0.0')
        })
    
    @app.route('/', methods=['GET'])
    def index():
        """API documentation"""
        return jsonify({
            'service': 'Zippuff USPS API Tool',
            'version': config.get('app.version', '1.0.0'),
            'endpoints': {
                'health': '/health',
                'zip_to_city': '/api/zip-to-city?zipcode=<zipcode>',
                'city_to_zip': '/api/city-to-zip?city=<city>&state=<state>',
                'validate_zip': '/api/validate-zip?zipcode=<zipcode>',
                'config': '/api/config'
            },
            'examples': {
                'zip_to_city': '/api/zip-to-city?zipcode=90210',
                'city_to_zip': '/api/city-to-zip?city=Beverly%20Hills&state=CA',
                'validate_zip': '/api/validate-zip?zipcode=90210'
            }
        })
    
    return app


def main():
    """Run the Flask application"""
    config = ConfigManager()
    app_config = config.get_app_config()
    
    app = create_app()
    
    app.run(
        host=app_config['host'],
        port=app_config['port'],
        debug=app_config['debug']
    )


if __name__ == '__main__':
    main() 