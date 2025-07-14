#!/usr/bin/env python3
"""
Simple test script for USPS API service with v3 endpoints
"""
import os
import sys
import requests
import time
import base64

def test_usps_oauth():
    """Test USPS OAuth 2.0 flow and API calls"""
    print("Testing USPS OAuth 2.0 and v3 API...")
    
    # OAuth credentials
    client_id = "xH9Z25hLbnEXcOv6RpCELJB5vpaf3vKredXduDjyFD3vhwAd"
    client_secret = "your_secret_here"  # Replace with actual secret
    
    # OAuth endpoints
    oauth_url = "https://apis.usps.com/oauth2/v3/token"
    api_base = "https://apis.usps.com/addresses/v3"
    
    try:
        # Step 1: Get OAuth token
        print("1. Getting OAuth token...")
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'addresses'
        }
        
        response = requests.post(oauth_url, headers=headers, data=data, timeout=30)
        
        if response.status_code != 200:
            print(f"✗ OAuth token request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        token_data = response.json()
        access_token = token_data['access_token']
        print("✓ OAuth token obtained successfully")
        
        # Step 2: Test API call
        print("2. Testing API call...")
        
        api_url = f"{api_base}/city-state"
        params = {'ZIPCode': '20012'}
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"✗ API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        print("✓ API call successful!")
        print(f"  - City: {data.get('city')}")
        print(f"  - State: {data.get('state')}")
        print(f"  - ZIP: {data.get('ZIPCode')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_usps_oauth()
    sys.exit(0 if success else 1) 