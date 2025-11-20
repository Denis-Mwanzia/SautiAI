#!/bin/bash

# Authentication script for environments without browser (WSL, SSH, etc.)

echo "🔐 Google Cloud & Firebase Authentication (No Browser)"
echo "======================================================"
echo ""

# Google Cloud Authentication
echo "Step 1: Google Cloud Authentication"
echo "-----------------------------------"
echo "Visit this URL in your browser (on your local machine or phone):"
echo ""
gcloud auth login --no-launch-browser 2>&1 | grep -A 1 "visit:" | tail -1
echo ""
echo "After signing in, you'll get a verification code."
echo "Paste it here when prompted, or run:"
echo "  gcloud auth login --no-launch-browser"
echo ""

# Firebase Authentication  
echo ""
echo "Step 2: Firebase Authentication"
echo "-----------------------------------"
echo "For Firebase, you have two options:"
echo ""
echo "Option A: Use CI token (recommended for automation)"
echo "  firebase login:ci"
echo "  (This will give you a token you can use)"
echo ""
echo "Option B: Manual login"
echo "  firebase login --no-localhost"
echo "  (Copy the URL and visit it, then paste the token)"
echo ""

