# 🚀 Deploy Your API to Render (Free Hosting)

## Prerequisites
✅ Your code should be on GitHub: https://github.com/AniketBhudke/mitadt-mess-api

---

## Step-by-Step Deployment

### Step 1: Sign Up on Render
1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with GitHub (use your AniketBhudke account)
4. Authorize Render to access your repositories

### Step 2: Create New Web Service
1. Click "New +" button (top right)
2. Select "Web Service"
3. Connect your GitHub account if not already connected
4. Find and select "mitadt-mess-api" repository
5. Click "Connect"

### Step 3: Configure Service
Render will auto-detect your `render.yaml` file, but verify these settings:

- **Name**: `mitadt-mess-api` (or any name you prefer)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- **Start Command**: `gunicorn mitadt_mess.wsgi:application`
- **Plan**: `Free`

### Step 4: Add Environment Variables
Click "Advanced" and add these environment variables:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.12.0` |
| `SECRET_KEY` | Click "Generate" or use any random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 5-10 minutes for deployment
3. Watch the logs for any errors

### Step 6: Access Your API
Once deployed, your API will be available at:

- **API Documentation**: `https://mitadt-mess-api.onrender.com/api/docs/`
- **Main App**: `https://mitadt-mess-api.onrender.com/`
- **Admin Panel**: `https://mitadt-mess-api.onrender.com/admin/`

---

## API Endpoints

Your deployed API will have these endpoints:

- `GET /api/raj-mess/?day=Monday&meal=breakfast` - Get Raj Mess menu
- `POST /api/rate-dish/` - Rate a dish
- `POST /api/complaint/` - Submit a complaint
- `GET /api/notices/` - Get published notices

---

## Create Superuser (Admin Access)

After deployment, create an admin user:

1. Go to Render dashboard
2. Click on your service "mitadt-mess-api"
3. Click "Shell" tab
4. Run this command:
   ```bash
   python manage.py createsuperuser
   ```
5. Enter username, email, and password
6. Now you can login at: `https://mitadt-mess-api.onrender.com/admin/`

---

## Troubleshooting

### If deployment fails:

**Check logs in Render dashboard**

Common issues:
1. **Missing dependencies**: Make sure `requirements.txt` is complete
2. **Database errors**: Render uses SQLite by default (works fine)
3. **Static files**: Already configured with WhiteNoise

### If API doesn't work:

1. Check if service is running in Render dashboard
2. View logs for errors
3. Make sure `ALLOWED_HOSTS` includes `.onrender.com`

---

## Free Tier Limitations

Render Free Tier:
- ✅ 750 hours/month (enough for 24/7)
- ✅ Automatic HTTPS
- ✅ Auto-deploy on git push
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Takes ~30 seconds to wake up

---

## Alternative: Deploy to Railway

If you prefer Railway:

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select "mitadt-mess-api"
5. Railway auto-deploys using `railway.json`
6. Add environment variables (same as above)
7. Your API will be at: `https://mitadt-mess-api.railway.app/api/docs/`

---

## Next Steps After Deployment

1. ✅ Test all API endpoints at `/api/docs/`
2. ✅ Create superuser for admin access
3. ✅ Add some test data through admin panel
4. ✅ Share your API URL with your team
5. ✅ Connect your frontend to the deployed API

---

## Your API is Production Ready! 🎉

All configurations are done:
- ✅ API Documentation (Swagger UI)
- ✅ REST API endpoints
- ✅ Database (SQLite)
- ✅ Static files handling
- ✅ Security settings
- ✅ CORS configuration
- ✅ Auto-deployment on git push

Just deploy and you're live!
