# Quick Start: Deploy to Google Cloud Platform

This is a quick reference guide. For detailed instructions, see [DEPLOY_GCP.md](./DEPLOY_GCP.md).

## 🚀 Quick Deployment

### 1. Setup GCP Project

```bash
./scripts/setup-gcp.sh
```

### 2. Configure Secrets

```bash
# Required secrets
echo -n "https://your-project.supabase.co" | \
  gcloud secrets create supabase-url --data-file=-

echo -n "your-anon-key" | \
  gcloud secrets create supabase-key --data-file=-

echo -n "your-service-role-key" | \
  gcloud secrets create supabase-service-key --data-file=-

echo -n "postgresql://..." | \
  gcloud secrets create database-url --data-file=-

echo -n "$(gcloud config get-value project)" | \
  gcloud secrets create vertex-ai-project --data-file=-
```

Or use the interactive script:

```bash
./scripts/update-secrets.sh
```

### 3. Deploy

```bash
./scripts/deploy-gcp.sh
```

## 📝 What Gets Deployed

- **Backend**: FastAPI application on Cloud Run
- **Frontend**: React application on Cloud Run
- **Images**: Stored in Artifact Registry
- **Secrets**: Managed in Secret Manager

## 🔗 URLs

After deployment, you'll get:
- Backend URL: `https://sauti-ai-backend-XXXXXX-uc.a.run.app`
- Frontend URL: `https://sauti-ai-frontend-XXXXXX-uc.a.run.app`

## 📚 Next Steps

1. Update Supabase project settings with frontend URL
2. Test the deployment
3. Set up monitoring and alerts
4. Configure custom domain (optional)

For detailed information, see [DEPLOY_GCP.md](./DEPLOY_GCP.md).

