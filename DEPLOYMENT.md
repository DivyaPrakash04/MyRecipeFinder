# MyRecipeFinder - Free Production Deployment Guide

This guide explains how to deploy MyRecipeFinder to production using completely free services.

## Overview

We'll deploy:
- **Frontend**: Netlify (React app)
- **Backend**: Render (Flask API)
- **Database**: Neon (PostgreSQL) - Optional, can use SQLite for simplicity

## Prerequisites

1. **GitHub Account** - You'll need this for both Netlify and Render
2. **API Keys** - Get these free accounts:
   - [Cohere](https://cohere.ai/) - Free tier available
   - [Tavily](https://tavily.com/) - Free tier available

## Step 1: Database Setup (Optional - Skip for SQLite)

### Option A: Neon PostgreSQL (Recommended)
1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project
3. Copy the connection string from the dashboard
4. Update your `backend/.env`:
   ```env
   DATABASE_URL=postgres://USER:PASS@HOST.neon.tech:5432/DB?sslmode=require
   ```

### Option B: SQLite (Simpler)
Keep the default SQLite setup - no configuration needed.

## Step 2: Backend Deployment (Render)

1. **Fork or upload to GitHub**:
   - Create a GitHub repository
   - Push your code: `git push origin main`

2. **Deploy to Render**:
   - Go to [render.com](https://render.com) and sign up with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `myrecipefinder-backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

3. **Environment Variables**:
   Add these in Render dashboard:
   ```
   FLASK_ENV=production
   PORT=10000
   COHERE_API_KEY=your_cohere_key_here
   TAVILY_API_KEY=your_tavily_key_here
   DATABASE_URL=your_database_url_here (if using Postgres)
   FRONTEND_ORIGIN=https://your-frontend-domain.netlify.app
   ```

4. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (usually 2-3 minutes)
   - Note your backend URL (e.g., `https://myrecipefinder-backend.onrender.com`)

## Step 3: Frontend Deployment (Netlify)

1. **Build the frontend locally**:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Deploy to Netlify**:
   - Go to [netlify.com](https://netlify.com) and sign up with GitHub
   - Click "New site from Git"
   - Connect your GitHub repository
   - Configure:
     - **Branch**: `main`
     - **Build command**: `npm run build`
     - **Publish directory**: `dist`
   - Add environment variable:
     ```
     VITE_API_BASE_URL=https://your-backend-domain.onrender.com
     ```

3. **Deploy**:
   - Click "Deploy site"
   - Wait for build completion
   - Note your frontend URL (e.g., `https://amazing-site-123.netlify.app`)

## Step 4: Update Environment Variables

1. **Update backend .env**:
   ```env
   FLASK_ENV=production
   PORT=10000
   FRONTEND_ORIGIN=https://your-frontend-domain.netlify.app
   COHERE_API_KEY=your_cohere_key_here
   TAVILY_API_KEY=your_tavily_key_here
   DATABASE_URL=your_database_url_here
   ```

2. **Update frontend .env** (already done):
   ```env
   VITE_API_BASE_URL=https://your-backend-domain.onrender.com
   ```

## Step 5: Testing

1. Visit your frontend URL
2. Test the health endpoint: `https://your-backend-domain.onrender.com/health`
3. Test a recipe search
4. Try the chat functionality

## Free Tier Limits

- **Render**: 512MB RAM, sleeps after inactivity (wakes quickly)
- **Netlify**: 100GB bandwidth/month, 300 build minutes/month
- **Neon**: 512MB storage, 100 hours compute/month
- **Cohere**: Free tier limits vary
- **Tavily**: Free tier limits vary

## Troubleshooting

### Backend Issues
- Check Render logs in dashboard
- Ensure all environment variables are set
- Verify API keys are valid
- Test locally first: `python app.py`

### Frontend Issues
- Check Netlify build logs
- Ensure `VITE_API_BASE_URL` is correct
- Verify CORS settings in backend

### Database Issues
- Check database connection string
- Ensure database is not paused (Neon)
- Consider using SQLite for simplicity

## Cost Estimate

**Total: $0/month** (all services have generous free tiers)

- Render: Free for small apps
- Netlify: Free for personal projects
- Neon: Free for small databases
- API costs: Covered by free tiers

## Advanced Options

### Custom Domain
- Add custom domain in Netlify dashboard
- Add SSL certificate (free with Netlify)

### Database Migration (SQLite to Postgres)
```bash
# Install postgres driver
pip install -r requirements-postgres.txt

# Update DATABASE_URL in .env
# Restart backend
```

### Monitoring
- Use Render dashboard for backend monitoring
- Use Netlify Analytics for frontend
- Check API usage in Cohere/Tavily dashboards

## Re-deployment

After making changes:
1. Push to GitHub
2. Render and Netlify auto-deploy from main branch
3. No manual intervention needed

## Support

If you encounter issues:
1. Check service dashboards (Render, Netlify, Neon)
2. Verify all environment variables
3. Test API keys locally first
4. Check console logs in browser

---

Your MyRecipeFinder app is now live and accessible worldwide! 🚀
