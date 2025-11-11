#!/bin/bash

# Fix the duplicated API key in Secret Manager
# The key was accidentally stored 4 times instead of once

PROJECT_ID=socal-deal-finder

echo "Fetching current secret..."
FULL_KEY=$(gcloud secrets versions access latest --secret=anthropic-api-key --project=$PROJECT_ID)

echo "Current key length: ${#FULL_KEY} characters"

# The key is duplicated 4 times. Extract just the first occurrence.
# A valid Anthropic key is approximately 108 characters
CORRECT_KEY=$(echo "$FULL_KEY" | head -c 108)

echo "Corrected key length: ${#CORRECT_KEY} characters"
echo "Corrected key format: ${CORRECT_KEY:0:15}...${CORRECT_KEY: -10}"

# Update the secret with the correct key
echo ""
echo "Updating secret..."
echo -n "$CORRECT_KEY" | gcloud secrets versions add anthropic-api-key \
  --data-file=- \
  --project=$PROJECT_ID

echo ""
echo "✓ Secret updated successfully!"
echo ""
echo "Verifying..."
NEW_KEY=$(gcloud secrets versions access latest --secret=anthropic-api-key --project=$PROJECT_ID)
echo "New key length: ${#NEW_KEY} characters"
echo "New key format: ${NEW_KEY:0:15}...${NEW_KEY: -10}"

if [ ${#NEW_KEY} -eq 108 ]; then
    echo ""
    echo "✅ Secret is now correct! You can now test the search agent."
else
    echo ""
    echo "⚠ Warning: Key length is ${#NEW_KEY}, expected ~108"
fi
