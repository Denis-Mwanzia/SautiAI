#!/bin/bash

# Google Cloud Platform Setup Script for Sauti AI
# Sets up GCP project, APIs, and initial configuration

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

print_step "🔧 Setting up Google Cloud Platform for Sauti AI..."
echo ""

# Get or set project ID
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ]; then
    read -p "Enter your GCP Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
else
    PROJECT_ID="$CURRENT_PROJECT"
    print_info "Using GCP Project: $PROJECT_ID"
    read -p "Use this project? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        read -p "Enter your GCP Project ID: " PROJECT_ID
        gcloud config set project "$PROJECT_ID"
    fi
fi

# Get or set region
read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}
print_info "Using region: $REGION"

# Enable billing (check)
print_step "Checking billing..."
BILLING_ACCOUNT=$(gcloud beta billing projects describe "$PROJECT_ID" --format="value(billingAccountName)" 2>/dev/null || echo "")
if [ -z "$BILLING_ACCOUNT" ]; then
    print_warn "⚠️  Billing is not enabled for this project!"
    print_info "Cloud Run and other services require billing. Please enable it:"
    echo "  https://console.cloud.google.com/billing?project=$PROJECT_ID"
    read -p "Press Enter after enabling billing..."
else
    print_info "✅ Billing is enabled"
fi

# Enable required APIs
print_step "Enabling required Google Cloud APIs..."
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
    "secretmanager.googleapis.com"
    "aiplatform.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "iam.googleapis.com"
)

for api in "${APIS[@]}"; do
    if gcloud services list --enabled --project="$PROJECT_ID" --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        print_info "  ✓ $api already enabled"
    else
        print_info "  Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID"
    fi
done

# Create Artifact Registry repository
print_step "Setting up Artifact Registry..."
REPO_NAME="sauti-ai"
if gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" &>/dev/null; then
    print_info "  ✓ Artifact Registry repository already exists"
else
    print_info "  Creating Artifact Registry repository..."
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Sauti AI Docker images" \
        --project="$PROJECT_ID"
    print_info "  ✓ Repository created"
fi

# Create service account
print_step "Setting up service account..."
SERVICE_ACCOUNT="sauti-ai-backend@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT" --project="$PROJECT_ID" &>/dev/null; then
    print_info "  ✓ Service account already exists"
else
    print_info "  Creating service account..."
    gcloud iam service-accounts create sauti-ai-backend \
        --display-name="Sauti AI Backend Service Account" \
        --description="Service account for Sauti AI backend Cloud Run service" \
        --project="$PROJECT_ID"
    print_info "  ✓ Service account created"
fi

# Grant permissions
print_step "Granting permissions..."
ROLES=(
    "roles/aiplatform.user"
    "roles/secretmanager.secretAccessor"
    "roles/run.invoker"
)

for role in "${ROLES[@]}"; do
    print_info "  Granting $role..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SERVICE_ACCOUNT}" \
        --role="$role" \
        --condition=None \
        --quiet || print_warn "  Could not grant $role (may already be granted)"
done

# Configure Docker authentication
print_step "Configuring Docker authentication..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Create secrets placeholder
print_step "Setting up Secret Manager..."
print_info "  You'll need to create the following secrets:"
echo ""
echo "  Required secrets:"
echo "    - supabase-url"
echo "    - supabase-key"
echo "    - supabase-service-key"
echo "    - database-url"
echo "    - vertex-ai-project"
echo ""
echo "  Optional secrets:"
echo "    - gcp-service-account (JSON content)"
echo "    - twitter-bearer-token"
echo "    - facebook-access-token"
echo "    - slack-webhook-url"
echo "    - sentry-dsn"
echo ""
print_info "  Create secrets with:"
echo "    echo -n 'value' | gcloud secrets create SECRET_NAME --data-file=- --project=$PROJECT_ID"
echo ""

# Summary
echo ""
print_step "✅ Setup Complete!"
echo ""
print_info "Project ID: $PROJECT_ID"
print_info "Region: $REGION"
print_info "Artifact Registry: $REPO_NAME"
print_info "Service Account: $SERVICE_ACCOUNT"
echo ""
print_info "Next steps:"
echo "  1. Create secrets in Secret Manager (see above)"
echo "  2. Run ./scripts/deploy-gcp.sh to deploy the application"
echo ""

