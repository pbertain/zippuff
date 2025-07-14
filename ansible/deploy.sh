#!/bin/bash

# Zippuff Deployment Script
# This script sources the deployment environment and runs the Ansible playbook

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Zippuff Deployment...${NC}"

# Check if deployment.env exists
if [ ! -f "deployment.env" ]; then
    echo -e "${RED}❌ Error: deployment.env file not found!${NC}"
    echo "Please ensure deployment.env exists in the ansible directory."
    exit 1
fi

# Source the deployment environment
echo -e "${YELLOW}📋 Loading deployment environment...${NC}"
set -a  # automatically export all variables
source deployment.env
set +a

# Verify required environment variables
required_vars=("USPS_USERID" "USPS_CONSUMER_KEY" "USPS_CONSUMER_SECRET")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Error: Required environment variable $var is not set!${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables loaded successfully${NC}"

# Export environment variables for Ansible
export USPS_USERID
export USPS_CONSUMER_KEY
export USPS_CONSUMER_SECRET
export USPS_TEST_MODE

# Run Ansible playbook
echo -e "${YELLOW}🔧 Running Ansible playbook...${NC}"
ansible-playbook -i inventory.yml playbook.yml --ask-become-pass

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${YELLOW}🌐 The Zippuff API should now be running on port 59080${NC}"
echo -e "${YELLOW}📱 Web interface should be accessible via nginx${NC}" 