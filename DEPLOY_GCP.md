# Google Cloud Platform Deployment Guide

Complete guide for deploying Sauti AI to Google Cloud Platform using Cloud Run.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Deployment Methods](#deployment-methods)
- [Configuration](#configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)

## 🎯 Prerequisites

### Required

1. **Google Cloud Platform Account**
   - Active GCP project with billing enabled
   - [Create a project](https://console.cloud.google.com/projectcreate) if needed

2. **Google Cloud SDK (gcloud)**
   - [Install gcloud CLI](https://cloud.google.com/sdk/docs/install)
   - Authenticate: `gcloud auth login`
   - Set default project: `gcloud config set project YOUR_PROJECT_ID`

3. **Docker** (for local builds)
   - [Install Docker](https://docs.docker.com/get-docker/)

4. **Supabase Account**
   - Active Supabase project
   - Database URL and API keys

### Optional

- **Firebase CLI** (for Firebase Hosting alternative)
- **Vertex AI Access** (for AI features)

## 🚀 Quick Start

### 1. Initial Setup

Run the setup script to configure your GCP project:

```bash
./scripts/setup-gcp.sh
```

This script will:
- Enable required GCP APIs
- Create Artifact Registry repository
- Create service account with necessary permissions
- Configure Docker authentication

### 2. Configure Secrets

Create secrets in Secret Manager:

```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Create secrets
echo -n "https://your-project.supabase.co" | \
  gcloud secrets create supabase-url --data-file=- --project=$PROJECT_ID

echo -n "your-anon-key" | \
  gcloud secrets create supabase-key --data-file=- --project=$PROJECT_ID

echo -n "your-service-role-key" | \
  gcloud secrets create supabase-service-key --data-file=- --project=$PROJECT_ID

echo -n "postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres" | \
  gcloud secrets create database-url --data-file=- --project=$PROJECT_ID

echo -n "$PROJECT_ID" | \
  gcloud secrets create vertex-ai-project --data-file=- --project=$PROJECT_ID

# Upload GCP service account JSON (if you have one)
gcloud secrets create gcp-service-account \
  --data-file=./gcp-service-account.json \
  --project=$PROJECT_ID
```

### 3. Deploy

Run the deployment script:

```bash
./scripts/deploy-gcp.sh
```

This will:
- Build Docker images
- Push to Artifact Registry
- Deploy backend to Cloud Run
- Deploy frontend to Cloud Run
- Configure CORS and environment variables

## 📖 Detailed Setup

### Step 1: Project Setup

1. **Create GCP Project** (if needed)
   ```bash
   gcloud projects create sauti-ai-prod --name="Sauti AI Production"
   gcloud config set project sauti-ai-prod
   ```

2. **Enable Billing**
   - Go to [Cloud Console Billing](https://console.cloud.google.com/billing)
   - Link a billing account to your project

3. **Run Setup Script**
   ```bash
   ./scripts/setup-gcp.sh
   ```

### Step 2: Configure Secrets

All sensitive data should be stored in Secret Manager:

**Required Secrets:**
- `supabase-url` - Your Supabase project URL
- `supabase-key` - Supabase anonymous key
- `supabase-service-key` - Supabase service role key
- `database-url` - PostgreSQL connection string
- `vertex-ai-project` - GCP project ID (usually same as your project)

**Optional Secrets:**
- `gcp-service-account` - GCP service account JSON (for Vertex AI)
- `twitter-bearer-token` - Twitter API token
- `facebook-access-token` - Facebook API token
- `slack-webhook-url` - Slack webhook URL
- `sentry-dsn` - Sentry DSN for error tracking

**Create secrets:**
```bash
# Method 1: From file
gcloud secrets create SECRET_NAME --data-file=path/to/file --project=$PROJECT_ID

# Method 2: From stdin
echo -n "secret-value" | gcloud secrets create SECRET_NAME --data-file=- --project=$PROJECT_ID

# Method 3: Update existing secret
echo -n "new-secret-value" | gcloud secrets versions add SECRET_NAME --data-file=- --project=$PROJECT_ID
```

### Step 3: Build and Deploy

#### Option A: Using Deployment Script (Recommended)

```bash
./scripts/deploy-gcp.sh
```

#### Option B: Manual Deployment

**Backend:**

```bash
cd backend

# Build and push image
gcloud builds submit --tag gcr.io/$PROJECT_ID/sauti-ai-backend:latest

# Deploy to Cloud Run
gcloud run deploy sauti-ai-backend \
  --image gcr.io/$PROJECT_ID/sauti-ai-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --service-account sauti-ai-backend@$PROJECT_ID.iam.gserviceaccount.com \
  --set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,SUPABASE_SERVICE_KEY=supabase-service-key:latest,DATABASE_URL=database-url:latest" \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO" \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10
```

**Frontend:**

```bash
cd frontend

# Build with environment variables
export VITE_API_URL=https://sauti-ai-backend-xxxxx-uc.a.run.app
export VITE_SUPABASE_URL=https://your-project.supabase.co
export VITE_SUPABASE_ANON_KEY=your-anon-key

# Build and push image
gcloud builds submit \
  --substitutions=_VITE_API_URL=$VITE_API_URL,_VITE_SUPABASE_URL=$VITE_SUPABASE_URL,_VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY \
  --tag gcr.io/$PROJECT_ID/sauti-ai-frontend:latest

# Deploy to Cloud Run
gcloud run deploy sauti-ai-frontend \
  --image gcr.io/$PROJECT_ID/sauti-ai-frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

#### Option C: Using Cloud Build (CI/CD)

1. **Create Cloud Build Trigger:**

```bash
gcloud builds triggers create github \
  --name="sauti-ai-deploy" \
  --repo-name="sauti-ai" \
  --repo-owner="your-username" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --substitutions="_REGION=us-central1,_REPO_NAME=sauti-ai"
```

2. **Update cloudbuild.yaml substitutions** with your values

3. **Push to main branch** to trigger deployment

## ⚙️ Configuration

### Environment Variables

Backend environment variables are set via Cloud Run:

```bash
gcloud run services update sauti-ai-backend \
  --update-env-vars="KEY1=value1,KEY2=value2" \
  --region us-central1
```

**Common variables:**
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`
- `VERTEX_AI_LOCATION=us-central1`
- `CORS_ORIGINS=https://your-frontend-url.run.app`
- `PRODUCTION_ORIGINS=https://your-frontend-url.run.app`
- `PUBLIC_BACKEND_ORIGIN=https://your-backend-url.run.app`

### Resource Configuration

**Backend:**
- Memory: 2Gi (recommended), 1Gi (minimum)
- CPU: 2 (recommended), 1 (minimum)
- Min instances: 1 (to avoid cold starts)
- Max instances: 10 (adjust based on traffic)

**Frontend:**
- Memory: 512Mi
- CPU: 1
- Min instances: 0 (can scale to zero)
- Max instances: 10

### CORS Configuration

After deployment, update CORS to allow your frontend:

```bash
BACKEND_URL=$(gcloud run services describe sauti-ai-backend --region=us-central1 --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe sauti-ai-frontend --region=us-central1 --format="value(status.url)")

gcloud run services update sauti-ai-backend \
  --update-env-vars="PRODUCTION_ORIGINS=$FRONTEND_URL,PUBLIC_BACKEND_ORIGIN=$BACKEND_URL,FRONTEND_ORIGINS=$FRONTEND_URL" \
  --region us-central1
```

## 📊 Monitoring & Logging

### View Logs

```bash
# Backend logs
gcloud run services logs tail sauti-ai-backend --region us-central1

# Frontend logs
gcloud run services logs tail sauti-ai-frontend --region us-central1

# Follow logs in real-time
gcloud run services logs tail sauti-ai-backend --region us-central1 --follow
```

### Cloud Monitoring

1. Go to [Cloud Console Monitoring](https://console.cloud.google.com/monitoring)
2. View metrics for:
   - Request count
   - Latency
   - Error rate
   - CPU/Memory usage

### Set Up Alerts

```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

## 🔧 Troubleshooting

### Common Issues

**1. Deployment fails with "Permission denied"**
```bash
# Grant Cloud Build service account necessary permissions
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"
```

**2. Backend can't access secrets**
```bash
# Grant service account access to secrets
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:sauti-ai-backend@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**3. CORS errors**
- Verify `PRODUCTION_ORIGINS` includes your frontend URL
- Check that frontend URL matches exactly (including https://)
- Clear browser cache

**4. Cold start issues**
- Set `min-instances=1` to keep at least one instance warm
- Use Cloud Scheduler to ping the service periodically

**5. Out of memory errors**
- Increase memory allocation: `--memory 4Gi`
- Check for memory leaks in application code

### Debug Commands

```bash
# Check service status
gcloud run services describe sauti-ai-backend --region us-central1

# View recent revisions
gcloud run revisions list --service sauti-ai-backend --region us-central1

# Rollback to previous revision
gcloud run services update-traffic sauti-ai-backend \
  --to-revisions=REVISION_NAME=100 \
  --region us-central1

# Test service locally
gcloud run services proxy sauti-ai-backend --port=8080 --region us-central1
```

## 💰 Cost Optimization

### Tips to Reduce Costs

1. **Scale to Zero (Frontend)**
   - Frontend can scale to zero when not in use
   - Set `min-instances=0`

2. **Optimize Backend Scaling**
   - Use `min-instances=1` only if needed (prevents cold starts)
   - Set appropriate `max-instances` based on traffic

3. **Use Cloud CDN**
   - Enable Cloud CDN for frontend static assets
   - Reduces Cloud Run invocations

4. **Monitor Usage**
   - Set up billing alerts
   - Review Cloud Run metrics regularly

5. **Optimize Container Images**
   - Use multi-stage builds (already implemented)
   - Minimize image size

### Estimated Costs (us-central1)

**Backend (2Gi, 2 CPU, min 1 instance):**
- ~$50-100/month (idle)
- ~$0.00002400 per request (after free tier)

**Frontend (512Mi, 1 CPU, min 0 instances):**
- ~$0/month (scales to zero)
- ~$0.00002400 per request (after free tier)

**Free Tier:**
- 2 million requests/month
- 360,000 GB-seconds memory
- 180,000 vCPU-seconds

## 🔐 Security Best Practices

1. **Use Secret Manager** for all sensitive data
2. **Enable IAM** and use service accounts
3. **Set up VPC** for private services (if needed)
4. **Enable Cloud Armor** for DDoS protection
5. **Regular security updates** for base images
6. **Enable audit logging** for compliance

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)

## 🆘 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Cloud Run logs
3. Check [GitHub Issues](https://github.com/your-org/sauti-ai/issues)

---

**Last Updated:** 2025-01-15  
**Version:** 1.0.0

