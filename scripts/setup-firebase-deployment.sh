#!/bin/bash

# Firebase Deployment Setup Script
# This script helps set up authentication and project configuration

set -e

echo "🔥 Firebase Deployment Setup"
echo "=============================="
echo ""

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found!"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check firebase CLI
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found!"
    echo "Install with: npm install -g firebase-tools"
    exit 1
fi

echo "Step 1: Google Cloud Authentication"
echo "-----------------------------------"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  Not authenticated with Google Cloud"
    echo "Running: gcloud auth login"
    gcloud auth login
else
    echo "✅ Already authenticated"
    gcloud auth list --filter=status:ACTIVE
fi

echo ""
echo "Step 2: Set Google Cloud Project"
echo "-----------------------------------"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$CURRENT_PROJECT" ] || [ "$CURRENT_PROJECT" = "(unset)" ]; then
    echo "⚠️  No project set"
    echo ""
    echo "Available projects:"
    gcloud projects list --format="table(projectId,name)" || true
    echo ""
    read -p "Enter your Google Cloud Project ID (or create new): " PROJECT_ID
    
    if [ -n "$PROJECT_ID" ]; then
        gcloud config set project "$PROJECT_ID"
        echo "✅ Project set to: $PROJECT_ID"
    else
        echo "❌ Project ID required"
        exit 1
    fi
else
    echo "✅ Current project: $CURRENT_PROJECT"
    read -p "Use this project? (y/n): " use_current
    if [ "$use_current" != "y" ]; then
        gcloud projects list --format="table(projectId,name)"
        read -p "Enter project ID: " PROJECT_ID
        gcloud config set project "$PROJECT_ID"
    fi
fi

PROJECT_ID=$(gcloud config get-value project)

echo ""
echo "Step 3: Enable Required APIs"
echo "-----------------------------------"
echo "Enabling Cloud Run, Cloud Build, and Container Registry APIs..."
gcloud services enable run.googleapis.com --project="$PROJECT_ID"
gcloud services enable cloudbuild.googleapis.com --project="$PROJECT_ID"
gcloud services enable containerregistry.googleapis.com --project="$PROJECT_ID"
echo "✅ APIs enabled"

echo ""
echo "Step 4: Firebase Authentication"
echo "-----------------------------------"
if ! firebase projects:list &>/dev/null; then
    echo "⚠️  Not authenticated with Firebase"
    echo "Running: firebase login"
    firebase login
else
    echo "✅ Already authenticated with Firebase"
fi

echo ""
echo "Step 5: Initialize Firebase"
echo "-----------------------------------"
if [ ! -f ".firebaserc" ]; then
    echo "⚠️  Firebase not initialized"
    echo "Linking to project: $PROJECT_ID"
    firebase use --add "$PROJECT_ID"
else
    echo "✅ Firebase already initialized"
    cat .firebaserc
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/deploy-firebase.sh"
echo "2. Or deploy manually following DEPLOY_FIREBASE_FULL_STACK.md"

