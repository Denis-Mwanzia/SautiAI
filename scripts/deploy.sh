#!/bin/bash

# Sauti AI Deployment Script
# This script builds and deploys the application using Docker Compose

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    print_info "Please create a .env file based on backend/.env.example and frontend/.env.example"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
REQUIRED_VARS=("SUPABASE_URL" "SUPABASE_KEY" "DATABASE_URL" "VITE_SUPABASE_URL" "VITE_SUPABASE_ANON_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

print_info "Starting deployment..."

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Build images
print_info "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
print_info "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 10

# Check health
print_info "Checking service health..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${BACKEND_PORT:-8000}/health || echo "000")
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${FRONTEND_PORT:-80}/health || echo "000")

if [ "$BACKEND_HEALTH" = "200" ]; then
    print_info "Backend is healthy ✓"
else
    print_warn "Backend health check failed (HTTP $BACKEND_HEALTH)"
fi

if [ "$FRONTEND_HEALTH" = "200" ]; then
    print_info "Frontend is healthy ✓"
else
    print_warn "Frontend health check failed (HTTP $FRONTEND_HEALTH)"
fi

# Show logs
print_info "Showing service logs (Ctrl+C to exit)..."
docker-compose -f docker-compose.prod.yml logs -f

