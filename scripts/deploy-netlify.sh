#!/bin/bash

# Netlify Deployment Script
# Run this script to deploy to Netlify

set -e

echo "🚀 Deploying Sauti AI to Netlify..."
echo ""

# Check if build exists
if [ ! -d "frontend/dist" ]; then
    echo "📦 Building frontend..."
    cd frontend
    npm run build
    cd ..
fi

# Deploy to Netlify
echo "🚀 Deploying to Netlify..."
npx netlify deploy --prod --dir=frontend/dist

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Set environment variables in Netlify dashboard:"
echo "   - VITE_SUPABASE_URL"
echo "   - VITE_SUPABASE_ANON_KEY"
echo "   - VITE_API_URL"
echo ""
echo "2. Visit your site: https://app.netlify.com/projects/denismwanzia"


