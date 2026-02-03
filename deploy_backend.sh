#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

REGION="us-west2"
REPO_NAME="backend-repo"
SERVICE_NAME="web-reader-backend"

echo -e "${GREEN}=== Google Cloud Run Backend Deployment ($REGION) ===${NC}"

# 1. Check gcloud installation
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo "Please install it using: brew install --cask google-cloud-sdk"
    exit 1
fi

# 2. Check Project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "(unset)" ]; then
    echo -e "${RED}Error: No Google Cloud Project set.${NC}"
    echo "Please login and set a project:"
    echo "  gcloud auth login"
    echo "  gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "Deploying to Project: ${GREEN}$PROJECT_ID${NC}"
echo -e "Target Region: ${GREEN}$REGION${NC}"

# 3. Enable APIs
echo "Enabling necessary APIs (this may take a minute)..."
gcloud services enable run.googleapis.com \
    texttospeech.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com

# 4. Create Artifact Registry Repo (if not exists)
echo "Ensuring Artifact Registry repository exists in $REGION..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker repository for Web Reader Backend"
    echo "Repository created."
else
    echo "Repository already exists."
fi

# 5. Build and Push Image
IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"
echo "Building and Pushing image to: $IMAGE_URL"
cd Docker/backend
gcloud builds submit --tag "$IMAGE_URL" .

# 6. Deploy to Cloud Run
echo "Deploying Cloud Run Service..."
gcloud run deploy $SERVICE_NAME \
    --image "$IMAGE_URL" \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars ALLOWED_ORIGINS="*"

# 7. Get the URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}Backend deployed successfully!${NC}"
echo -e "Backend URL: ${GREEN}$SERVICE_URL${NC}"

echo ""
echo "Next Step: Deploy the frontend using:"
echo "  ./deploy_frontend.sh \"$SERVICE_URL\""
