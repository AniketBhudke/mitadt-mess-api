# MIT ADT Mess Management System

A Django-based web application for managing mess operations, including menu management, ratings, complaints, and notices.

## Quick Start (Automated)

### Windows
1. Run setup (first time only):
   ```bash
   setup.bat
   ```

2. Start the server:
   ```bash
   start_server.bat
   ```

### Linux/Mac
1. Make scripts executable:
   ```bash
   chmod +x setup.sh start_server.sh
   ```

2. Run setup (first time only):
   ```bash
   ./setup.sh
   ```

3. Start the server:
   ```bash
   ./start_server.sh
   ```

## Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Start the server:
   ```bash
   python manage.py runserver
   ```

## Access Points

- **Main Application**: http://127.0.0.1:8000/
- **API Documentation (Swagger UI)**: http://127.0.0.1:8000/api/docs/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Schema**: http://127.0.0.1:8000/api/schema/

## API Endpoints

- `GET /api/raj-mess/` - Get Raj Mess menu (params: day, meal)
- `POST /api/rate-dish/` - Rate a dish
- `POST /api/complaint/` - Submit a complaint
- `GET /api/notices/` - Get published notices

## Features

- User authentication (signup/login/logout)
- Multiple mess management (Raj Mess, Design Mess, Manet Mess)
- Dish rating system
- Complaint submission
- Notice board
- Weekly menu suggestions
- Payment selection
- Feedback system
- REST API with Swagger documentation

## Technology Stack

- Django 5.1
- Django REST Framework
- drf-spectacular (API documentation)
- SQLite database
- Bootstrap/CSS for frontend

## Project Structure

```
mitadt_mess/
├── manage.py
├── requirements.txt
├── setup.bat / setup.sh
├── start_server.bat / start_server.sh
├── mitadt_mess/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── testapp/              # Main application
│   ├── models.py
│   ├── views.py
│   ├── api_views.py
│   ├── api_urls.py
│   ├── serializers.py
│   └── forms.py
├── static/               # Static files (CSS, images)
├── media/                # User uploaded files
└── templates/            # HTML templates
```

## Development

To create a superuser for admin access:
```bash
python manage.py createsuperuser
```

## License

MIT License
