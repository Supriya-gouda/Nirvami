# 🚀 Deployment Guide - Nirvami

Complete guide to deploy Nirvami's full-stack application using free tiers.

**Architecture:**
- **Frontend**: Vercel (React + Vite)
- **Backend**: Render (FastAPI + Python)
- **Database**: Supabase (PostgreSQL)

---

## 📋 Pre-Deployment Checklist

- [ ] GitHub account
- [ ] Supabase account (already setup)
- [ ] Vercel account
- [ ] Render account
- [ ] Google Gemini API key

---

## � Step 1: Prepare Your Repository

### Push to GitHub (if not already done):

```bash
# In project root (d:\Nirvami)
git init
git add .
git commit -m "Initial commit - Ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/nirvami.git
git push -u origin main
```

---

## 🎨 Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account & Import Project

1. Go to [https://vercel.com/](https://vercel.com/)
2. Sign up with GitHub
3. Click **"Add New Project"**
4. Import your `nirvami` repository
5. **Configure Project:**
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

### 2.2 Add Environment Variables

In Vercel project settings → Environment Variables, add these **3 required variables**:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=https://your-backend.onrender.com
```

> **Note:** You'll get the `VITE_API_URL` (backend URL) in Step 3. You can deploy now and update it later, or wait until Step 3 is complete.

### 2.3 Deploy

1. Click **"Deploy"**
2. Wait ~2 minutes
3. Copy your frontend URL: `https://your-app.vercel.app`

---

## ⚙️ Step 3: Deploy Backend to Render

### 3.1 Create Render Account & Import Project

1. Go to [https://render.com/](https://render.com/)
2. Sign up with GitHub
3. Click **"New +"** → **"Blueprint"**
4. Connect your `nirvami` repository
5. Render will detect `render.yaml`

### 3.2 Configure Environment Variables

Before deploying, add these **REQUIRED** variables in Render dashboard:

```env
# Required
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=your_supabase_postgres_connection_string
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=generate_random_string_here
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app.vercel.app
```

**How to get these values:**

1. **Supabase values**: Go to your [Supabase dashboard](https://supabase.com/dashboard) → Project Settings → API
   - `SUPABASE_URL`: Project URL
   - `SUPABASE_KEY`: anon/public key
   - `SUPABASE_SERVICE_ROLE_KEY`: service_role key (keep secret!)

2. **DATABASE_URL**: Supabase → Project Settings → Database → Connection String (URI format)

3. **GEMINI_API_KEY**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. **SECRET_KEY**: Generate using:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **ALLOWED_ORIGINS**: Use your Vercel URL from Step 2

**Optional variables** (can add later if needed):
```env
YOUTUBE_API_KEY=  # For practice videos
TWILIO_ACCOUNT_SID=  # For SMS crisis alerts
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

### 3.3 Update ALLOWED_ORIGINS

Replace `https://your-app.vercel.app` with your actual Vercel URL from Step 2.

### 3.4 Deploy

1. Click **"Apply"**
2. Wait ~5-10 minutes (ML models are large)
3. Copy your backend URL: `https://nirvami-backend.onrender.com`

### 3.5 Update Frontend Environment Variable

Go back to **Vercel** → Settings → Environment Variables:

Update `VITE_API_URL` to your Render backend URL:
```env
VITE_API_URL=https://nirvami-backend.onrender.com
```

Then **Redeploy** your frontend in Vercel.

---

## 🗄️ Step 4: Verify Database (Supabase)

Your Supabase is already configured. Just verify:

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings** → **Database**
4. Copy **Connection String** (URI format)
5. Make sure it's set as `DATABASE_URL` in Render

---

## ✅ Step 5: Testing Deployment

### Test Backend:
```bash
curl https://nirvami-backend.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### Test Frontend:
Visit `https://your-app.vercel.app` and:
- [ ] Page loads correctly
- [ ] Login/Signup works
- [ ] API calls succeed (check browser console)

---

## 🔧 Troubleshooting

### Frontend can't reach backend:
- Check CORS: `ALLOWED_ORIGINS` must include your Vercel URL
- Check `VITE_API_URL` is correct
- Redeploy frontend after changing env vars

### Backend crashes on Render:
- Check logs: Render Dashboard → Logs
- ML models might fail: Set `ENABLE_ML_MODELS=false` temporarily
- Redis connection: Verify `REDIS_URL` format

### Database errors:
- Check `DATABASE_URL` connection string
- Verify Supabase project is active
- Check RLS policies in Supabase

---

## 📊 Free Tier Limits

| Service | Free Tier Limit |
|---------|----------------|
| **Vercel** | Unlimited deployments, bandwidth |
| **Render** | 750 hours/month, sleeps after 15min inactivity |
| **Supabase** | 500MB database, 2GB bandwidth |

---

## 🔄 Continuous Deployment

Both Vercel and Render auto-deploy on git push:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

✅ Frontend auto-deploys in ~1 minute
✅ Backend auto-deploys in ~5 minutes

---

## 🎯 Post-Deployment Checklist

- [ ] Frontend accessible at Vercel URL
- [ ] Backend health check responds
- [ ] Login/signup works
- [ ] Database queries succeed
- [ ] ML models load (check Render logs)
- [ ] Custom domain setup (optional)
- [ ] SSL certificate active (automatic)

---

## 📞 Support

If you encounter issues:
1. Check Render logs for backend errors
2. Check Vercel deployment logs
3. Verify all environment variables are set
4. Test API endpoints with curl/Postman

---

**Estimated Total Setup Time:** 20-30 minutes

**Monthly Cost:** $0 (all free tiers)

**Done!** 🎉 Your app is now live on the internet!
