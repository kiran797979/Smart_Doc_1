# 🌐 Cloud Deployment Guide

This guide will help you deploy Smart Doc Checker to Render (backend) and Vercel (frontend).

## 📋 Prerequisites

1. **GitHub Account** with your repository
2. **Render Account** ([render.com](https://render.com))
3. **Vercel Account** ([vercel.com](https://vercel.com))

## 🚀 Step 1: Deploy Backend to Render

### 1.1 Create Render Account and Connect GitHub

1. Go to [render.com](https://render.com) and sign up
2. Connect your GitHub account
3. Grant access to your Smart Doc repository

### 1.2 Create a New Web Service

1. Click **"New +"** → **"Web Service"**
2. Select your repository: `Smart_Doc_1`
3. Configure the service:

```yaml
Name: smart-doc-checker-api
Environment: Docker
Branch: main
Root Directory: backend
```

### 1.3 Configure Build & Deploy Settings

Render will automatically detect the `Dockerfile` in the backend directory and use these settings:

- **Build Command**: `docker build -t smart-doc-api .`
- **Start Command**: `python -m api.api_server`
- **Port**: `8000` (automatically detected from Procfile)

### 1.4 Environment Variables (Optional)

You can set these in Render dashboard under "Environment":

```
PYTHON_VERSION=3.11
PORT=8000
```

### 1.5 Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Note your Render URL: `https://your-service-name.onrender.com`

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Prepare Environment Variables

1. Create `.env.local` in your frontend directory:

```bash
cd "d:\Smart_Doc-master\Smart_Doc-master\frontend"
echo "VITE_API_URL=https://your-render-app-name.onrender.com" > .env.local
```

Replace `your-render-app-name` with your actual Render service URL.

### 2.2 Deploy to Vercel

#### Option A: Vercel CLI (Recommended)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy from frontend directory:
```bash
cd "d:\Smart_Doc-master\Smart_Doc-master\frontend"
vercel
```

4. Follow the prompts:
   - Set up and deploy? **Yes**
   - Which scope? **Your username**
   - Link to existing project? **No**
   - Project name? **smart-doc-checker** (or your choice)
   - In which directory is your code located? **./**

5. Set production environment variable:
```bash
vercel env add VITE_API_URL
# Enter your Render backend URL when prompted
```

6. Deploy to production:
```bash
vercel --prod
```

#### Option B: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"New Project"**
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - Name: `VITE_API_URL`
   - Value: `https://your-render-app-name.onrender.com`
6. Click **"Deploy"**

## 🔗 Step 3: Update CORS Settings

After both deployments are complete, update your backend CORS settings:

1. Note your Vercel frontend URL: `https://your-project.vercel.app`
2. The backend is already configured to accept Vercel domains in `api_server.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.vercel.app",
    "https://smart-doc-checker.vercel.app"
]
```

## ✅ Step 4: Verify Deployment

### 4.1 Test Backend

Visit your Render URL:
- Health check: `https://your-render-app.onrender.com/health`
- API docs: `https://your-render-app.onrender.com/docs`

### 4.2 Test Frontend

Visit your Vercel URL and test:
1. File upload functionality
2. Document processing
3. Contradiction detection

### 4.3 Test Integration

1. Upload a test document through the frontend
2. Verify it communicates with the backend
3. Check that contradictions are detected and displayed

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your Vercel URL is in the CORS origins list
2. **API Connection Timeout**: Check if your Render service is sleeping (free tier)
3. **Build Failures**: Check build logs in Render/Vercel dashboards

### Render Free Tier Limitations

- Services sleep after 15 minutes of inactivity
- Cold starts can take 30+ seconds
- Consider keeping the service warm with a health check service

### Vercel Deployment Tips

- Build time limit: 45 seconds (Hobby plan)
- Function execution limit: 10 seconds (Hobby plan)
- Consider upgrading for production use

## 📊 Monitoring

### Render Monitoring

1. Check service logs in Render dashboard
2. Monitor deployment status
3. Set up health checks

### Vercel Monitoring

1. Check function logs in Vercel dashboard
2. Monitor build and deployment status
3. Set up analytics (optional)

## 🎉 Success!

Your Smart Doc Checker is now live on:
- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `https://your-render-app.onrender.com`

Share these URLs to let others use your document contradiction detection system!

## 📝 Next Steps

1. **Custom Domains**: Configure custom domains for both services
2. **SSL Certificates**: Automatically provided by both platforms
3. **Environment Management**: Set up staging environments
4. **Monitoring**: Add error tracking and analytics
5. **Performance**: Optimize for production workloads