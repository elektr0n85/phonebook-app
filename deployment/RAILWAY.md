# 🚂 Deploy to Railway

Railway is a modern deployment platform with automatic deployments from Git.

## ✅ **Prerequisites**

- Railway account (free tier available)
- GitHub repository with your code
- Railway CLI (optional)

---

## 🚀 **Quick Deploy (Web UI)**

### **1. Create New Project**

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select your phonebook repository

### **2. Add PostgreSQL Database**

1. In your project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will create a database automatically
4. Copy the `DATABASE_URL` from the database settings

### **3. Deploy Backend**

1. Click "+ New" → "GitHub Repo"
2. Select your repository
3. Set **Root Directory**: `backend`
4. Add environment variables:
   ```
   SECRET_KEY=<generate-random-32-chars>
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   ALLOWED_ORIGINS=https://your-frontend-url.railway.app
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ENVIRONMENT=production
   DEBUG=false
   ```
5. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Click "Deploy"

### **4. Deploy Frontend**

1. Click "+ New" → "GitHub Repo"
2. Select your repository again
3. Set **Root Directory**: `frontend`
4. Add environment variables:
   ```
   VITE_API_URL=https://your-backend-url.railway.app/api/v1
   ```
5. Set **Build Command**: `npm install && npm run build`
6. Set **Start Command**: `npx serve -s dist -l $PORT`
7. Click "Deploy"

---

## 🔧 **Using Railway CLI**

### **Install CLI**
```bash
npm install -g @railway/cli
railway login
```

### **Initialize Project**
```bash
# In your project root
railway init
railway link
```

### **Deploy Backend**
```bash
cd backend
railway up
```

### **Deploy Frontend**
```bash
cd frontend
railway up
```

### **Set Environment Variables**
```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
```

---

## 📋 **Configuration Files**

### **railway.json** (Backend)
Create `backend/railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **railway.json** (Frontend)
Create `frontend/railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npx serve -s dist -l $PORT"
  }
}
```

---

## 🔐 **Security Configuration**

### **Environment Variables**
Set in Railway dashboard under "Variables":
```
SECRET_KEY=<your-secret-key>
DATABASE_URL=${{Postgres.DATABASE_URL}}
ALLOWED_ORIGINS=https://your-frontend-domain.railway.app
ENVIRONMENT=production
DEBUG=false
```

### **Custom Domain** (Optional)
1. Go to Settings → Domains
2. Click "Generate Domain" or "Custom Domain"
3. Add your custom domain and configure DNS

---

## 🔄 **Automatic Deployments**

Railway automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update app"
git push origin main
# Railway automatically deploys! 🚀
```

---

## 📊 **Monitoring**

### **View Logs**
```bash
railway logs
```

Or in web UI: Click on service → "View Logs"

### **Metrics**
Railway dashboard shows:
- CPU usage
- Memory usage
- Network traffic
- Deployment history

---

## 💰 **Pricing**

- **Hobby Plan**: $5/month + usage
  - 512 MB RAM
  - 1 GB Disk
  - Shared CPU

- **Pro Plan**: $20/month + usage
  - 8 GB RAM
  - 100 GB Disk
  - Dedicated CPU

---

## 🐛 **Troubleshooting**

### **Build Fails**
```bash
# Check logs
railway logs --build

# Common issues:
# 1. Missing requirements.txt
# 2. Python version mismatch
# 3. Node version mismatch
```

### **Database Connection Issues**
- Ensure `DATABASE_URL` variable references: `${{Postgres.DATABASE_URL}}`
- Check database is in same project
- Verify connection string format

### **Frontend Not Loading**
- Check `VITE_API_URL` points to correct backend URL
- Ensure CORS `ALLOWED_ORIGINS` includes frontend URL
- Verify build completed successfully

---

## ✅ **Post-Deployment Checklist**

- [ ] Backend health check: `https://your-backend.railway.app/health`
- [ ] Frontend loads: `https://your-frontend.railway.app`
- [ ] Can register new user
- [ ] Can login
- [ ] Can create contact
- [ ] API calls work (check browser console)

---

## 🔗 **Useful Links**

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Railway Discord](https://discord.gg/railway)

---

**Deployment Time**: ~10 minutes  
**Difficulty**: ⭐⭐ Easy  
**Cost**: From $5/month
