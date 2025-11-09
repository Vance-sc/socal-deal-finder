#!/bin/bash

# Deployment script for SoCal M&A Deal Finder to Google Cloud Run

set -e

# Configuration
PROJECT_ID="socal-deal-finder"
REGION="us-west1"
SERVICE_NAME="socal-deal-finder"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "================================"
echo "SoCal M&A Deal Finder Deployment"
echo "================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
echo "Setting GCP project to: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo ""
echo "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable gmail.googleapis.com

# Build the container
echo ""
echo "Building Docker container..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --timeout 900 \
    --max-instances 1 \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo ""
echo "✓ Deployment complete!"
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "Next steps:"
echo "1. Set up Cloud Scheduler to trigger the scraper weekly"
echo "2. Configure service account credentials for Google Sheets/Gmail"
echo "3. Test the scraper by visiting the service URL"
