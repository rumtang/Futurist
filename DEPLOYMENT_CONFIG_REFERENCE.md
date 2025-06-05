# CX Futurist AI - Deployment Configuration Reference

## 🔧 **Standardized Configuration Values**

### **Artifact Registry Repository Name**
- **ALWAYS USE**: `cx-futurist`
- **NEVER USE**: `insightcommand-registry` (legacy name)

### **Image Names & Tags**
- Backend: `${_REGION}-docker.pkg.dev/$PROJECT_ID/cx-futurist/api`
- Frontend: `${_REGION}-docker.pkg.dev/$PROJECT_ID/cx-futurist/frontend`

### **Service Names**
- Backend Service: `cx-futurist-api`
- Frontend Service: `cx-futurist-frontend`
- Service Account: `cx-futurist-sa`

### **Port Configuration**
- Backend Port: `8080` (set in Dockerfile)
- Frontend Port: `3000` (set in frontend/Dockerfile)
- Local Development API: `8080`
- Local Development Frontend: `3000`

### **Project Configuration**
- Default Project ID: `insightcommand-461701`
- Default Region: `us-central1`
- Repository Format: `docker`

## 📁 **Configuration Files Reference**

### **Main Deployment Files**
1. **`deploy.sh`** - Primary deployment script
   - Creates `cx-futurist` repository
   - Sets up service account: `cx-futurist-sa`
   - Uses `cloudbuild.yaml` for deployment

2. **`cloudbuild.yaml`** - Full production build & deploy
   - Builds both backend and frontend
   - Deploys to Cloud Run
   - Links frontend to backend URL

3. **`cloudbuild-simple.yaml`** - Simplified deployment
   - Backend only deployment
   - For testing and development

4. **`cloudbuild-build-only.yaml`** - Build without deploy
   - Just builds and pushes images
   - For CI/CD pipelines

### **Configuration Templates**
1. **`service.yaml`** - Cloud Run service template
2. **`.env.example`** - Environment variables template
3. **`frontend/.env.local`** - Frontend local development

## ⚠️ **Critical Consistency Rules**

### **Repository Name**
- ALL cloudbuild files MUST use: `cx-futurist`
- deploy.sh creates repository: `cx-futurist`
- service.yaml references: `cx-futurist`

### **Port Numbers**
- Backend Dockerfile exposes: `8080`
- All cloudbuild files MUST use: `8080`
- Cloud Run service MUST use: `8080`
- Environment files MUST reference: `8080`

### **Service Names**
- Backend service: `cx-futurist-api` (everywhere)
- Frontend service: `cx-futurist-frontend` (everywhere)
- Service account: `cx-futurist-sa@{PROJECT_ID}.iam.gserviceaccount.com`

## 🔍 **Verification Commands**

### **Check Repository Consistency**
```bash
grep -r "insightcommand-registry\|cx-futurist" cloudbuild*.yaml
# Should ONLY show "cx-futurist" references
```

### **Check Port Consistency**
```bash
grep -r "8000\|8080\|8100\|8101" cloudbuild*.yaml .env* frontend/.env*
# Should ONLY show "8080" for API ports
```

### **Check Service Names**
```bash
grep -r "cx-futurist-api\|cx-futurist-frontend\|cx-futurist-sa" cloudbuild*.yaml deploy.sh service.yaml
# Should show consistent naming across all files
```

## 🛠️ **Fixed Issues (2025-06-03)**

### **Repository Name Conflicts**
- ❌ **Before**: `cloudbuild-simple.yaml` and `cloudbuild-build-only.yaml` used `insightcommand-registry`
- ✅ **After**: All files now use `cx-futurist`

### **Port Inconsistencies**
- ❌ **Before**: Mixed use of ports 8000, 8080, 8100, 8101
- ✅ **After**: Standardized on port 8080 for backend

### **Environment Configuration**
- ❌ **Before**: `frontend/.env.local` used ports 8100/8101
- ✅ **After**: Uses port 8080 consistently

## 🚀 **Deployment Options**

### **Full Production Deployment**
```bash
./deploy.sh
```
Uses: `cloudbuild.yaml` - Full setup with frontend and backend

### **Quick Backend-Only Deployment**
```bash
gcloud builds submit --config cloudbuild-simple.yaml
```
Uses: `cloudbuild-simple.yaml` - Backend only

### **Build Images Only**
```bash
gcloud builds submit --config cloudbuild-build-only.yaml
```
Uses: `cloudbuild-build-only.yaml` - Just builds and pushes images

### **Manual Service Deployment**
```bash
# Replace placeholders in service.yaml first
gcloud run services replace service.yaml --region=us-central1
```

## 📋 **Pre-Deployment Checklist**

- [ ] All cloudbuild files reference `cx-futurist` repository
- [ ] All port references use `8080` for backend
- [ ] Service names are consistent across all files
- [ ] Environment variables match expected ports
- [ ] Project ID is set correctly
- [ ] Secrets are created in Secret Manager
- [ ] Service account has proper permissions

## 🔄 **Preventing Future Issues**

1. **Always use this reference document** when modifying deployment configs
2. **Run verification commands** before committing changes  
3. **Test with `cloudbuild-simple.yaml`** before full deployment
4. **Never hard-code different repository names** in different files
5. **Keep all port numbers consistent** across all configuration files
6. **Use the same service names** everywhere

---
**Last Updated**: 2025-06-03  
**Status**: All configuration inconsistencies resolved ✅