"""
USPS API Client for ZIP code and city/state lookups
"""
import logging
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import os


@dataclass
class AddressInfo:
    """Data class for address information"""
    zipcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None


class USPSClient:
    """Secure USPS API client with proper credential management"""
    
    def __init__(self, userid: str, test_mode: bool = True):
        """
        Initialize USPS client
        
        Args:
            userid: USPS API user ID
            test_mode: Whether to use test mode (default: True)
        """
        self.userid = userid
        self.test_mode = test_mode
        self.base_url = "http://production.shippingapis.com/ShippingAPI.dll"
        self.logger = logging.getLogger(__name__)
        
        if not userid or userid == "YOUR_USERID":
            raise ValueError("USPS UserID must be provided")
    
    def _make_request(self, xml_request: str) -> str:
        """
        Make HTTP request to USPS API
        
        Args:
            xml_request: XML request string
            
        Returns:
            XML response string
        """
        try:
            response = requests.get(
                self.base_url,
                params={"API": "CityStateLookup", "XML": xml_request},
                timeout=30
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"USPS API request failed: {e}")
            raise
    
    def _parse_xml_response(self, xml_string: str) -> AddressInfo:
        """
        Parse XML response from USPS API
        
        Args:
            xml_string: XML response string
            
        Returns:
            AddressInfo object
        """
        try:
            root = ET.fromstring(xml_string)
            
            # Check for errors
            error_elem = root.find(".//Error")
            if error_elem is not None:
                error_desc = error_elem.find("Description")
                error_text = error_desc.text if error_desc is not None else "Unknown error"
                return AddressInfo(error=error_text)
            
            # Parse successful response
            zip_elem = root.find(".//ZipCode")
            if zip_elem is not None:
                zip5 = zip_elem.find("Zip5")
                city = zip_elem.find("City")
                state = zip_elem.find("State")
                
                return AddressInfo(
                    zipcode=zip5.text if zip5 is not None else None,
                    city=city.text if city is not None else None,
                    state=state.text if state is not None else None
                )
            
            return AddressInfo(error="No data found in response")
            
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse XML response: {e}")
            return AddressInfo(error=f"Invalid XML response: {e}")
    
    def zip_to_city_state(self, zipcode: str) -> AddressInfo:
        """
        Look up city and state from ZIP code
        
        Args:
            zipcode: 5-digit ZIP code
            
        Returns:
            AddressInfo with city and state information
        """
        if not zipcode or len(zipcode) != 5:
            return AddressInfo(error="ZIP code must be 5 digits")
        
        xml_request = f"""<CityStateLookupRequest USERID='{self.userid}'>
            <ZipCode ID='0'>
                <Zip5>{zipcode}</Zip5>
            </ZipCode>
        </CityStateLookupRequest>"""
        
        try:
            response = self._make_request(xml_request)
            return self._parse_xml_response(response)
        except Exception as e:
            self.logger.error(f"ZIP to city/state lookup failed: {e}")
            return AddressInfo(error=str(e))
    
    def city_state_to_zip(self, city: str, state: str) -> AddressInfo:
        """
        Look up ZIP code from city and state
        
        Args:
            city: City name
            state: State abbreviation (2 letters)
            
        Returns:
            AddressInfo with ZIP code information
        """
        if not city or not state:
            return AddressInfo(error="City and state are required")
        
        if len(state) != 2:
            return AddressInfo(error="State must be 2-letter abbreviation")
        
        xml_request = f"""<CityStateLookupRequest USERID='{self.userid}'>
            <ZipCode ID='0'>
                <City>{city}</City>
                <State>{state}</State>
            </ZipCode>
        </CityStateLookupRequest>"""
        
        try:
            response = self._make_request(xml_request)
            return self._parse_xml_response(response)
        except Exception as e:
            self.logger.error(f"City/state to ZIP lookup failed: {e}")
            return AddressInfo(error=str(e))
    
    def validate_zipcode(self, zipcode: str) -> bool:
        """
        Validate ZIP code format
        
        Args:
            zipcode: ZIP code to validate
            
        Returns:
            True if valid, False otherwise
        """
        return bool(zipcode and len(zipcode) == 5 and zipcode.isdigit()) 