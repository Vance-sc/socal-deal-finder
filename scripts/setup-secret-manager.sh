#!/bin/bash

# Google Secret Manager Setup for SoCal Deal Finder
# Run this script to securely store your Anthropic API key in Google Secret Manager

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================================${NC}"
echo -e "${BLUE}  Google Secret Manager Setup - SoCal Deal Finder${NC}"
echo -e "${BLUE}========================================================================${NC}"
echo ""

# Check if running in Cloud Shell
if [ -n "$CLOUD_SHELL" ]; then
    echo -e "${GREEN}✓ Running in Google Cloud Shell${NC}"
else
    echo -e "${YELLOW}⚠ Not in Cloud Shell - make sure gcloud is configured${NC}"
fi

# Get project ID
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-socal-deal-finder}
echo -e "${BLUE}Project ID:${NC} $PROJECT_ID"
echo ""

# Step 1: Enable Secret Manager API
echo -e "${YELLOW}[Step 1/4] Enabling Secret Manager API...${NC}"
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID
echo -e "${GREEN}✓ Secret Manager API enabled${NC}"
echo ""

# Step 2: Get Anthropic API Key
echo -e "${YELLOW}[Step 2/4] Anthropic API Key${NC}"
echo ""
echo "You need your Anthropic API key from https://console.anthropic.com/"
echo ""
echo -e "${BLUE}Your API key should start with: sk-ant-${NC}"
echo ""
read -sp "Enter your Anthropic API key: " ANTHROPIC_API_KEY
echo ""

# Validate API key format
if [[ ! $ANTHROPIC_API_KEY =~ ^sk-ant- ]]; then
    echo -e "${RED}✗ Error: API key should start with 'sk-ant-'${NC}"
    exit 1
fi

echo -e "${GREEN}✓ API key format valid${NC}"
echo ""

# Step 3: Create secret
echo -e "${YELLOW}[Step 3/4] Creating secret in Secret Manager...${NC}"

# Check if secret already exists
if gcloud secrets describe anthropic-api-key --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Secret 'anthropic-api-key' already exists. Creating new version...${NC}"
    echo -n "$ANTHROPIC_API_KEY" | gcloud secrets versions add anthropic-api-key \
        --data-file=- \
        --project=$PROJECT_ID
    echo -e "${GREEN}✓ New secret version created${NC}"
else
    echo "Creating new secret..."
    echo -n "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key \
        --data-file=- \
        --replication-policy="automatic" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✓ Secret created${NC}"
fi

echo ""

# Step 4: Grant access to Cloud Run service account
echo -e "${YELLOW}[Step 4/4] Setting up permissions...${NC}"

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Granting access to service account: $SERVICE_ACCOUNT"

gcloud secrets add-iam-policy-binding anthropic-api-key \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

echo -e "${GREEN}✓ Permissions configured${NC}"
echo ""

# Summary
echo -e "${BLUE}========================================================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${BLUE}========================================================================${NC}"
echo ""
echo "Secret Information:"
echo -e "  Name: ${BLUE}anthropic-api-key${NC}"
echo -e "  Project: ${BLUE}$PROJECT_ID${NC}"
echo -e "  Full Name: ${BLUE}projects/$PROJECT_NUMBER/secrets/anthropic-api-key/versions/latest${NC}"
echo ""
echo "Your Anthropic API key is now securely stored in Google Secret Manager."
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update your .env file to use Secret Manager (already configured)"
echo "2. Test locally: python src/utils.py"
echo "3. Deploy to Cloud Run (will automatically use Secret Manager)"
echo ""
echo -e "${BLUE}View your secret:${NC}"
echo "  https://console.cloud.google.com/security/secret-manager?project=$PROJECT_ID"
echo ""
echo -e "${BLUE}Access secret value programmatically:${NC}"
echo "  gcloud secrets versions access latest --secret=anthropic-api-key --project=$PROJECT_ID"
echo ""
