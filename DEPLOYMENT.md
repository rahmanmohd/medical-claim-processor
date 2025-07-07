# 🚀 Deployment Guide - Medical Claim Processor

## Quick Deploy on Render

### Option 1: One-Click Deploy (Recommended)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rahmanmohd/medical-claim-processor)

### Option 2: Manual Deployment

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect repository: `rahmanmohd/medical-claim-processor`
   - Click "Connect"

3. **Configure Service Settings**
   ```
   Name: medical-claim-processor
   Region: Oregon (US West)
   Branch: main
   Runtime: Docker
   ```

4. **Environment Variables** (Optional)
   ```
   PORT=10000
   PYTHON_VERSION=3.11
   NODE_VERSION=18
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build completion

## What Gets Deployed

### 🏗️ Full-Stack Application
- **Frontend**: React with Tailwind CSS and shadcn/ui
- **Backend**: FastAPI with Python 3.11
- **AI Integration**: Google Gemini API for document processing

### 🔧 Technical Stack
- **Frontend Build**: Vite + React 19 + TypeScript
- **Backend**: FastAPI + Uvicorn server
- **AI Agents**: Multi-agent document processing
- **Database**: SQLite (included)
- **PDF Processing**: ReportLab + Poppler utils

### 📦 Docker Configuration
- Multi-stage build for optimization
- Node.js 18 for frontend build
- Python 3.11-slim for backend
- Automatic frontend build integration

## API Endpoints

Once deployed, your application will have:

- **Frontend UI**: `https://your-app.onrender.com/`
- **API Documentation**: `https://your-app.onrender.com/docs`
- **Health Check**: `https://your-app.onrender.com/health`
- **Process Claims**: `POST https://your-app.onrender.com/process-claim`

## Expected Build Time

- **Total**: 5-10 minutes
- **Frontend Build**: 2-3 minutes
- **Backend Setup**: 2-3 minutes
- **Dependencies**: 3-4 minutes

## Post-Deployment

### 🧪 Testing Your Deployment
1. Visit your Render app URL
2. Upload sample medical documents (PDF format)
3. Test the claim processing functionality
4. Download generated PDF reports

### 🔧 Custom Domain (Optional)
1. Go to your service in Render dashboard
2. Click "Settings" → "Custom Domains"
3. Add your domain and configure DNS

### 📊 Monitoring
- **Logs**: Available in Render dashboard
- **Metrics**: CPU, Memory, Response time tracking
- **Health Checks**: Automatic monitoring at `/health`

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check logs in Render dashboard
   - Ensure all dependencies are in requirements.txt
   - Verify Docker configuration

2. **Frontend Not Loading**
   - Check static file serving
   - Verify build output in logs
   - Ensure proper path resolution

3. **API Errors**
   - Check environment variables
   - Verify Python dependencies
   - Test health endpoint first

### Support Resources
- **Repository**: [GitHub Issues](https://github.com/rahmanmohd/medical-claim-processor/issues)
- **Documentation**: [Project README](README.md)
- **Render Docs**: [render.com/docs](https://render.com/docs)

## Features Available

✅ **Multi-Document Upload**: Support for multiple PDF files  
✅ **AI Classification**: Automatic document type detection  
✅ **Data Extraction**: LLM-powered structured data extraction  
✅ **Cross-Validation**: Multi-document consistency checks  
✅ **Decision Engine**: AI-assisted claim approval/rejection  
✅ **PDF Reports**: Professional downloadable reports  
✅ **Modern UI**: Responsive design with drag-and-drop  
✅ **Real-time Processing**: Live progress indicators  

## Security & Privacy

- All processing happens server-side
- No data persistence beyond session
- Secure file upload handling
- CORS configuration for security
- Health check monitoring

---

**🎉 Your HealthPay AI Medical Claim Processor is now live!**

Access your application at: `https://your-app-name.onrender.com`
