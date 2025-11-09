#!/bin/bash

# Set up Cloud Scheduler to run scraper weekly

set -e

PROJECT_ID="socal-deal-finder"
REGION="us-west1"
SERVICE_NAME="socal-deal-finder"
JOB_NAME="${SERVICE_NAME}-weekly"

echo "Setting up Cloud Scheduler..."

# Enable Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# Get Cloud Run service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Cloud Run service not found. Deploy the service first."
    exit 1
fi

echo "Service URL: ${SERVICE_URL}"

# Create or update scheduler job
# Runs every Monday at 8am Pacific Time
gcloud scheduler jobs create http ${JOB_NAME} \
    --location ${REGION} \
    --schedule "0 8 * * 1" \
    --time-zone "America/Los_Angeles" \
    --uri "${SERVICE_URL}" \
    --http-method GET \
    --attempt-deadline 15m \
    --description "Weekly M&A deal scraper for SoCal Business Group" \
    || gcloud scheduler jobs update http ${JOB_NAME} \
       --location ${REGION} \
       --schedule "0 8 * * 1" \
       --time-zone "America/Los_Angeles" \
       --uri "${SERVICE_URL}"

echo ""
echo "✓ Cloud Scheduler configured!"
echo "  Job: ${JOB_NAME}"
echo "  Schedule: Every Monday at 8:00 AM Pacific Time"
echo ""
echo "To test the job manually:"
echo "  gcloud scheduler jobs run ${JOB_NAME} --location ${REGION}"
