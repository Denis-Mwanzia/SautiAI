#!/bin/bash

# Check deployment prerequisites
# This script verifies that all requirements are met before deployment

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

echo "Checking deployment prerequisites..."
echo ""

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI not found"
    exit 1
fi
print_info "gcloud CLI installed"

# Check authentication
CURRENT_ACCOUNT=$(gcloud config get-value account 2>/dev/null)
if [ -z "$CURRENT_ACCOUNT" ]; then
    print_error "Not authenticated. Run: gcloud auth login"
    exit 1
fi

# Check if service account (needs user account)
if echo "$CURRENT_ACCOUNT" | grep -q "iam.gserviceaccount.com"; then
    print_warn "Authenticated as service account: $CURRENT_ACCOUNT"
    print_warn "You need to authenticate with a user account that has Owner/Editor permissions"
    print_warn "Run: gcloud auth login"
    exit 1
fi
print_info "Authenticated as: $CURRENT_ACCOUNT"

# Check project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    print_error "No project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi
print_info "Project: $PROJECT_ID"

# Check APIs
echo ""
echo "Checking required APIs..."
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "artifactregistry.googleapis.com"
    "secretmanager.googleapis.com"
    "aiplatform.googleapis.com"
)

for api in "${APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>/dev/null | grep -q "$api"; then
        print_info "$api enabled"
    else
        print_warn "$api not enabled"
        echo "  Enable with: gcloud services enable $api --project=$PROJECT_ID"
    fi
done

# Check Artifact Registry
echo ""
echo "Checking Artifact Registry..."
if gcloud artifacts repositories describe sauti-ai --location=us-central1 --project="$PROJECT_ID" &>/dev/null; then
    print_info "Artifact Registry repository 'sauti-ai' exists"
else
    print_warn "Artifact Registry repository 'sauti-ai' does not exist"
    echo "  Create with: gcloud artifacts repositories create sauti-ai --repository-format=docker --location=us-central1 --project=$PROJECT_ID"
fi

# Check service account
echo ""
echo "Checking service account..."
if gcloud iam service-accounts describe sauti-ai-backend@${PROJECT_ID}.iam.gserviceaccount.com --project="$PROJECT_ID" &>/dev/null; then
    print_info "Service account 'sauti-ai-backend' exists"
else
    print_warn "Service account 'sauti-ai-backend' does not exist"
    echo "  Create with: gcloud iam service-accounts create sauti-ai-backend --display-name='Sauti AI Backend' --project=$PROJECT_ID"
fi

# Check secrets
echo ""
echo "Checking required secrets..."
REQUIRED_SECRETS=(
    "supabase-url"
    "supabase-key"
    "supabase-service-key"
    "database-url"
    "vertex-ai-project"
)

for secret in "${REQUIRED_SECRETS[@]}"; do
    if gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
        print_info "Secret '$secret' exists"
    else
        print_warn "Secret '$secret' does not exist"
        echo "  Create with: echo -n 'value' | gcloud secrets create $secret --data-file=- --project=$PROJECT_ID"
    fi
done

echo ""
echo "Prerequisites check complete!"
echo ""
echo "If all checks pass, you can proceed with deployment:"
echo "  ./scripts/deploy-gcp.sh"

