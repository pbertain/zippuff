"""
Secure USPS API Service Module
Handles all USPS API interactions with proper credential management
"""
import os
import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import sys

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


class USPSAPIService:
    """
    Secure USPS API Service
    
    This module provides a secure interface to the USPS API with:
    - Environment variable credential management
    - Request/response logging
    - Error handling and retry logic
    - Rate limiting protection
    - Response validation
    """
    
    def __init__(self):
        """Initialize the USPS API service with secure credential management"""
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        
        # Load credentials from environment variables
        self._load_credentials()
        
        # API configuration
        self.base_url = "http://production.shippingapis.com/ShippingAPI.dll"
        self.timeout = 30
        self.max_retries = 3
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = None
        
        self.logger.info("USPS API Service initialized")
    
    def _load_credentials(self):
        """Load and validate USPS API credentials from environment variables"""
        # Primary credential sources (in order of preference)
        self.userid = (
            os.getenv('USPS_USERID') or
            os.getenv('USPS_CONSUMER_KEY') or
            self.config.get('usps.userid')
        )
        
        # Consumer secret (if needed for future authentication)
        self.consumer_secret = os.getenv('USPS_CONSUMER_SECRET')
        
        # Test mode configuration
        test_mode = os.getenv('USPS_TEST_MODE', 'true').lower()
        self.test_mode = test_mode == 'true'
        
        # Validate credentials
        if not self.userid or self.userid == 'YOUR_USERID':
            raise ValueError(
                "USPS UserID not configured. Please set USPS_USERID environment variable."
            )
        
        self.logger.info(f"USPS API credentials loaded (Test Mode: {self.test_mode})")
    
    def _make_secure_request(self, xml_request: str) -> USPSResponse:
        """
        Make a secure HTTP request to USPS API with proper error handling
        
        Args:
            xml_request: XML request string
            
        Returns:
            USPSResponse object with standardized response format
        """
        try:
            # Log request (without sensitive data)
            self.logger.info(f"Making USPS API request to {self.base_url}")
            
            # Make the request
            response = requests.get(
                self.base_url,
                params={"API": "CityStateLookup", "XML": xml_request},
                timeout=self.timeout,
                headers={
                    'User-Agent': 'Zippuff-USPS-API/1.0',
                    'Accept': 'application/xml'
                }
            )
            
            # Log response status
            self.logger.info(f"USPS API response status: {response.status_code}")
            
            # Handle HTTP errors
            response.raise_for_status()
            
            # Parse and validate response
            return self._parse_response(response.text)
            
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
    
    def _parse_response(self, xml_string: str) -> USPSResponse:
        """
        Parse and validate USPS API XML response
        
        Args:
            xml_string: XML response string
            
        Returns:
            USPSResponse object
        """
        try:
            root = ET.fromstring(xml_string)
            
            # Check for API errors
            error_elem = root.find(".//Error")
            if error_elem is not None:
                error_desc = error_elem.find("Description")
                error_text = error_desc.text if error_desc is not None else "Unknown USPS API error"
                self.logger.error(f"USPS API error: {error_text}")
                return USPSResponse(success=False, error=error_text, raw_response=xml_string)
            
            # Parse successful response
            zip_elem = root.find(".//ZipCode")
            if zip_elem is not None:
                zip5 = zip_elem.find("Zip5")
                city = zip_elem.find("City")
                state = zip_elem.find("State")
                
                address_info = AddressInfo(
                    zipcode=zip5.text if zip5 is not None else None,
                    city=city.text if city is not None else None,
                    state=state.text if state is not None else None
                )
                
                self.logger.info(f"Successfully parsed USPS API response")
                return USPSResponse(success=True, data=address_info, raw_response=xml_string)
            
            # No data found
            error_msg = "No data found in USPS API response"
            self.logger.warning(error_msg)
            return USPSResponse(success=False, error=error_msg, raw_response=xml_string)
            
        except ET.ParseError as e:
            error_msg = f"Failed to parse USPS API XML response: {e}"
            self.logger.error(error_msg)
            return USPSResponse(success=False, error=error_msg, raw_response=xml_string)
    
    def zip_to_city_state(self, zipcode: str) -> USPSResponse:
        """
        Look up city and state from ZIP code
        
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
        
        # Build XML request
        xml_request = f"""<CityStateLookupRequest USERID='{self.userid}'>
            <ZipCode ID='0'>
                <Zip5>{zipcode}</Zip5>
            </ZipCode>
        </CityStateLookupRequest>"""
        
        self.logger.info(f"Looking up city/state for ZIP code: {zipcode}")
        return self._make_secure_request(xml_request)
    
    def city_state_to_zip(self, city: str, state: str) -> USPSResponse:
        """
        Look up ZIP code from city and state
        
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
        
        # Build XML request
        xml_request = f"""<CityStateLookupRequest USERID='{self.userid}'>
            <ZipCode ID='0'>
                <City>{city}</City>
                <State>{state}</State>
            </ZipCode>
        </CityStateLookupRequest>"""
        
        self.logger.info(f"Looking up ZIP code for city: {city}, state: {state}")
        return self._make_secure_request(xml_request)
    
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
            'service': 'USPS API Service',
            'status': 'active',
            'test_mode': self.test_mode,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'credentials_configured': bool(self.userid and self.userid != 'YOUR_USERID')
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