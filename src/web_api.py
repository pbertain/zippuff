"""
Flask web API for USPS ZIP code lookup tool
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
from usps_api_service import get_usps_service, USPSResponse


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app, origins=["*"])
    
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
    
    # Initialize USPS API service
    try:
        usps_service = get_usps_service()
        app.logger.info("USPS API service initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize USPS API service: {e}")
        usps_service = None
    
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
        if not usps_service:
            return jsonify({
                'error': 'USPS API service not available'
            }), 503
        
        zipcode = request.args.get('zipcode')
        
        if not zipcode:
            return jsonify({
                'error': 'ZIP code parameter is required'
            }), 400
        
        result = usps_service.zip_to_city_state(zipcode)
        
        if not result.success:
            return jsonify({
                'error': result.error
            }), 400
        
        return jsonify({
            'zipcode': result.data.zipcode if result.data else None,
            'city': result.data.city if result.data else None,
            'state': result.data.state if result.data else None
        })
    
    @app.route('/api/city-to-zip', methods=['GET'])
    def city_to_zip():
        """Look up ZIP code from city and state"""
        if not usps_service:
            return jsonify({
                'error': 'USPS API service not available'
            }), 503
        
        city = request.args.get('city')
        state = request.args.get('state')
        
        if not city or not state:
            return jsonify({
                'error': 'Both city and state parameters are required'
            }), 400
        
        result = usps_service.city_state_to_zip(city, state)
        
        if not result.success:
            return jsonify({
                'error': result.error
            }), 400
        
        return jsonify({
            'zipcode': result.data.zipcode if result.data else None,
            'city': result.data.city if result.data else None,
            'state': result.data.state if result.data else None
        })
    
    @app.route('/api/validate-zip', methods=['GET'])
    def validate_zip():
        """Validate ZIP code format"""
        if not usps_service:
            return jsonify({
                'error': 'USPS API service not available'
            }), 503
        
        zipcode = request.args.get('zipcode')
        
        if not zipcode:
            return jsonify({
                'error': 'ZIP code parameter is required'
            }), 400
        
        is_valid = usps_service.validate_zipcode(zipcode)
        
        return jsonify({
            'zipcode': zipcode,
            'valid': is_valid
        })
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration (without sensitive data)"""
        if usps_service:
            status = usps_service.get_api_status()
        else:
            status = {'status': 'unavailable'}
        
        return jsonify({
            'test_mode': status.get('test_mode', False),
            'base_url': status.get('base_url', ''),
            'app_version': config.get('app.version', '1.0.0'),
            'api_status': status.get('status', 'unknown')
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
    
    # Use API_PORT if available, otherwise use regular port
    api_port = os.getenv('API_PORT')
    if api_port:
        try:
            app_config['port'] = int(api_port)
        except ValueError:
            pass  # Use default port if invalid
    
    app = create_app()
    
    app.run(
        host=app_config['host'],
        port=app_config['port'],
        debug=app_config['debug']
    )


if __name__ == '__main__':
    main() 