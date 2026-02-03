#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Firebase Frontend Deployment ===${NC}"

# Check arguments
BACKEND_URL="$1"

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}Error: Backend URL is required.${NC}"
    echo "Usage: ./deploy_frontend.sh <BACKEND_URL>"
    exit 1
fi

# Check tools
if ! command -v firebase &> /dev/null; then
    echo -e "${RED}Error: firebase-tools is not installed.${NC}"
    echo "Run: npm install -g firebase-tools"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed.${NC}"
    exit 1
fi

echo "Using Backend URL: $BACKEND_URL"

cd Docker/frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Get Project ID from gcloud
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "(unset)" ]; then
    echo -e "${RED}Error: No Google Cloud Project set.${NC}"
    echo "Please set your project: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi
echo "Deploying to Project: $PROJECT_ID"

# Build with env var
echo "Building frontend..."
export VITE_API_URL="$BACKEND_URL"
npm run build

# Deploy
echo "Deploying to Firebase..."
firebase deploy --project "$PROJECT_ID"

echo -e "${GREEN}Frontend deployment complete!${NC}"
