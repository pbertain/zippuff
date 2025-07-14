#!/usr/bin/env python3
"""
Test script for the updated USPS API service with v3 endpoints
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from usps_api_service import get_usps_service

def test_usps_service():
    """Test the USPS API service with v3 endpoints"""
    print("Testing USPS API Service with v3 endpoints...")
    
    try:
        # Get the service
        service = get_usps_service()
        print(f"✓ Service initialized successfully")
        print(f"  - Base URL: {service.base_url}")
        print(f"  - Test Mode: {service.test_mode}")
        print(f"  - OAuth Configured: {bool(service.client_id and service.client_secret)}")
        
        # Test connection
        print("\nTesting API connection...")
        test_result = service.test_connection()
        
        if test_result.success:
            print("✓ API connection successful!")
            print(f"  - Test ZIP: 90210")
            if test_result.data:
                print(f"  - City: {test_result.data.city}")
                print(f"  - State: {test_result.data.state}")
        else:
            print(f"✗ API connection failed: {test_result.error}")
            return False
        
        # Test specific ZIP codes
        test_zipcodes = ["20012", "95618", "90210"]
        
        for zipcode in test_zipcodes:
            print(f"\nTesting ZIP code: {zipcode}")
            result = service.zip_to_city_state(zipcode)
            
            if result.success and result.data:
                print(f"✓ Success: {result.data.city}, {result.data.state}")
            else:
                print(f"✗ Failed: {result.error}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing USPS service: {e}")
        return False

if __name__ == "__main__":
    success = test_usps_service()
    sys.exit(0 if success else 1) 