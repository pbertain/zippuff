#!/usr/bin/env python3
"""
Test script to verify USPS API endpoints and parameters
"""
import os
import requests
import json
import base64
import time

def test_endpoints_with_token():
    """Test different USPS API endpoints with a known working token"""
    # Use the token we got from curl
    token = "eyJraWQiOiJIdWpzX2F6UnFJUzBpSE5YNEZIRk96eUwwdjE4RXJMdjNyZDBoalpNUnJFIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ.eyJlbnRpdGxlbWVudHMiOltdLCJzdWIiOiI0NTkwNzUzMDMiLCJjcmlkIjoiNTMwNjk4MDYiLCJzdWJfaWQiOiI0NTkwNzUzMDMiLCJyb2xlcyI6W10sInBheW1lbnRfYWNjb3VudHMiOnsicGVybWl0cyI6W119LCJpc3MiOiJodHRwczovL2tleWMudXNwcy5jb20vcmVhbG1zL1VTUFMiLCJjb250cmFjdHMiOnsicGF5bWVudEFjY291bnRzIjp7fSwicGVybWl0cyI6W119LCJhdWQiOlsicGF5bWVudHMiLCJwcmljZXMiLCJzdWJzY3JpcHRpb25zLXRyYWNraW5nIiwib3JnYW5pemF0aW9ucyJdLCJhenAiOiJ4SDlaMjVoTGJuRVhjT3Y2UnBDRUxKQjV2cGFmM3ZLcmVkWGR1RGp5RkQzdmh3QWQiLCJtYWlsX293bmVycyI6W3siY3JpZCI6IjUzMDY5ODA2IiwibWlkcyI6IiJ9XSwic2NvcGUiOiJhZGRyZXNzZXMiLCJjb21wYW55X25hbWUiOiJaSVAgUHVmZiIsImV4cCI6MTc1MjUzNDk3OCwiaWF0IjoxNzUyNTA2MTc4LCJqdGkiOiJkN2MwODNlNy02M2ZjLTQ0OTEtOTU0MC0yNjk0YjI1NjkxODkifQ.nX-4wlKLd2IZJjFLzx51_rWropD4-fNYTpyZQ4OV0JTyrDgv8kUyYHKlHx6ELgjSh78ngf7M79JnROlCl3OCc5-GVfB0C5Dldu12aUCklXBa2aBCwzcl0B7PjlFY4WwHOsO6o5xReJqiAKyT17UBbOI7Hg9-CE7r8Mz2oJUI4tQE7dkjN51Zl3ELb_okZju9dImHxJ8_PMugaBjL57P8uwrdwFhaD3fAANsqbJRhmou12_758PSjhyIdwuHywgl6f3s6Ba2mxWiSklMfP5d0gfNDLemk1WGbWMORxfXpCeUWlcBaKRB1TApRJqS_KRrXBBU92cUx1cal4nrHNZH3SQ"
    
    base_url = "https://apis-tem.usps.com/addresses/v3"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }
    
    # Test 1: ZIP to city/state (this works)
    print("\n=== Test 1: ZIP to city/state ===")
    url1 = f"{base_url}/city-state"
    params1 = {'ZIPCode': '90210'}
    response1 = requests.get(url1, params=params1, headers=headers)
    print(f"URL: {response1.url}")
    print(f"Status: {response1.status_code}")
    print(f"Response: {response1.text}")
    
    # Test 2: Address validation with real address (Beverly Hills City Hall)
    print("\n=== Test 2: Address validation with real address ===")
    url2 = f"{base_url}/zipcode"
    params2 = {
        'streetAddress': '455 N Rexford Dr',
        'city': 'Beverly Hills',
        'state': 'CA',
        'ZIPCode': '90210'
    }
    response2 = requests.get(url2, params=params2, headers=headers)
    print(f"URL: {response2.url}")
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")
    
    # Test 3: Address validation with different real address
    print("\n=== Test 3: Address validation with different real address ===")
    url3 = f"{base_url}/zipcode"
    params3 = {
        'streetAddress': '1234 Main St',
        'city': 'Davis',
        'state': 'CA',
        'ZIPCode': '95616'
    }
    response3 = requests.get(url3, params=params3, headers=headers)
    print(f"URL: {response3.url}")
    print(f"Status: {response3.status_code}")
    print(f"Response: {response3.text}")
    
    # Test 4: Address validation with secondary address
    print("\n=== Test 4: Address validation with secondary address ===")
    url4 = f"{base_url}/zipcode"
    params4 = {
        'streetAddress': '455 N Rexford Dr',
        'secondaryAddress': 'Suite 100',
        'city': 'Beverly Hills',
        'state': 'CA',
        'ZIPCode': '90210'
    }
    response4 = requests.get(url4, params=params4, headers=headers)
    print(f"URL: {response4.url}")
    print(f"Status: {response4.status_code}")
    print(f"Response: {response4.text}")

if __name__ == "__main__":
    test_endpoints_with_token() 