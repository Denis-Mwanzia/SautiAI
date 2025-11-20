#!/bin/bash

# Google Cloud Platform Deployment Script for Sauti AI
# Deploys backend and frontend to Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK not found!"
    print_info "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_step "🚀 Starting Google Cloud Platform Deployment..."
echo ""

# Get or set project ID
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    read -p "Enter your GCP Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
else
    PROJECT_ID="$CURRENT_PROJECT"
    print_info "Using GCP Project: $PROJECT_ID"
fi

# Get or set region
read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}
print_info "Using region: $REGION"

# Enable required APIs
print_step "Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    --project "$PROJECT_ID"

# Create Artifact Registry repository if it doesn't exist
print_step "Setting up Artifact Registry..."
REPO_NAME="sauti-ai"
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    print_info "Creating Artifact Registry repository..."
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --project="$PROJECT_ID"
else
    print_info "Artifact Registry repository already exists"
fi

# Create service account for Cloud Run if it doesn't exist
print_step "Setting up service account..."
SERVICE_ACCOUNT="sauti-ai-backend@${PROJECT_ID}.iam.gserviceaccount.com"
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" &>/dev/null; then
    print_info "Creating service account..."
    gcloud iam service-accounts create sauti-ai-backend \
        --display-name="Sauti AI Backend Service Account" \
        --project="$PROJECT_ID"
    
    # Grant necessary permissions
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/aiplatform.user"
    
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="roles/secretmanager.secretAccessor"
else
    print_info "Service account already exists"
fi

# Set up secrets in Secret Manager
print_step "Setting up secrets in Secret Manager..."
echo ""
print_warn "You'll need to provide the following secrets:"
echo "  1. SUPABASE_URL"
echo "  2. SUPABASE_KEY (anon key)"
echo "  3. SUPABASE_SERVICE_KEY (service role key)"
echo "  4. DATABASE_URL (PostgreSQL connection string)"
echo "  5. VERTEX_AI_PROJECT (usually same as PROJECT_ID)"
echo ""

read -p "Do you want to set up secrets now? (y/n): " setup_secrets
if [ "$setup_secrets" = "y" ]; then
    read -p "SUPABASE_URL: " SUPABASE_URL
    read -p "SUPABASE_KEY: " SUPABASE_KEY
    read -p "SUPABASE_SERVICE_KEY: " SUPABASE_SERVICE_KEY
    read -p "DATABASE_URL: " DATABASE_URL
    read -p "VERTEX_AI_PROJECT (default: $PROJECT_ID): " VERTEX_AI_PROJECT
    VERTEX_AI_PROJECT=${VERTEX_AI_PROJECT:-$PROJECT_ID}
    
    # Create or update secrets
    echo -n "$SUPABASE_URL" | gcloud secrets create supabase-url --data-file=- --project="$PROJECT_ID" 2>/dev/null || \
        echo -n "$SUPABASE_URL" | gcloud secrets versions add supabase-url --data-file=- --project="$PROJECT_ID"
    
    echo -n "$SUPABASE_KEY" | gcloud secrets create supabase-key --data-file=- --project="$PROJECT_ID" 2>/dev/null || \
        echo -n "$SUPABASE_KEY" | gcloud secrets versions add supabase-key --data-file=- --project="$PROJECT_ID"
    
    echo -n "$SUPABASE_SERVICE_KEY" | gcloud secrets create supabase-service-key --data-file=- --project="$PROJECT_ID" 2>/dev/null || \
        echo -n "$SUPABASE_SERVICE_KEY" | gcloud secrets versions add supabase-service-key --data-file=- --project="$PROJECT_ID"
    
    echo -n "$DATABASE_URL" | gcloud secrets create database-url --data-file=- --project="$PROJECT_ID" 2>/dev/null || \
        echo -n "$DATABASE_URL" | gcloud secrets versions add database-url --data-file=- --project="$PROJECT_ID"
    
    echo -n "$VERTEX_AI_PROJECT" | gcloud secrets create vertex-ai-project --data-file=- --project="$PROJECT_ID" 2>/dev/null || \
        echo -n "$VERTEX_AI_PROJECT" | gcloud secrets versions add vertex-ai-project --data-file=- --project="$PROJECT_ID"
    
    # Handle GCP service account JSON if it exists
    if [ -f "$PROJECT_ROOT/gcp-service-account.json" ]; then
        print_info "Uploading GCP service account JSON..."
        gcloud secrets create gcp-service-account --data-file="$PROJECT_ROOT/gcp-service-account.json" --project="$PROJECT_ID" 2>/dev/null || \
            gcloud secrets versions add gcp-service-account --data-file="$PROJECT_ROOT/gcp-service-account.json" --project="$PROJECT_ID"
    else
        print_warn "gcp-service-account.json not found. You may need to upload it manually."
    fi
    
    print_info "✅ Secrets configured"
else
    print_warn "Skipping secrets setup. Make sure to configure them manually in Secret Manager."
fi

# Build and deploy backend
print_step "Building and deploying backend..."
cd "$PROJECT_ROOT/backend"

# Build Docker image
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/sauti-ai-backend"
print_info "Building Docker image..."
gcloud builds submit --tag "$IMAGE_NAME:latest" --project="$PROJECT_ID" --region="$REGION" .

# Deploy to Cloud Run
print_info "Deploying to Cloud Run..."
gcloud run deploy sauti-ai-backend \
    --image "$IMAGE_NAME:latest" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --service-account "$SERVICE_ACCOUNT" \
    --set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,SUPABASE_SERVICE_KEY=supabase-service-key:latest,DATABASE_URL=database-url:latest,VERTEX_AI_PROJECT=vertex-ai-project:latest,GOOGLE_APPLICATION_CREDENTIALS=gcp-service-account:latest" \
    --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO,VERTEX_AI_LOCATION=${REGION}" \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --timeout 300 \
    --port 8000 \
    --project "$PROJECT_ID"

# Get backend URL
BACKEND_URL=$(gcloud run services describe sauti-ai-backend --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")

print_info "✅ Backend deployed: $BACKEND_URL"

# Update CORS and frontend origins
print_step "Updating backend CORS configuration..."
gcloud run services update sauti-ai-backend \
    --update-env-vars="PRODUCTION_ORIGINS=${BACKEND_URL},PUBLIC_BACKEND_ORIGIN=${BACKEND_URL}" \
    --region "$REGION" \
    --project "$PROJECT_ID"

# Build and deploy frontend
print_step "Building and deploying frontend..."
cd "$PROJECT_ROOT/frontend"

# Get frontend environment variables
if [ -z "$SUPABASE_URL" ]; then
    read -p "VITE_SUPABASE_URL: " VITE_SUPABASE_URL
    read -p "VITE_SUPABASE_ANON_KEY: " VITE_SUPABASE_ANON_KEY
fi

# Build Docker image with build args
FRONTEND_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/sauti-ai-frontend"
print_info "Building Docker image..."
gcloud builds submit \
    --tag "$FRONTEND_IMAGE_NAME:latest" \
    --substitutions="_VITE_API_URL=${BACKEND_URL},_VITE_SUPABASE_URL=${VITE_SUPABASE_URL},_VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    .

# Deploy to Cloud Run
print_info "Deploying to Cloud Run..."
gcloud run deploy sauti-ai-frontend \
    --image "$FRONTEND_IMAGE_NAME:latest" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --port 80 \
    --project "$PROJECT_ID"

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe sauti-ai-frontend --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")

print_info "✅ Frontend deployed: $FRONTEND_URL"

# Update backend CORS with frontend URL
print_step "Updating backend CORS with frontend URL..."
gcloud run services update sauti-ai-backend \
    --update-env-vars="PRODUCTION_ORIGINS=${FRONTEND_URL},PUBLIC_BACKEND_ORIGIN=${BACKEND_URL},FRONTEND_ORIGINS=${FRONTEND_URL}" \
    --region "$REGION" \
    --project "$PROJECT_ID"

echo ""
print_step "🎉 Deployment Complete!"
echo ""
print_info "Backend URL: $BACKEND_URL"
print_info "Frontend URL: $FRONTEND_URL"
echo ""
print_info "Next steps:"
echo "  1. Update your Supabase project settings with the new frontend URL"
echo "  2. Test the deployment by visiting: $FRONTEND_URL"
echo "  3. Monitor logs: gcloud run services logs tail sauti-ai-backend --region=$REGION"
echo ""

