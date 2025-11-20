#!/bin/bash

# Script to update secrets in Google Cloud Secret Manager
# Usage: ./scripts/update-secrets.sh

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
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$PROJECT_ID" ]; then
    read -p "Enter your GCP Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

print_step "Updating secrets for project: $PROJECT_ID"
echo ""

# Function to update a secret
update_secret() {
    local secret_name=$1
    local prompt_text=$2
    local is_file=$3
    
    if [ "$is_file" = "true" ]; then
        read -p "$prompt_text (file path, or press Enter to skip): " secret_value
        if [ -n "$secret_value" ] && [ -f "$secret_value" ]; then
            print_info "Updating $secret_name from file..."
            gcloud secrets versions add "$secret_name" \
                --data-file="$secret_value" \
                --project="$PROJECT_ID"
            print_info "✅ $secret_name updated"
        else
            print_warn "Skipping $secret_name (file not found or empty)"
        fi
    else
        read -p "$prompt_text (press Enter to skip): " secret_value
        if [ -n "$secret_value" ]; then
            print_info "Updating $secret_name..."
            echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
                --data-file=- \
                --project="$PROJECT_ID"
            print_info "✅ $secret_name updated"
        else
            print_warn "Skipping $secret_name"
        fi
    fi
}

# Update required secrets
update_secret "supabase-url" "SUPABASE_URL" false
update_secret "supabase-key" "SUPABASE_KEY (anon key)" false
update_secret "supabase-service-key" "SUPABASE_SERVICE_KEY (service role key)" false
update_secret "database-url" "DATABASE_URL" false
update_secret "vertex-ai-project" "VERTEX_AI_PROJECT" false

# Update optional secrets
echo ""
print_step "Optional secrets:"
update_secret "gcp-service-account" "GCP Service Account JSON file path" true
update_secret "twitter-bearer-token" "TWITTER_BEARER_TOKEN" false
update_secret "facebook-access-token" "FACEBOOK_ACCESS_TOKEN" false
update_secret "slack-webhook-url" "SLACK_WEBHOOK_URL" false
update_secret "sentry-dsn" "SENTRY_DSN" false

echo ""
print_info "✅ Secret update complete!"
print_info "Note: Cloud Run services will use the latest version automatically"

