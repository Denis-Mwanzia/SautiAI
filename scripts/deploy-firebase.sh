#!/bin/bash

# Firebase & Cloud Run Deployment Script
# Deploys backend to Cloud Run and frontend to Firebase Hosting

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

# Check if firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    print_error "Firebase CLI not found!"
    print_info "Install with: npm install -g firebase-tools"
    exit 1
fi

print_step "🚀 Starting Firebase & Cloud Run Deployment..."
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Get backend URL
print_step "Checking backend deployment..."
BACKEND_URL=$(gcloud run services describe sauti-ai-backend \
  --region us-central1 \
  --format 'value(status.url)' 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    print_warn "Backend not found. Deploying backend first..."
    
    # Check if we're in the right project
    print_info "Current GCP project: $(gcloud config get-value project)"
    print_info "Continuing with backend deployment..."
    
    # Deploy backend
    print_step "Deploying backend to Cloud Run..."
    cd backend
    
    gcloud run deploy sauti-ai-backend \
      --source . \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --port 8000 \
      --memory 2Gi \
      --cpu 2 \
      --min-instances 1 \
      --max-instances 10 \
      --timeout 300 \
      --set-env-vars ENVIRONMENT=production || {
        print_error "Backend deployment failed!"
        exit 1
    }
    
    BACKEND_URL=$(gcloud run services describe sauti-ai-backend \
      --region us-central1 \
      --format 'value(status.url)')
    
    print_info "✅ Backend deployed: $BACKEND_URL"
    print_warn "⚠️  Don't forget to set environment variables!"
    print_info "Run: gcloud run services update sauti-ai-backend --update-env-vars KEY=value --region us-central1"
    cd ..
else
    print_info "✅ Backend already deployed: $BACKEND_URL"
fi

# Get Firebase project ID
FIREBASE_PROJECT=$(firebase projects:list 2>/dev/null | grep -oP '(?<=\[).*?(?=\])' | head -1 || echo "")

if [ -z "$FIREBASE_PROJECT" ]; then
    print_warn "No Firebase project found."
    print_error "Please run 'firebase init' first or set FIREBASE_PROJECT_ID environment variable"
    exit 1
fi

print_info "Firebase project: $FIREBASE_PROJECT"

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    print_step "Building frontend..."
    cd frontend
    
    # Check for .env.production
    if [ ! -f ".env.production" ]; then
        print_warn ".env.production not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env.production
            print_warn "⚠️  Please update frontend/.env.production with correct values!"
            print_info "Required: VITE_API_URL=$BACKEND_URL"
        else
            print_error ".env.example not found!"
            exit 1
        fi
    fi
    
    # Update API URL if needed
    if grep -q "VITE_API_URL=" frontend/.env.production; then
        sed -i "s|VITE_API_URL=.*|VITE_API_URL=$BACKEND_URL|" frontend/.env.production
        print_info "Updated VITE_API_URL to $BACKEND_URL"
    else
        echo "VITE_API_URL=$BACKEND_URL" >> frontend/.env.production
        print_info "Added VITE_API_URL to .env.production"
    fi
    
    npm run build || {
        print_error "Frontend build failed!"
        exit 1
    }
    cd ..
else
    print_info "Frontend already built"
fi

# Deploy frontend
print_step "Deploying frontend to Firebase Hosting..."
firebase deploy --only hosting || {
    print_error "Frontend deployment failed!"
    exit 1
}

# Get frontend URL
FRONTEND_URL="https://${FIREBASE_PROJECT}.web.app"

echo ""
print_info "✅ Deployment complete!"
echo ""
print_info "Frontend: $FRONTEND_URL"
print_info "Backend:  $BACKEND_URL"
echo ""
print_warn "⚠️  Next steps:"
print_info "1. Update backend CORS to include: $FRONTEND_URL"
print_info "   Run: gcloud run services update sauti-ai-backend \\"
print_info "     --update-env-vars CORS_ORIGINS=$FRONTEND_URL,https://${FIREBASE_PROJECT}.firebaseapp.com \\"
print_info "     --update-env-vars PRODUCTION_ORIGINS=$FRONTEND_URL,https://${FIREBASE_PROJECT}.firebaseapp.com \\"
print_info "     --region us-central1"
echo ""
print_info "2. Set all required environment variables in Cloud Run"
print_info "3. Test the deployment: curl $BACKEND_URL/health"

