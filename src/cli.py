"""
Command-line interface for USPS ZIP code lookup tool
Updated to use the API service instead of direct USPS calls
"""
import argparse
import sys
import logging
import requests
import os
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager


def setup_logging(config: ConfigManager):
    """Setup logging configuration"""
    log_config = config.get_logging_config()
    
    # Create logs directory if it doesn't exist
    log_file = Path(log_config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config['level']),
        format=log_config['format'],
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_api_service_url():
    """Get API service URL from environment or config"""
    api_port = os.getenv('API_PORT', '59081')
    api_host = os.getenv('API_HOST', 'localhost')
    return f"http://{api_host}:{api_port}"


def call_api_service(endpoint: str, params: Optional[dict] = None) -> dict:
    """
    Call the API service
    
    Args:
        endpoint: API endpoint (e.g., '/api/zip-to-city')
        params: Query parameters
        
    Returns:
        API response as dictionary
    """
    api_url = get_api_service_url()
    url = f"{api_url}{endpoint}"
    
    try:
        response = requests.get(url, params=params or {}, timeout=10)
        return {
            'success': response.status_code == 200,
            'status_code': response.status_code,
            'data': response.json() if response.status_code == 200 else None,
            'error': response.json().get('error') if response.status_code != 200 else None
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'status_code': 0,
            'data': None,
            'error': f"Failed to connect to API service at {api_url}"
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'status_code': 0,
            'data': None,
            'error': "API service request timed out"
        }
    except Exception as e:
        return {
            'success': False,
            'status_code': 0,
            'data': None,
            'error': f"API service error: {e}"
        }


def print_result(result: dict, operation: str):
    """Print formatted result"""
    if not result['success']:
        print(f"❌ Error: {result['error']}")
        return
    
    data = result['data']
    if not data:
        print(f"❌ Error: No data received from API service")
        return
    
    print(f"✅ {operation} Result:")
    if data.get('zipcode'):
        print(f"   ZIP Code: {data['zipcode']}")
    if data.get('city'):
        print(f"   City: {data['city']}")
    if data.get('state'):
        print(f"   State: {data['state']}")
    if data.get('valid') is not None:
        print(f"   Valid: {'Yes' if data['valid'] else 'No'}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="USPS ZIP Code Lookup Tool (API Client)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s zip-to-city 90210
  %(prog)s city-to-zip "Beverly Hills" CA
  %(prog)s validate 90210
  %(prog)s config
  %(prog)s test
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ZIP to City/State command
    zip_parser = subparsers.add_parser('zip-to-city', help='Look up city and state from ZIP code')
    zip_parser.add_argument('zipcode', help='5-digit ZIP code')
    
    # City/State to ZIP command
    city_parser = subparsers.add_parser('city-to-zip', help='Look up ZIP code from city and state')
    city_parser.add_argument('city', help='City name')
    city_parser.add_argument('state', help='State abbreviation (2 letters)')
    
    # Validate ZIP command
    validate_parser = subparsers.add_parser('validate', help='Validate ZIP code format')
    validate_parser.add_argument('zipcode', help='ZIP code to validate')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show current configuration')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test API service connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize configuration
    try:
        config = ConfigManager()
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Handle commands
    try:
        if args.command == 'zip-to-city':
            result = call_api_service('/api/zip-to-city', {'zipcode': args.zipcode})
            print_result(result, "ZIP to City/State")
            
        elif args.command == 'city-to-zip':
            result = call_api_service('/api/city-to-zip', {
                'city': args.city,
                'state': args.state
            })
            print_result(result, "City/State to ZIP")
            
        elif args.command == 'validate':
            result = call_api_service('/api/validate-zip', {'zipcode': args.zipcode})
            if result['success'] and result['data']:
                is_valid = result['data'].get('valid', False)
                if is_valid:
                    print(f"✅ ZIP code {args.zipcode} is valid")
                else:
                    print(f"❌ ZIP code {args.zipcode} is invalid")
            else:
                print(f"❌ Error: {result['error']}")
                
        elif args.command == 'config':
            result = call_api_service('/api/config')
            if result['success'] and result['data']:
                config_data = result['data']
                print("📋 API Service Configuration:")
                print(f"   API Service: {get_api_service_url()}")
                if 'api_status' in config_data:
                    api_status = config_data['api_status']
                    if isinstance(api_status, dict):
                        print(f"   Test Mode: {api_status.get('test_mode', 'Unknown')}")
                        print(f"   Base URL: {api_status.get('base_url', 'Unknown')}")
                        print(f"   Status: {api_status.get('status', 'Unknown')}")
                    else:
                        print(f"   Status: {api_status}")
                print(f"   Web Version: {config_data.get('web_version', 'Unknown')}")
            else:
                print(f"❌ Error getting configuration: {result['error']}")
                
        elif args.command == 'test':
            print("🧪 Testing API service connection...")
            result = call_api_service('/api/zip-to-city', {'zipcode': '90210'})
            if result['success']:
                print("✅ API service connection successful!")
                print_result(result, "Test")
            else:
                print(f"❌ API service test failed: {result['error']}")
                
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 