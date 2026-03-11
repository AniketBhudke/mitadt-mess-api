# 🌐 Frontend & Backend Access Guide

Your MIT ADT Mess Management System now serves both Frontend (HTML pages) and Backend (REST API).

---

## 🎨 Frontend URLs (HTML Pages)

### Main Pages:
- **Home**: `https://mitadt-mess-api.onrender.com/`
- **Login**: `https://mitadt-mess-api.onrender.com/login/`
- **Signup**: `https://mitadt-mess-api.onrender.com/signup/`

### Mess Pages (Student View):
- **Raj Mess Menu**: `https://mitadt-mess-api.onrender.com/raj_mess/`
- **Design Mess Menu**: `https://mitadt-mess-api.onrender.com/design_mess/`
- **Manet Mess Menu**: `https://mitadt-mess-api.onrender.com/manet_mess/`

### Admin Pages:
- **Django Admin**: `https://mitadt-mess-api.onrender.com/admin/`
- **Raj Mess Admin**: `https://mitadt-mess-api.onrender.com/admin_raj_mess/`
- **Design Mess Admin**: `https://mitadt-mess-api.onrender.com/admin_design_mess/`
- **Manet Mess Admin**: `https://mitadt-mess-api.onrender.com/admin_manet_mess/`

### Other Pages:
- **Notices**: `https://mitadt-mess-api.onrender.com/notices/`
- **Complaint Form**: `https://mitadt-mess-api.onrender.com/complaint/`
- **Feedback**: `https://mitadt-mess-api.onrender.com/feedback/`
- **Weekly Suggestion**: `https://mitadt-mess-api.onrender.com/weekly_suggestion/`
- **Payment Selection**: `https://mitadt-mess-api.onrender.com/payment_selection/`

---

## 🔌 Backend URLs (REST API)

### API Documentation:
- **Swagger UI**: `https://mitadt-mess-api.onrender.com/api/docs/`
- **API Home**: `https://mitadt-mess-api.onrender.com/api/home/`
- **API Schema**: `https://mitadt-mess-api.onrender.com/api/schema/`

### API Endpoints:
- **GET** `/api/raj-mess/?day=Monday&meal=breakfast` - Get mess menu
- **GET** `/api/notices/` - Get all notices
- **POST** `/api/rate-dish/` - Rate a dish
- **POST** `/api/complaint/` - Submit complaint

---

## 🚀 How to Access:

### For Students:
1. Visit: `https://mitadt-mess-api.onrender.com/`
2. Sign up or login
3. View mess menus, submit complaints, give feedback

### For Admins:
1. Visit: `https://mitadt-mess-api.onrender.com/admin/`
2. Login with superuser credentials
3. Manage dishes, notices, complaints

### For Developers:
1. Visit: `https://mitadt-mess-api.onrender.com/api/docs/`
2. Test API endpoints
3. Integrate with mobile apps or other frontends

---

## 📱 Architecture:

```
┌─────────────────────────────────────┐
│   MIT ADT Mess Management System    │
└─────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼────┐      ┌────▼────┐
   │ Frontend│      │ Backend │
   │  (HTML) │      │  (API)  │
   └─────────┘      └─────────┘
        │                 │
   ┌────▼────┐      ┌────▼────┐
   │Templates│      │   JSON  │
   │   CSS   │      │Response │
   │  Images │      │         │
   └─────────┘      └─────────┘
```

---

## 🔧 Local Development:

### Run Both Frontend & Backend Locally:

```bash
cd mitadt_mess
python manage.py runserver
```

Then access:
- Frontend: `http://127.0.0.1:8000/`
- API Docs: `http://127.0.0.1:8000/api/docs/`

---

## 📊 What's Included:

### Frontend Features:
✅ User authentication (signup/login/logout)
✅ Mess menu display (Raj, Design, Manet)
✅ Dish rating system
✅ Complaint submission
✅ Feedback forms
✅ Weekly suggestions
✅ Notice board
✅ Payment selection
✅ Admin panels for each mess

### Backend API Features:
✅ RESTful API endpoints
✅ JSON responses
✅ Swagger documentation
✅ CORS support
✅ Authentication ready
✅ Mobile app integration ready

---

## 🎯 Use Cases:

### Web Application:
Users access the HTML frontend directly through browser
- URL: `https://mitadt-mess-api.onrender.com/`

### Mobile App:
Mobile apps consume the REST API
- Base URL: `https://mitadt-mess-api.onrender.com/api/`
- Documentation: `/api/docs/`

### Third-party Integration:
Other systems can integrate via API
- Get menu data
- Submit complaints
- Fetch notices

---

## 🔐 Authentication:

### Frontend:
- Session-based authentication
- Login at: `/login/`
- Signup at: `/signup/`

### API:
- Token-based authentication (can be added)
- Currently uses Django session auth

---

## 📝 Next Steps:

1. **Create Superuser** (for admin access):
```bash
# On Render Shell:
python manage.py createsuperuser
```

2. **Add Sample Data**:
- Login to admin panel
- Add dishes, notices, etc.

3. **Test Frontend**:
- Visit homepage
- Create account
- Browse mess menus

4. **Test API**:
- Visit `/api/docs/`
- Try out endpoints
- Check responses

---

## 🌟 Your System is Now Complete!

✅ Frontend (HTML/CSS) - For web users
✅ Backend (REST API) - For mobile apps & integrations
✅ Admin Panel - For management
✅ Documentation - For developers

**Both frontend and backend are deployed and accessible!** 🎉
