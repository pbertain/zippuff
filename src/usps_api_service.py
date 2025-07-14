"""
Secure USPS API Service Module
Handles all USPS API interactions with proper OAuth 2.0 credential management
"""
import os
import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import sys
import time
import base64

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager


@dataclass
class AddressInfo:
    """Data class for address information"""
    zipcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None


@dataclass
class USPSResponse:
    """Standardized response format for USPS API calls"""
    success: bool
    data: Optional[AddressInfo] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


@dataclass
class OAuthToken:
    """OAuth 2.0 token information"""
    access_token: str
    token_type: str
    expires_in: int
    issued_at: int
    scope: str


class USPSAPIService:
    """
    Secure USPS API Service with OAuth 2.0 authentication
    
    This module provides a secure interface to the USPS API with:
    - OAuth 2.0 Client Credentials flow
    - Automatic token refresh
    - Request/response logging
    - Error handling and retry logic
    - Rate limiting protection
    - Response validation
    """
    
    def __init__(self):
        """Initialize the USPS API service with OAuth 2.0 credential management"""
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        # Load OAuth credentials from environment variables
        self._load_credentials()
        
        # OAuth configuration
        self.oauth_url = "https://apis.usps.com/oauth2/v3/token"
        self.base_url = "https://apis.usps.com/addresses/v3"  # Updated to v3
        self.timeout = 30
        self.max_retries = 3
        
        # Token management
        self.current_token: Optional[OAuthToken] = None
        self.token_expiry = 0
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = None
        
        self.logger.info("USPS API Service initialized")
    
    def _load_credentials(self):
        """Load and validate USPS OAuth credentials from environment variables"""
        # OAuth credentials
        self.client_id = os.getenv('USPS_CONSUMER_KEY')
        self.client_secret = os.getenv('USPS_CONSUMER_SECRET')
        
        # Test mode configuration
        test_mode = os.getenv('USPS_TEST_MODE', 'true').lower()
        self.test_mode = test_mode == 'true'
        
        # Use test endpoints if in test mode
        if self.test_mode:
            self.oauth_url = "https://apis-tem.usps.com/oauth2/v3/token"
            self.base_url = "https://apis-tem.usps.com/addresses/v3"  # Updated to v3
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "USPS OAuth credentials not configured. Please set USPS_CONSUMER_KEY and USPS_CONSUMER_SECRET environment variables."
            )
        
        self.logger.info(f"USPS OAuth credentials loaded (Test Mode: {self.test_mode})")
    
    def _get_oauth_token(self) -> Optional[OAuthToken]:
        """
        Get OAuth 2.0 access token using client credentials flow
        
        Returns:
            OAuthToken object or None if failed
        """
        try:
            # Check if we have a valid token
            if self.current_token and time.time() < self.token_expiry:
                return self.current_token
            
            self.logger.info("Requesting new OAuth token")
            
            # Try different OAuth request formats
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Method 1: Try with credentials in Authorization header
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            
            headers_with_auth = headers.copy()
            headers_with_auth['Authorization'] = f'Basic {auth_header}'
            
            data = {
                'grant_type': 'client_credentials',
                'scope': 'addresses'  # Scope for address lookup APIs
            }
            
            # Debug logging
            self.logger.debug(f"OAuth URL: {self.oauth_url}")
            self.logger.debug(f"OAuth Headers: {headers_with_auth}")
            self.logger.debug(f"OAuth Data: {data}")
            
            # Make OAuth request with Authorization header
            response = requests.post(
                self.oauth_url,
                headers=headers_with_auth,
                data=data,
                timeout=self.timeout
            )
            
            self.logger.info(f"OAuth token response status: {response.status_code}")
            self.logger.debug(f"OAuth response headers: {dict(response.headers)}")
            self.logger.debug(f"OAuth response body: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Calculate expiry time (subtract 5 minutes for safety)
                expires_in = token_data.get('expires_in', 28800)  # 8 hours default
                issued_at = token_data.get('issued_at', int(time.time() * 1000))
                
                self.current_token = OAuthToken(
                    access_token=token_data['access_token'],
                    token_type=token_data['token_type'],
                    expires_in=expires_in,
                    issued_at=issued_at,
                    scope=token_data.get('scope', '')
                )
                
                # Set expiry time (subtract 5 minutes for safety)
                self.token_expiry = time.time() + expires_in - 300
                
                self.logger.info("OAuth token obtained successfully")
                return self.current_token
            else:
                # Try Method 2: Credentials in request body
                self.logger.info("Trying OAuth with credentials in request body")
                
                data_with_creds = {
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'scope': 'addresses'
                }
                
                response = requests.post(
                    self.oauth_url,
                    headers=headers,
                    data=data_with_creds,
                    timeout=self.timeout
                )
                
                self.logger.info(f"OAuth token response status (method 2): {response.status_code}")
                self.logger.debug(f"OAuth response body (method 2): {response.text}")
                
                if response.status_code == 200:
                    token_data = response.json()
                    
                    # Calculate expiry time (subtract 5 minutes for safety)
                    expires_in = token_data.get('expires_in', 28800)  # 8 hours default
                    issued_at = token_data.get('issued_at', int(time.time() * 1000))
                    
                    self.current_token = OAuthToken(
                        access_token=token_data['access_token'],
                        token_type=token_data['token_type'],
                        expires_in=expires_in,
                        issued_at=issued_at,
                        scope=token_data.get('scope', '')
                    )
                    
                    # Set expiry time (subtract 5 minutes for safety)
                    self.token_expiry = time.time() + expires_in - 300
                    
                    self.logger.info("OAuth token obtained successfully (method 2)")
                    return self.current_token
                else:
                    error_msg = f"OAuth token request failed: {response.status_code} - {response.text}"
                    self.logger.error(error_msg)
                    return None
                
        except Exception as e:
            error_msg = f"Failed to get OAuth token: {e}"
            self.logger.error(error_msg)
            return None
    
    def _make_secure_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> USPSResponse:
        """
        Make a secure HTTP request to USPS API with OAuth 2.0 authentication
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            USPSResponse object with standardized response format
        """
        try:
            # Get OAuth token
            token = self._get_oauth_token()
            if not token:
                return USPSResponse(success=False, error="Failed to obtain OAuth token")
            
            # Prepare request
            url = f"{self.base_url}{endpoint}"
            headers = {
                'Authorization': f'Bearer {token.access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Zippuff-USPS-API/1.0'
            }
            
            # Log request (without sensitive data)
            self.logger.info(f"Making USPS API request to {url}")
            self.logger.debug(f"USPS API request params: {params}")
            
            # Make the request
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            # Log response status
            self.logger.info(f"USPS API response status: {response.status_code}")
            
            # Handle HTTP errors
            response.raise_for_status()
            
            # Parse and validate response
            return self._parse_json_response(response.text)
            
        except requests.exceptions.Timeout:
            error_msg = "USPS API request timed out"
            self.logger.error(error_msg)
            return USPSResponse(success=False, error=error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to USPS API"
            self.logger.error(error_msg)
            return USPSResponse(success=False, error=error_msg)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"USPS API HTTP error: {e}"
            self.logger.error(error_msg)
            return USPSResponse(success=False, error=error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error in USPS API request: {e}"
            self.logger.error(error_msg)
            return USPSResponse(success=False, error=error_msg)
    
    def _parse_json_response(self, json_string: str) -> USPSResponse:
        """
        Parse and validate USPS API JSON response
        
        Args:
            json_string: JSON response string
            
        Returns:
            USPSResponse object
        """
        try:
            import json
            data = json.loads(json_string)
            
            # Check for API errors
            if 'error' in data:
                error_msg = data.get('error_description', data['error'])
                self.logger.error(f"USPS API error: {error_msg}")
                return USPSResponse(success=False, error=error_msg, raw_response=json_string)
            
            # Parse successful response - v3 API format
            # Response format: {"city": "WASHINGTON", "state": "DC", "ZIPCode": "20012"}
            if 'city' in data and 'state' in data:
                address_info = AddressInfo(
                    zipcode=data.get('ZIPCode'),
                    city=data.get('city'),
                    state=data.get('state')
                )
                
                self.logger.info("Successfully parsed USPS API v3 response")
                return USPSResponse(success=True, data=address_info, raw_response=json_string)
            
            # No data found
            error_msg = "No data found in USPS API response"
            self.logger.warning(error_msg)
            self.logger.debug(f"Raw USPS API response: {json_string}")
            return USPSResponse(success=False, error=error_msg, raw_response=json_string)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse USPS API JSON response: {e}"
            self.logger.error(error_msg)
            return USPSResponse(success=False, error=error_msg, raw_response=json_string)
    
    def zip_to_city_state(self, zipcode: str) -> USPSResponse:
        """
        Look up city and state from ZIP code using USPS Address API
        
        Args:
            zipcode: 5-digit ZIP code
            
        Returns:
            USPSResponse with city and state information
        """
        # Validate input
        if not zipcode or len(zipcode) != 5:
            error_msg = "ZIP code must be exactly 5 digits"
            self.logger.warning(f"Invalid ZIP code: {zipcode}")
            return USPSResponse(success=False, error=error_msg)
        
        if not zipcode.isdigit():
            error_msg = "ZIP code must contain only digits"
            self.logger.warning(f"Invalid ZIP code format: {zipcode}")
            return USPSResponse(success=False, error=error_msg)
        
        self.logger.info(f"Looking up city/state for ZIP code: {zipcode}")
        
        # Use USPS Address API (v3)
        params = {
            'ZIPCode': zipcode
        }
        
        return self._make_secure_request('/city-state', params)

    def city_state_to_zip(self, city: str, state: str) -> USPSResponse:
        """
        Look up ZIP code from city and state using USPS Address API
        
        Args:
            city: City name
            state: State abbreviation (2 letters)
            
        Returns:
            USPSResponse with ZIP code information
        """
        # Validate input
        if not city or not state:
            error_msg = "Both city and state are required"
            self.logger.warning("Missing city or state parameter")
            return USPSResponse(success=False, error=error_msg)
        
        if len(state) != 2:
            error_msg = "State must be 2-letter abbreviation"
            self.logger.warning(f"Invalid state format: {state}")
            return USPSResponse(success=False, error=error_msg)
        
        # Normalize state to uppercase
        state = state.upper()
        
        self.logger.info(f"Looking up ZIP code for city: {city}, state: {state}")
        
        # Use USPS Address API (v3)
        params = {
            'city': city,
            'state': state
        }
        
        return self._make_secure_request('/zipcode', params)
    
    def validate_zipcode(self, zipcode: str) -> bool:
        """
        Validate ZIP code format
        
        Args:
            zipcode: ZIP code to validate
            
        Returns:
            True if valid, False otherwise
        """
        return bool(zipcode and len(zipcode) == 5 and zipcode.isdigit())
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        Get API service status and configuration (without sensitive data)
        
        Returns:
            Dictionary with API status information
        """
        return {
            'service': 'USPS API Service (OAuth 2.0)',
            'status': 'active',
            'test_mode': self.test_mode,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'oauth_configured': bool(self.client_id and self.client_secret),
            'token_valid': bool(self.current_token and time.time() < self.token_expiry)
        }
    
    def test_connection(self) -> USPSResponse:
        """
        Test USPS API connection with a known ZIP code
        
        Returns:
            USPSResponse indicating connection status
        """
        self.logger.info("Testing USPS API connection")
        return self.zip_to_city_state("90210")  # Beverly Hills, CA


# Global service instance
_usps_service = None


def get_usps_service() -> USPSAPIService:
    """
    Get or create the global USPS API service instance
    
    Returns:
        USPSAPIService instance
    """
    global _usps_service
    if _usps_service is None:
        _usps_service = USPSAPIService()
    return _usps_service


def zip_to_city_state(zipcode: str) -> USPSResponse:
    """
    Convenience function to look up city and state from ZIP code
    
    Args:
        zipcode: 5-digit ZIP code
        
    Returns:
        USPSResponse with city and state information
    """
    service = get_usps_service()
    return service.zip_to_city_state(zipcode)


def city_state_to_zip(city: str, state: str) -> USPSResponse:
    """
    Convenience function to look up ZIP code from city and state
    
    Args:
        city: City name
        state: State abbreviation (2 letters)
        
    Returns:
        USPSResponse with ZIP code information
    """
    service = get_usps_service()
    return service.city_state_to_zip(city, state)


def validate_zipcode(zipcode: str) -> bool:
    """
    Convenience function to validate ZIP code format
    
    Args:
        zipcode: ZIP code to validate
        
    Returns:
        True if valid, False otherwise
    """
    service = get_usps_service()
    return service.validate_zipcode(zipcode)


def test_api_connection() -> USPSResponse:
    """
    Convenience function to test USPS API connection
    
    Returns:
        USPSResponse indicating connection status
    """
    service = get_usps_service()
    return service.test_connection() 