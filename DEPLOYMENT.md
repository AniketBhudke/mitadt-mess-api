# Deployment Guide - MIT ADT Mess Management API

## Quick Deploy Options

### 1. Render (Recommended - Free Tier Available)

1. Create account at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Click "Create Web Service"
6. Your API will be live at: `https://your-app.onrender.com`

**API Docs URL**: `https://your-app.onrender.com/api/docs/`

---

### 2. Railway (Easy Deploy)

1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect `railway.json`
5. Add environment variables:
   - `SECRET_KEY`: Generate a random string
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: your-app.railway.app

**API Docs URL**: `https://your-app.railway.app/api/docs/`

---

### 3. Heroku

1. Install Heroku CLI: `npm install -g heroku`
2. Login: `heroku login`
3. Create app:
   ```bash
   cd mitadt_mess
   heroku create your-app-name
   ```
4. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG=False
   ```
5. Deploy:
   ```bash
   git push heroku main
   ```
6. Run migrations:
   ```bash
   heroku run python manage.py migrate
   ```

**API Docs URL**: `https://your-app-name.herokuapp.com/api/docs/`

---

### 4. PythonAnywhere (Free Tier)

1. Create account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code via Git or Files
3. Create a new web app (Django)
4. Configure WSGI file to point to `mitadt_mess.wsgi`
5. Set up virtualenv and install requirements
6. Reload web app

**API Docs URL**: `https://yourusername.pythonanywhere.com/api/docs/`

---

### 5. DigitalOcean App Platform

1. Create account at [digitalocean.com](https://www.digitalocean.com)
2. Go to App Platform
3. Connect GitHub repository
4. DigitalOcean will auto-detect Django
5. Add environment variables
6. Deploy

---

## Environment Variables Required

For all platforms, set these environment variables:

```
SECRET_KEY=your-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

Optional:
```
DATABASE_URL=postgres://user:pass@host:5432/dbname
CORS_ALLOWED_ORIGINS=https://your-frontend.com
```

---

## Pre-Deployment Checklist

- [ ] Update `requirements.txt` with all dependencies
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use environment variables for sensitive data
- [ ] Set up proper database (PostgreSQL recommended for production)
- [ ] Configure static files with WhiteNoise
- [ ] Run migrations on production database
- [ ] Create superuser for admin access
- [ ] Test all API endpoints

---

## Post-Deployment

After deployment, your API will be available at:

- **Main App**: `https://your-domain.com/`
- **API Documentation**: `https://your-domain.com/api/docs/`
- **Admin Panel**: `https://your-domain.com/admin/`
- **API Endpoints**:
  - `GET /api/raj-mess/` - Get mess menu
  - `POST /api/rate-dish/` - Rate a dish
  - `POST /api/complaint/` - Submit complaint
  - `GET /api/notices/` - Get notices

---

## Create Superuser on Production

```bash
# Heroku
heroku run python manage.py createsuperuser

# Railway
railway run python manage.py createsuperuser

# Render (use web shell in dashboard)
python manage.py createsuperuser
```

---

## Troubleshooting

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
```

**Database issues:**
```bash
python manage.py migrate
```

**Check logs:**
- Heroku: `heroku logs --tail`
- Railway: Check logs in dashboard
- Render: Check logs in dashboard

---

## Cost Comparison

| Platform | Free Tier | Paid Plans |
|----------|-----------|------------|
| Render | ✅ Yes (750 hrs/month) | From $7/month |
| Railway | ✅ Yes ($5 credit) | Pay as you go |
| Heroku | ❌ No (was discontinued) | From $5/month |
| PythonAnywhere | ✅ Yes (limited) | From $5/month |
| DigitalOcean | ❌ No | From $5/month |

**Recommendation**: Start with Render or Railway for free hosting.
