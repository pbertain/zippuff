"""
Command-line interface for USPS ZIP code lookup tool
"""
import argparse
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
from usps_client import USPSClient, AddressInfo


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


def print_result(result: AddressInfo, operation: str):
    """Print formatted result"""
    if result.error:
        print(f"❌ Error: {result.error}")
        return
    
    print(f"✅ {operation} Result:")
    if result.zipcode:
        print(f"   ZIP Code: {result.zipcode}")
    if result.city:
        print(f"   City: {result.city}")
    if result.state:
        print(f"   State: {result.state}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="USPS ZIP Code Lookup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s zip-to-city 90210
  %(prog)s city-to-zip "Beverly Hills" CA
  %(prog)s validate 90210
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
    test_parser = subparsers.add_parser('test', help='Test USPS API connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize configuration
    try:
        config = ConfigManager()
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        if not config.validate_config():
            print("❌ Configuration error: USPS UserID not set")
            print("Please set USPS_USERID environment variable or update config/config.yaml")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Initialize USPS client
    try:
        usps_config = config.get_usps_config()
        client = USPSClient(
            userid=usps_config['userid'],
            test_mode=usps_config['test_mode']
        )
    except Exception as e:
        print(f"❌ Failed to initialize USPS client: {e}")
        sys.exit(1)
    
    # Handle commands
    try:
        if args.command == 'zip-to-city':
            result = client.zip_to_city_state(args.zipcode)
            print_result(result, "ZIP to City/State")
            
        elif args.command == 'city-to-zip':
            result = client.city_state_to_zip(args.city, args.state)
            print_result(result, "City/State to ZIP")
            
        elif args.command == 'validate':
            is_valid = client.validate_zipcode(args.zipcode)
            if is_valid:
                print(f"✅ ZIP code {args.zipcode} is valid")
            else:
                print(f"❌ ZIP code {args.zipcode} is invalid")
                
        elif args.command == 'config':
            print("📋 Current Configuration:")
            print(f"   USPS UserID: {usps_config['userid']}")
            print(f"   Test Mode: {usps_config['test_mode']}")
            print(f"   Base URL: {usps_config['base_url']}")
            
        elif args.command == 'test':
            print("🧪 Testing USPS API connection...")
            test_result = client.zip_to_city_state("90210")
            if test_result.error:
                print(f"❌ API test failed: {test_result.error}")
            else:
                print("✅ API connection successful!")
                print_result(test_result, "Test")
                
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 