#!/bin/bash

# Zippuff Status Check Script
# This script checks the status of the Zippuff services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Checking Zippuff Service Status...${NC}"
echo ""

# Check if deployment.env exists and load it
if [ -f "deployment.env" ]; then
    set -a
    source deployment.env
    set +a
    echo -e "${GREEN}✅ Deployment environment loaded${NC}"
else
    echo -e "${YELLOW}⚠️  deployment.env not found, using default values${NC}"
fi

# Get the first host from deployment.env or use default
HOST=${ZIPPUFF_HOST_1:-host77.nird.club}
USER=${ZIPPUFF_USER:-ansible}

echo -e "${BLUE}📡 Checking services on $HOST...${NC}"
echo ""

# Check service status
echo -e "${YELLOW}🔧 Checking zippuff-api service...${NC}"
ssh -i ~/.ssh/keys/nirdclub__id_ed25519 $USER@$HOST "sudo systemctl status zippuff-api --no-pager" || echo -e "${RED}❌ zippuff-api service not found or not running${NC}"

echo ""
echo -e "${YELLOW}🔌 Checking port 59080...${NC}"
ssh -i ~/.ssh/keys/nirdclub__id_ed25519 $USER@$HOST "sudo netstat -tlnp | grep :59080" || echo -e "${RED}❌ Port 59080 not listening${NC}"

echo ""
echo -e "${YELLOW}📁 Checking application directory...${NC}"
ssh -i ~/.ssh/keys/nirdclub__id_ed25519 $USER@$HOST "ls -la /opt/zippuff/" || echo -e "${RED}❌ Application directory not found${NC}"

echo ""
echo -e "${YELLOW}🔑 Checking environment file...${NC}"
ssh -i ~/.ssh/keys/nirdclub__id_ed25519 $USER@$HOST "sudo cat /opt/zippuff/.env" || echo -e "${RED}❌ Environment file not found${NC}"

echo ""
echo -e "${GREEN}✅ Status check completed!${NC}"
echo -e "${BLUE}🔌 API should be accessible at: http://$HOST:59080${NC}"
echo -e "${BLUE}🌐 Web interface: Configured by your nginx playbook${NC}" 