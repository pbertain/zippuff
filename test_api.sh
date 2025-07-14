#!/bin/bash

# Test script for Zippuff API endpoints

echo "🧪 Testing Zippuff API endpoints..."

# Test health endpoint
echo "📡 Testing health endpoint..."
curl -s http://host78.nird.club:59081/api/health

echo -e "\n\n📡 Testing city-to-zip endpoint..."
curl -s "http://host78.nird.club:59081/api/city-to-zip?city=Davis&state=CA"

echo -e "\n\n📡 Testing config endpoint..."
curl -s http://host78.nird.club:59081/api/config

echo -e "\n\n✅ API tests completed!" 