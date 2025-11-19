#!/bin/bash

# Netlify Deployment Script
# This script helps deploy the frontend to Netlify

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

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    print_error "Netlify CLI is not installed!"
    print_info "Install it with: npm install -g netlify-cli"
    exit 1
fi

print_step "Netlify Deployment Setup"
echo ""

# Check if user is logged in
if ! netlify status &> /dev/null; then
    print_warn "Not logged in to Netlify"
    print_info "Logging in..."
    netlify login
fi

# Check if site is linked
if [ ! -f ".netlify/state.json" ] || [ -z "$(cat .netlify/state.json | grep -o '"siteId": "[^"]*"' | cut -d'"' -f4)" ]; then
    print_step "Linking to Netlify site..."
    print_info "You can either:"
    echo "  1. Create a new site"
    echo "  2. Link to an existing site"
    echo ""
    read -p "Create new site? (y/n): " create_new
    
    if [ "$create_new" = "y" ] || [ "$create_new" = "Y" ]; then
        netlify init
    else
        netlify link
    fi
else
    print_info "Site already linked"
    netlify status
fi

echo ""
print_step "Setting up environment variables..."

# Check for required environment variables
REQUIRED_VARS=("VITE_SUPABASE_URL" "VITE_SUPABASE_ANON_KEY" "VITE_API_URL")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    print_warn "Some environment variables are not set:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    print_info "You can set them now or configure them in Netlify dashboard later"
    echo ""
    read -p "Set environment variables now? (y/n): " set_env
    
    if [ "$set_env" = "y" ] || [ "$set_env" = "Y" ]; then
        for var in "${MISSING_VARS[@]}"; do
            read -p "Enter value for $var: " value
            netlify env:set "$var" "$value"
        done
    fi
fi

echo ""
print_step "Deployment Options"
echo ""
echo "1. Deploy to production"
echo "2. Deploy a draft (preview)"
echo "3. Build only (no deploy)"
echo ""
read -p "Choose option (1-3): " deploy_option

case $deploy_option in
    1)
        print_info "Deploying to production..."
        netlify deploy --prod
        ;;
    2)
        print_info "Creating draft deployment..."
        netlify deploy
        ;;
    3)
        print_info "Building only..."
        cd frontend
        npm install
        npm run build
        print_info "Build complete! Output in frontend/dist"
        ;;
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

echo ""
print_info "Deployment complete!"
print_info "Check your site at: $(netlify status --json | grep -o '"siteUrl": "[^"]*"' | cut -d'"' -f4 || echo 'Check Netlify dashboard')"

