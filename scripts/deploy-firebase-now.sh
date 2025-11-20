#!/bin/bash

# Firebase Deployment Script - Option 1 (Hybrid)
# Deploys backend to Cloud Run and frontend to Firebase Hosting

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

cd "$(dirname "$0")/.."

print_step "🚀 Starting Firebase Deployment (Option 1: Hybrid)"
echo ""

# Check prerequisites
print_step "Checking prerequisites..."
command -v gcloud >/dev/null || { print_error "gcloud not found"; exit 1; }
command -v firebase >/dev/null || { print_error "firebase CLI not found"; exit 1; }
print_info "✅ Prerequisites met"

# Check authentication
print_step "Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q .; then
    print_warn "Not authenticated with Google Cloud"
    print_info "Please run: gcloud auth login"
    print_info "Then run this script again"
    exit 1
fi
print_info "✅ Google Cloud authenticated"

# Check project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    print_warn "No Google Cloud project set"
    print_info "Available projects:"
    gcloud projects list --format="table(projectId,name)" || true
    print_info "Please set project with: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi
print_info "✅ Using project: $PROJECT_ID"

# Enable APIs (skip if permission denied - they may already be enabled)
print_step "Checking required APIs..."
print_info "APIs should be enabled. If deployment fails, enable them manually:"
print_info "Visit: https://console.cloud.google.com/apis/library?project=$PROJECT_ID"

# Check Firebase
print_step "Checking Firebase..."
if ! firebase projects:list &>/dev/null; then
    print_warn "Not authenticated with Firebase"
    print_info "Please run: firebase login"
    print_info "Then run this script again"
    exit 1
fi

# Initialize Firebase if needed
if [ ! -f ".firebaserc" ]; then
    print_info "Initializing Firebase..."
    firebase use --add "$PROJECT_ID" || {
        print_error "Failed to initialize Firebase"
        exit 1
    }
fi
print_info "✅ Firebase ready"

# Deploy backend
print_step "Deploying backend to Cloud Run..."
cd backend

# Check if backend is already deployed
EXISTING_SERVICE=$(gcloud run services describe sauti-ai-backend \
  --region us-central1 \
  --format 'value(name)' 2>/dev/null || echo "")

if [ -z "$EXISTING_SERVICE" ]; then
    print_info "Deploying new service..."
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
      --set-env-vars ENVIRONMENT=production \
      --project "$PROJECT_ID" || {
        print_error "Backend deployment failed!"
        exit 1
    }
else
    print_info "Service already exists, updating..."
    gcloud run deploy sauti-ai-backend \
      --source . \
      --platform managed \
      --region us-central1 \
      --port 8000 \
      --memory 2Gi \
      --cpu 2 \
      --project "$PROJECT_ID" || {
        print_error "Backend update failed!"
        exit 1
    }
fi

BACKEND_URL=$(gcloud run services describe sauti-ai-backend \
  --region us-central1 \
  --format 'value(status.url)' \
  --project "$PROJECT_ID")

print_info "✅ Backend deployed: $BACKEND_URL"
cd ..

# Get environment variables
print_step "Environment Variables Setup"
echo ""
print_warn "⚠️  IMPORTANT: You need to set environment variables!"
echo ""
print_info "Backend URL: $BACKEND_URL"
echo ""
print_info "Please provide the following (from your Supabase dashboard):"
echo "  1. SUPABASE_URL"
echo "  2. SUPABASE_KEY (anon key)"
echo "  3. SUPABASE_SERVICE_KEY (service role key)"
echo "  4. DATABASE_URL (PostgreSQL connection string)"
echo ""
read -p "Do you want to set environment variables now? (y/n): " set_env

if [ "$set_env" = "y" ]; then
    read -p "SUPABASE_URL: " SUPABASE_URL
    read -p "SUPABASE_KEY: " SUPABASE_KEY
    read -p "SUPABASE_SERVICE_KEY: " SUPABASE_SERVICE_KEY
    read -p "DATABASE_URL: " DATABASE_URL
    
    # Get Firebase hosting URL
    FIREBASE_PROJECT=$(firebase use --json 2>/dev/null | grep -o '"alias":"[^"]*"' | cut -d'"' -f4 || echo "$PROJECT_ID")
    FRONTEND_URL="https://${FIREBASE_PROJECT}.web.app"
    
    print_info "Setting environment variables..."
    gcloud run services update sauti-ai-backend \
      --update-env-vars \
        ENVIRONMENT=production,\
        SUPABASE_URL="$SUPABASE_URL",\
        SUPABASE_KEY="$SUPABASE_KEY",\
        SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY",\
        DATABASE_URL="$DATABASE_URL",\
        CORS_ORIGINS="$FRONTEND_URL,https://${FIREBASE_PROJECT}.firebaseapp.com",\
        PRODUCTION_ORIGINS="$FRONTEND_URL,https://${FIREBASE_PROJECT}.firebaseapp.com",\
        PUBLIC_BACKEND_ORIGIN="$BACKEND_URL" \
      --region us-central1 \
      --project "$PROJECT_ID"
    
    print_info "✅ Environment variables set"
else
    print_warn "Skipping environment variables. Set them later with:"
    echo "  gcloud run services update sauti-ai-backend --update-env-vars KEY=value --region us-central1"
fi

# Deploy frontend
print_step "Building and deploying frontend..."
cd frontend

# Create .env.production if it doesn't exist
if [ ! -f ".env.production" ]; then
    print_info "Creating .env.production..."
    cat > .env.production << EOF
VITE_API_URL=$BACKEND_URL
VITE_SUPABASE_URL=${SUPABASE_URL:-}
VITE_SUPABASE_ANON_KEY=${SUPABASE_KEY:-}
EOF
    print_warn "⚠️  Please update frontend/.env.production with your Supabase credentials"
fi

# Update API URL in .env.production
if [ -f ".env.production" ]; then
    if grep -q "VITE_API_URL=" .env.production; then
        sed -i "s|VITE_API_URL=.*|VITE_API_URL=$BACKEND_URL|" .env.production
    else
        echo "VITE_API_URL=$BACKEND_URL" >> .env.production
    fi
fi

print_info "Building frontend..."
npm run build || {
    print_error "Frontend build failed!"
    exit 1
}

cd ..

print_info "Deploying to Firebase Hosting..."
firebase deploy --only hosting || {
    print_error "Frontend deployment failed!"
    exit 1
}

# Get final URLs
FIREBASE_PROJECT=$(firebase use --json 2>/dev/null | grep -o '"alias":"[^"]*"' | cut -d'"' -f4 || echo "$PROJECT_ID")
FRONTEND_URL="https://${FIREBASE_PROJECT}.web.app"

echo ""
print_info "✅ Deployment Complete!"
echo ""
print_info "Frontend: $FRONTEND_URL"
print_info "Backend:  $BACKEND_URL"
echo ""
print_info "Next steps:"
echo "  1. Test backend: curl $BACKEND_URL/health"
echo "  2. Visit frontend: $FRONTEND_URL"
echo "  3. If environment variables weren't set, configure them now"
echo "  4. Update CORS if needed"

