from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import secrets
import string

def test_day_fields_debug(request):
    """Debug endpoint to test day fields generation"""
    try:
        from .forms import WeeklysuggestionForm
        from .models import SuggestionPeriod
        
        # Test form creation
        form = WeeklysuggestionForm()
        
        # Test day fields building (same logic as weekly_suggestion view)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_fields = []
        
        for day in days:
            key_base = day.lower()
            bf_name = f"{key_base}_breakfast"
            lf_name = f"{key_base}_lunch"
            df_name = f"{key_base}_dinner"

            day_fields.append({
                "day": day,
                "bf_name": bf_name,
                "lf_name": lf_name,
                "df_name": df_name,
                "bf_exists": bf_name in form.fields,
                "lf_exists": lf_name in form.fields,
                "df_exists": df_name in form.fields,
                "bf_field_type": str(type(form.fields.get(bf_name, None))),
                "lf_field_type": str(type(form.fields.get(lf_name, None))),
                "df_field_type": str(type(form.fields.get(df_name, None))),
            })
        
        # Test suggestion period
        current_period = SuggestionPeriod.get_current_period()
        
        debug_info = {
            'form_fields_count': len(form.fields),
            'form_fields': list(form.fields.keys()),
            'day_fields_count': len(day_fields),
            'day_fields_structure': day_fields,
            'current_period': str(current_period) if current_period else None,
            'period_active': current_period.is_submission_allowed() if current_period else False,
            'all_day_fields_exist': all(
                day['bf_exists'] and day['lf_exists'] and day['df_exists'] 
                for day in day_fields
            )
        }
        
        return JsonResponse({
            'status': 'success',
            'message': 'Day fields test completed successfully',
            'debug_info': debug_info
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'status': 'error',
            'message': f'Day fields test failed: {str(e)}',
            'traceback': traceback.format_exc()
        })

def health_check(request):
    """Health check endpoint to verify system status"""
    try:
        from .models import SuggestionPeriod, FeedbackPeriod
        from datetime import date
        
        status = {
            'status': 'healthy',
            'date': str(date.today()),
            'suggestion_system': {},
            'feedback_system': {},
            'database': {}
        }
        
        # Check suggestion system
        try:
            current_suggestion = SuggestionPeriod.get_current_period()
            if current_suggestion and current_suggestion.is_submission_allowed():
                status['suggestion_system'] = {
                    'status': 'active',
                    'current_period': current_suggestion.name,
                    'deadline': str(current_suggestion.submission_deadline),
                    'submissions_allowed': True
                }
            else:
                status['suggestion_system'] = {
                    'status': 'inactive',
                    'submissions_allowed': False,
                    'current_period': str(current_suggestion) if current_suggestion else None
                }
        except Exception as e:
            status['suggestion_system'] = {'status': 'error', 'error': str(e)}
        
        # Check feedback system
        try:
            current_feedback = FeedbackPeriod.get_current_period()
            if current_feedback and current_feedback.is_submission_allowed():
                status['feedback_system'] = {
                    'status': 'active',
                    'current_period': current_feedback.name,
                    'deadline': str(current_feedback.submission_deadline),
                    'submissions_allowed': True
                }
            else:
                status['feedback_system'] = {
                    'status': 'inactive',
                    'submissions_allowed': False,
                    'current_period': str(current_feedback) if current_feedback else None
                }
        except Exception as e:
            status['feedback_system'] = {'status': 'error', 'error': str(e)}
        
        # Check database
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                status['database'] = {'status': 'connected'}
        except Exception as e:
            status['database'] = {'status': 'error', 'error': str(e)}
        
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

def fix_periods(request):
    """Simple endpoint to fix suggestion periods - can be called via URL"""
    try:
        from django.core.management import call_command
        from io import StringIO
        import sys
        
        # Capture command output
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            call_command('fix_suggestion_periods')
            output = captured_output.getvalue()
        finally:
            sys.stdout = old_stdout
        
        return JsonResponse({
            'status': 'success',
            'message': 'Suggestion periods fixed successfully',
            'output': output
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to fix periods: {str(e)}'
        })

def initialize_database(request):
    """Initialize database tables - for deployment debugging"""
    try:
        from django.db import connection
        from django.core.management import call_command
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        results = []
        
        # First, create all Django system tables manually
        try:
            cursor = connection.cursor()
            
            # Create django_session table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_session (
                    session_key VARCHAR(40) PRIMARY KEY,
                    session_data TEXT NOT NULL,
                    expire_date DATETIME NOT NULL
                );
            """)
            results.append("Created django_session table")
            
            # Create django_content_type table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_content_type (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_label VARCHAR(100) NOT NULL,
                    model VARCHAR(100) NOT NULL,
                    UNIQUE(app_label, model)
                );
            """)
            results.append("Created django_content_type table")
            
            # Create django_migrations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied DATETIME NOT NULL
                );
            """)
            results.append("Created django_migrations table")
            
            # Create auth_permission table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_permission (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    content_type_id INTEGER NOT NULL,
                    codename VARCHAR(100) NOT NULL,
                    UNIQUE(content_type_id, codename)
                );
            """)
            results.append("Created auth_permission table")
            
            # Create auth_group table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_group (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(150) UNIQUE NOT NULL
                );
            """)
            results.append("Created auth_group table")
            
            # Create auth_group_permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_group_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    UNIQUE(group_id, permission_id)
                );
            """)
            results.append("Created auth_group_permissions table")
            
            # Create auth_user table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password VARCHAR(128) NOT NULL,
                    last_login DATETIME,
                    is_superuser BOOLEAN NOT NULL DEFAULT 0,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    first_name VARCHAR(150) NOT NULL DEFAULT '',
                    last_name VARCHAR(150) NOT NULL DEFAULT '',
                    email VARCHAR(254) NOT NULL DEFAULT '',
                    is_staff BOOLEAN NOT NULL DEFAULT 0,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            results.append("Created auth_user table")
            
            # Create auth_user_groups table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    UNIQUE(user_id, group_id)
                );
            """)
            results.append("Created auth_user_groups table")
            
            # Create auth_user_user_permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    UNIQUE(user_id, permission_id)
                );
            """)
            results.append("Created auth_user_user_permissions table")
            
            # Create django_admin_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_admin_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_time DATETIME NOT NULL,
                    object_id TEXT,
                    object_repr VARCHAR(200) NOT NULL,
                    action_flag SMALLINT UNSIGNED NOT NULL,
                    change_message TEXT NOT NULL,
                    content_type_id INTEGER,
                    user_id INTEGER NOT NULL
                );
            """)
            results.append("Created django_admin_log table")
            
            # Create testapp_manet_menu table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_manet_menu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL,
                    image VARCHAR(100),
                    meal VARCHAR(50) NOT NULL,
                    day VARCHAR(10) NOT NULL
                );
            """)
            results.append("Created testapp_manet_menu table")
            
            # Create testapp_design_menu table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_design_menu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL,
                    image VARCHAR(100),
                    meal VARCHAR(40) NOT NULL,
                    day VARCHAR(40) NOT NULL
                );
            """)
            results.append("Created testapp_design_menu table")
            
            # Create testapp_manetrating table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_manetrating (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    dish_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(user_id, dish_id)
                );
            """)
            results.append("Created testapp_manetrating table")
            
            # Create testapp_designrating table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_designrating (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    design_menu_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, design_menu_id)
                );
            """)
            results.append("Created testapp_designrating table")
            
            # Create testapp_weekly_suggestion table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_weekly_suggestion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mess_name VARCHAR(100) NOT NULL,
                    student_name VARCHAR(100),
                    email VARCHAR(254),
                    monday_breakfast VARCHAR(100) NOT NULL,
                    monday_lunch VARCHAR(100) NOT NULL,
                    monday_dinner VARCHAR(100) NOT NULL,
                    tuesday_breakfast VARCHAR(100) NOT NULL,
                    tuesday_lunch VARCHAR(100) NOT NULL,
                    tuesday_dinner VARCHAR(100) NOT NULL,
                    wednesday_breakfast VARCHAR(100) NOT NULL,
                    wednesday_lunch VARCHAR(100) NOT NULL,
                    wednesday_dinner VARCHAR(100) NOT NULL,
                    thursday_breakfast VARCHAR(100) NOT NULL,
                    thursday_lunch VARCHAR(100) NOT NULL,
                    thursday_dinner VARCHAR(100) NOT NULL,
                    friday_breakfast VARCHAR(100) NOT NULL,
                    friday_lunch VARCHAR(100) NOT NULL,
                    friday_dinner VARCHAR(100) NOT NULL,
                    saturday_breakfast VARCHAR(100) NOT NULL,
                    saturday_lunch VARCHAR(100) NOT NULL,
                    saturday_dinner VARCHAR(100) NOT NULL,
                    sunday_breakfast VARCHAR(100) NOT NULL,
                    sunday_lunch VARCHAR(100) NOT NULL,
                    sunday_dinner VARCHAR(100) NOT NULL,
                    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    suggestion_period_start DATE,
                    suggestion_period_end DATE
                );
            """)
            results.append("Created testapp_weekly_suggestion table")
            
            # Create testapp_suggestionperiod table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_suggestionperiod (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    submission_deadline DATE NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            results.append("Created testapp_suggestionperiod table")
            
            # Create testapp_feedbackperiod table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_feedbackperiod (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    submission_deadline DATE NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            results.append("Created testapp_feedbackperiod table")
            
            # Create testapp_complaint table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS testapp_complaint (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_name VARCHAR(100) NOT NULL,
                    email VARCHAR(254) NOT NULL,
                    mess_name VARCHAR(100),
                    message TEXT NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            results.append("Created testapp_complaint table")
            
        except Exception as e:
            results.append(f"Manual table creation error: {str(e)}")
        
        # Run migrations
        try:
            call_command('migrate', verbosity=0, interactive=False)
            results.append("Migrations completed successfully")
        except Exception as e:
            results.append(f"Migration error: {str(e)}")
        
        # Check if User table exists and is accessible
        try:
            user_count = User.objects.count()
            results.append(f"User table accessible, contains {user_count} users")
        except Exception as e:
            results.append(f"User table error: {str(e)}")
        
        # Create superuser if doesn't exist
        try:
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@mitadt.edu.in',
                    password='admin123'
                )
                results.append("Created admin superuser")
            else:
                results.append("Admin superuser already exists")
                
            # Create mess-specific admin users
            mess_admins = [
                {'username': 'raj_admin', 'email': 'raj.admin@mitadt.edu.in', 'password': 'raj123'},
                {'username': 'manet_admin', 'email': 'manet.admin@mitadt.edu.in', 'password': 'manet123'},
                {'username': 'design_admin', 'email': 'design.admin@mitadt.edu.in', 'password': 'design123'},
            ]
            
            for admin_data in mess_admins:
                if not User.objects.filter(username=admin_data['username']).exists():
                    User.objects.create_user(
                        username=admin_data['username'],
                        email=admin_data['email'],
                        password=admin_data['password'],
                        is_staff=True
                    )
                    results.append(f"Created {admin_data['username']} admin user")
                else:
                    results.append(f"{admin_data['username']} admin user already exists")
                    
        except Exception as e:
            results.append(f"Admin user creation error: {str(e)}")
        
        # Test user creation to verify everything works
        try:
            test_username = f'testuser_{User.objects.count()}'
            test_user, created = User.objects.get_or_create(
                username=test_username,
                defaults={
                    'email': f'{test_username}@example.com',
                    'is_active': True
                }
            )
            if created:
                test_user.set_password('testpass')
                test_user.save()
                results.append(f"Created test user: {test_username}")
            else:
                results.append(f"Test user already exists: {test_username}")
        except Exception as e:
            results.append(f"Test user creation error: {str(e)}")
        
        # Add sample Manet menu data
        try:
            from .models import manet_menu
            
            # Check if sample data already exists
            if manet_menu.objects.count() == 0:
                sample_dishes = [
                    {'name': 'Aloo Paratha', 'meal': 'breakfast', 'day': 'monday'},
                    {'name': 'Tea/Coffee', 'meal': 'breakfast', 'day': 'monday'},
                    {'name': 'Dal Rice', 'meal': 'lunch', 'day': 'monday'},
                    {'name': 'Vegetable Curry', 'meal': 'lunch', 'day': 'monday'},
                    {'name': 'Chapati', 'meal': 'dinner', 'day': 'monday'},
                    {'name': 'Paneer Curry', 'meal': 'dinner', 'day': 'monday'},
                    
                    {'name': 'Poha', 'meal': 'breakfast', 'day': 'tuesday'},
                    {'name': 'Tea/Coffee', 'meal': 'breakfast', 'day': 'tuesday'},
                    {'name': 'Rajma Rice', 'meal': 'lunch', 'day': 'tuesday'},
                    {'name': 'Mixed Vegetables', 'meal': 'lunch', 'day': 'tuesday'},
                    {'name': 'Roti', 'meal': 'dinner', 'day': 'tuesday'},
                    {'name': 'Dal Tadka', 'meal': 'dinner', 'day': 'tuesday'},
                ]
                
                for dish_data in sample_dishes:
                    manet_menu.objects.create(**dish_data)
                
                results.append(f"Created {len(sample_dishes)} sample Manet menu items")
            else:
                results.append(f"Manet menu already has {manet_menu.objects.count()} items")
                
        except Exception as e:
            results.append(f"Sample data creation error: {str(e)}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Database initialization completed',
            'results': results,
            'total_users': User.objects.count() if 'User table accessible' in str(results) else 0
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Database initialization failed: {str(e)}',
            'debug_info': 'Check server logs for details'
        })

# Create your views here.

def index_view(request):
    """Main index page"""
    try:
        # Safely check authentication without triggering session errors
        is_authenticated = False
        user = None
        
        try:
            is_authenticated = request.user.is_authenticated
            user = request.user if is_authenticated else None
        except Exception as session_error:
            # If session fails, treat as anonymous user
            is_authenticated = False
            user = None
        
        context = {
            'user': user,
            'is_authenticated': is_authenticated,
            'safe_user_authenticated': is_authenticated  # For template safety
        }
        
        # Add cache control headers to prevent browser caching issues
        response = render(request, 'testapp/index.html', context)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
        
    except Exception as e:
        # Fallback: render basic page without user context
        context = {
            'user': None,
            'is_authenticated': False,
            'safe_user_authenticated': False
        }
        response = render(request, 'testapp/index.html', context)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

#manet page 
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg
import json
@login_required(login_url='login')
def manet_mess_view(request):
    days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    meals = ['breakfast','lunch','dinner']

    # ✅ Default values when user first enters page
    selected_day = request.GET.get('day', '')
    selected_meal = request.GET.get('meal', '')

    dishes = []
    
    # ✅ Only fetch dishes if user selected both day & meal
    if selected_day and selected_meal:
        qs = manet_menu.objects.filter(day=selected_day, meal=selected_meal)
        for d in qs:
            dishes.append({
                'id': d.id,
                'name': d.name,
                'image': d.image,
                'average_rating_val': d.average_rating(),
                'user_rating_val': d.user_rating(request.user)
            })

    # Get notices for the page
    try:
        from .models import Notice
        notices = Notice.objects.filter(is_published=True).order_by('-created_at')[:4]
    except:
        notices = []

    return render(request, 'testapp/MANET_mess.html', {
        'days': days,
        'meals': meals,
        'selected_day': selected_day,
        'selected_meal': selected_meal,
        'dishes': dishes,
        'rating_range': range(1,6),
        'notices': notices,
    })

@login_required
def rate_manet_dish(request):
    dish_id = request.POST.get("dish_id")
    rating = int(request.POST.get("rating", 0))

    dish = manet_menu.objects.get(id=dish_id)
    r, created = ManetRating.objects.get_or_create(user=request.user, dish=dish)
    r.rating = rating
    r.save()

    avg = dish.ratings.aggregate(avg=Avg("rating"))["avg"] or 0
    return JsonResponse({"average_rating": round(avg, 1)})

#manet admin page    
from django.shortcuts import render, redirect
from .forms import DesignForm, ManetForm
from .models import DesignRating, Dish, DishRating, ManetRating,design_menu, manet_menu

def manet_add_dish(request):
    if request.method == 'POST':
        form = ManetForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_manet_mess')
    else:
        form = ManetForm()

    # Group dishes day → meal → dishes
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    meals = ["breakfast", "lunch", "dinner"]

    menu = {}
    for day in days:
        menu[day] = {}
        for meal in meals:
            menu[day][meal] = manet_menu.objects.filter(day=day, meal=meal)

    return render(request, 'testapp/admin_manet_mess.html', {
        'form': form,
        'menu': menu
    })



from django.shortcuts import render, get_object_or_404
from .models import Dish
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def raj_mess_view(request):
    days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    meals = ['breakfast','lunch','dinner']

    selected_day = request.GET.get('day')
    selected_meal = request.GET.get('meal')

    dishes = None  # ✅ Initially no dishes

    if selected_day and selected_meal:  # ✅ Only fetch after user selects
        dishes_qs = Dish.objects.filter(day=selected_day, meal=selected_meal).order_by('id')

        dishes = []  # ✅ list, not None
        for dish in dishes_qs:
            dishes.append({
                'id': dish.id,
                'name': dish.name,
                'image': dish.image,
                'average_rating_val': dish.average_rating(),
                'user_rating_val': dish.user_rating(request.user)
            })

    # Get notices for the page
    try:
        from .models import Notice
        notices = Notice.objects.filter(is_published=True).order_by('-created_at')[:4]
    except:
        notices = []

    context = {
        'days': days,
        'meals': meals,
        'selected_day': selected_day,
        'selected_meal': selected_meal,
        'dishes': dishes,
        'rating_range': range(1, 6),
        'notices': notices,
    }
    return render(request, 'testapp/raj_mess.html', context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Dish, DishRating
@login_required(login_url='login')
def rate_dish(request):
    if request.method == "POST":
        dish_id = request.POST.get("dish_id")
        rating_value = int(request.POST.get("rating"))

        dish = get_object_or_404(Dish, id=dish_id)

        DishRating.objects.update_or_create(
            user=request.user,
            dish=dish,
            defaults={"rating": rating_value}
        )

        agg = DishRating.objects.filter(dish=dish).aggregate(avg=Avg("rating"))
        avg_rating = round(agg["avg"], 1) if agg["avg"] else 0
        count = DishRating.objects.filter(dish=dish).count()

        return JsonResponse({
            "success": True,
            "average_rating": avg_rating,
            "your_rating": rating_value,
            "rating_count": count
        })
    return JsonResponse({"success": False}, status=400)

#raj mfrom django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Dish
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Dish, Weekly_suggestion

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64


DAYS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
MEALS = ['breakfast','lunch','dinner']


def create_pie_base64(counts_dict, title):
    fig, ax = plt.subplots(figsize=(4,3), dpi=100)
    
    if counts_dict:
        ax.pie(counts_dict.values(), labels=counts_dict.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
    else:
        ax.text(0.5,0.5,"No Data",ha="center",va="center",fontsize=12)
        ax.axis("off")

    ax.set_title(title, fontsize=10)
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    return encoded


def get_feedback_graphs():
    graphs = []

    for day in DAYS:
        for meal in MEALS:
            field = f"{day}_{meal}"
            data =Weekly_suggestion.objects.values_list(field, flat=True)

            counts = {}
            for d in data:
                if d:
                    counts[d] = counts.get(d, 0) + 1

            img = create_pie_base64(counts, f"{day.title()} - {meal.title()} Feedback")
            graphs.append({
                "day": day.title(),
                "meal": meal.title(),
                "image": img,
                "counts": counts
            })
    return graphs

# testapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Dish, Notice
# import your DAYS, MEALS, get_feedback_graphs etc.

@login_required(login_url='login')
def add_dish(request, mess_id=1):
    days = DAYS
    meals = MEALS

    # Handle Dish form submission (existing behavior)
    if request.method == "POST" and "name" in request.POST:
        name = request.POST.get('name')
        image = request.FILES.get('image')
        day = request.POST.get('day')
        meal = request.POST.get('meal')

        if Dish.objects.filter(mess_id=mess_id, day=day, meal=meal).exists():
            messages.error(request, f"{day.title()} - {meal.title()} meal already exists for this mess.")
            return redirect('admin_raj_mess', mess_id=mess_id)

        Dish.objects.create(
            mess_id=mess_id,
            name=name,
            image=image,
            day=day,
            meal=meal
        )
        messages.success(request, "Dish added successfully ✅")
        return redirect('admin_raj_mess', mess_id=mess_id)

    # Handle Notice form submission (same page)
    if request.method == "POST" and "title" in request.POST:
        title = request.POST.get('title')
        body = request.POST.get('body')
        attachment = request.FILES.get('attachment')
        is_published = request.POST.get('is_published') == 'on'
        Notice.objects.create(title=title, body=body, attachment=attachment, is_published=is_published)
        messages.success(request, "Notice saved.")
        return redirect('admin_raj_mess', mess_id=mess_id)

    dishes = Dish.objects.filter(mess_id=mess_id).order_by('day','meal')
    feedback_graphs = get_feedback_graphs()

    # include notices for admin table
    notices = Notice.objects.all()

    complaints = Complaint.objects.all().order_by('-id')

    return render(request, "testapp/add_dish.html", {
        "days": days,
        "meals": meals,
        "dishes": dishes,
        "mess_id": mess_id,
        "feedback_graphs": feedback_graphs,
        "notices": notices,
        'complaints':complaints
    })


@login_required(login_url='login')
def delete_notice(request, id, mess_id=1):
    # optional: restrict to staff only
    n = get_object_or_404(Notice, id=id)
    n.delete()
    messages.success(request, "Notice deleted.")
    # redirect back to admin page (mess_id preserved)
    return redirect('admin_raj_mess', mess_id=mess_id)


def delete_dish(request, id):
    dish = get_object_or_404(Dish, id=id)
    mess_id = dish.mess_id

    if request.method == 'POST':
        dish.delete()
        messages.success(request, "Dish deleted successfully ✅")

    return redirect('admin_raj_mess') if mess_id == 1 else redirect('admin_mess', mess_id=mess_id)


from django.db.models import Avg



def design_mess_admin_view(request):
    if request.method == 'POST':
        form = DesignForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Design menu item added successfully!')
            return redirect('admin_design_mess')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DesignForm()

    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    meals = ["breakfast", "lunch", "dinner"]

    # Get all design menu items
    dishes = design_menu.objects.all().order_by('-id')
    
    context = {
        'form': form,
        'days': days,
        'meals': meals,
        'dishes': dishes,
        'user': request.user,
    }
    
    return render(request, 'testapp/admin_design_mess.html', context)
# testapp/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import design_menu, DesignRating


@login_required(login_url='login')
def design_mess_view(request):
    days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
    meals = ['breakfast','lunch','dinner']

    selected_day = request.GET.get('day', days[0])
    selected_meal = request.GET.get('meal', meals[0])

    qs = design_menu.objects.filter(day=selected_day, meal=selected_meal).order_by('id')

    dishes = []
    for dish in qs:
        # ✅ Average rating for this dish
        avg = DesignRating.objects.filter(design_menu=dish).aggregate(avg=Avg('rating'))['avg']
        avg = round(avg, 1) if avg else 0

        # ✅ Logged-in user's rating
        ur = DesignRating.objects.filter(design_menu=dish, user=request.user).first()
        user_rating_val = ur.rating if ur else 0

        dishes.append({
            'id': dish.id,
            'name': dish.name,
            'image': dish.image,
            'average_rating_val': avg,
            'user_rating_val': user_rating_val,
        })

    # Get notices for the page
    try:
        from .models import Notice
        notices = Notice.objects.filter(is_published=True).order_by('-created_at')[:4]
    except:
        notices = []

    context = {
        'days': days,
        'meals': meals,
        'selected_day': selected_day,
        'selected_meal': selected_meal,
        'dishes': dishes,
        'rating_range': range(1,6),
        'notices': notices,
    }
    return render(request, 'testapp/design_mess.html', context)


@login_required(login_url='login')
def rate_design_dish(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    dish_id = request.POST.get('dish_id')
    rating = request.POST.get('rating')

    if not dish_id or not rating:
        return JsonResponse({'success': False, 'message': 'Missing parameters'}, status=400)

    try:
        rating_value = int(rating)
        if rating_value < 1 or rating_value > 5:
            raise ValueError()
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Invalid rating'}, status=400)

    dish = get_object_or_404(design_menu, id=dish_id)

    # ✅ Create/update user rating
    DesignRating.objects.update_or_create(
        user=request.user,
        design_menu=dish,
        defaults={'rating': rating_value}
    )

    # ✅ Recalculate average
    avg = DesignRating.objects.filter(design_menu=dish).aggregate(avg=Avg('rating'))['avg']
    avg = round(avg, 1) if avg else 0

    return JsonResponse({
        'success': True,
        'average_rating': avg,
        'your_rating': rating_value
    })

def simple_signup_view(request):
    """Working signup page that bypasses browser interference"""
    return render(request, 'testapp/working_signup.html')


def check_users_view(request):
    """Debug view to check what users exist"""
    try:
        users = User.objects.all()
        user_info = []
        for user in users:
            user_info.append({
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'total_users': len(user_info),
            'users': user_info
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})


def populate_sample_data(request):
    """Populate sample data for all messes"""
    try:
        from .models import manet_menu, design_menu
        results = []
        
        # Manet menu sample data
        if manet_menu.objects.count() == 0:
            manet_dishes = [
                {'name': 'Aloo Paratha', 'meal': 'breakfast', 'day': 'monday'},
                {'name': 'Tea/Coffee', 'meal': 'breakfast', 'day': 'monday'},
                {'name': 'Dal Rice', 'meal': 'lunch', 'day': 'monday'},
                {'name': 'Vegetable Curry', 'meal': 'lunch', 'day': 'monday'},
                {'name': 'Chapati', 'meal': 'dinner', 'day': 'monday'},
                {'name': 'Paneer Curry', 'meal': 'dinner', 'day': 'monday'},
                
                {'name': 'Poha', 'meal': 'breakfast', 'day': 'tuesday'},
                {'name': 'Tea/Coffee', 'meal': 'breakfast', 'day': 'tuesday'},
                {'name': 'Rajma Rice', 'meal': 'lunch', 'day': 'tuesday'},
                {'name': 'Mixed Vegetables', 'meal': 'lunch', 'day': 'tuesday'},
                {'name': 'Roti', 'meal': 'dinner', 'day': 'tuesday'},
                {'name': 'Dal Tadka', 'meal': 'dinner', 'day': 'tuesday'},
                
                {'name': 'Upma', 'meal': 'breakfast', 'day': 'wednesday'},
                {'name': 'Tea/Coffee', 'meal': 'breakfast', 'day': 'wednesday'},
                {'name': 'Chole Rice', 'meal': 'lunch', 'day': 'wednesday'},
                {'name': 'Aloo Gobi', 'meal': 'lunch', 'day': 'wednesday'},
                {'name': 'Chapati', 'meal': 'dinner', 'day': 'wednesday'},
                {'name': 'Palak Paneer', 'meal': 'dinner', 'day': 'wednesday'},
            ]
            
            for dish_data in manet_dishes:
                manet_menu.objects.create(**dish_data)
            
            results.append(f"Created {len(manet_dishes)} Manet menu items")
        else:
            results.append(f"Manet menu already has {manet_menu.objects.count()} items")
        
        # Design menu sample data
        if design_menu.objects.count() == 0:
            design_dishes = [
                {'name': 'Sandwich', 'meal': 'breakfast', 'day': 'monday'},
                {'name': 'Fresh Juice', 'meal': 'breakfast', 'day': 'monday'},
                {'name': 'Pasta', 'meal': 'lunch', 'day': 'monday'},
                {'name': 'Salad', 'meal': 'lunch', 'day': 'monday'},
                {'name': 'Pizza', 'meal': 'dinner', 'day': 'monday'},
                {'name': 'Soup', 'meal': 'dinner', 'day': 'monday'},
                
                {'name': 'Pancakes', 'meal': 'breakfast', 'day': 'tuesday'},
                {'name': 'Coffee', 'meal': 'breakfast', 'day': 'tuesday'},
                {'name': 'Burger', 'meal': 'lunch', 'day': 'tuesday'},
                {'name': 'Fries', 'meal': 'lunch', 'day': 'tuesday'},
                {'name': 'Grilled Chicken', 'meal': 'dinner', 'day': 'tuesday'},
                {'name': 'Rice', 'meal': 'dinner', 'day': 'tuesday'},
            ]
            
            for dish_data in design_dishes:
                design_menu.objects.create(**dish_data)
            
            results.append(f"Created {len(design_dishes)} Design menu items")
        else:
            results.append(f"Design menu already has {design_menu.objects.count()} items")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Sample data populated successfully',
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to populate sample data: {str(e)}'
        })


def fix_sessions(request):
    """Fix session-related issues"""
    try:
        from django.core.management import call_command
        results = []
        
        # Clear any existing session data
        try:
            request.session.flush()
            results.append("Cleared existing session data")
        except:
            results.append("No session data to clear")
        
        # Run migrations for sessions
        try:
            call_command('migrate', 'sessions', verbosity=0, interactive=False)
            results.append("Applied session migrations")
        except Exception as e:
            results.append(f"Session migration error: {str(e)}")
        
        # Test session functionality
        try:
            request.session['test'] = 'working'
            test_value = request.session.get('test')
            if test_value == 'working':
                results.append("Session functionality test: PASSED")
                del request.session['test']
            else:
                results.append("Session functionality test: FAILED")
        except Exception as e:
            results.append(f"Session test error: {str(e)}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Session fix completed',
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Session fix failed: {str(e)}'
        })

def sign_up_views(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')

        # Validation
        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, 'testapp/signup.html')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'testapp/signup.html')
        
        try:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already in use.')
                return render(request, 'testapp/signup.html')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
                return render(request, 'testapp/signup.html')
            
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
            
        except Exception as e:
            messages.error(request, "Failed to create account. Please try again.")
            return render(request, 'testapp/signup.html')
    
    return render(request, 'testapp/signup.html')

def login_view(request):
    # Handle any database initialization issues first
    try:
        # Test database connectivity
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as db_error:
        messages.error(request, f"Database not ready. Please visit /init-db/ first. Error: {str(db_error)}")
        return render(request, 'testapp/working_login.html')
    
    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email_or_username or not password:
            messages.error(request, "Please provide both email/username and password.")
            return render(request, 'testapp/working_login.html')
        
        try:
            # First, try to initialize database if tables are missing
            try:
                from django.core.management import call_command
                call_command('migrate', verbosity=0, interactive=False)
            except:
                pass
            
            # Debug: Let's see what we're looking for
            print(f"DEBUG: Looking for user: '{email_or_username}'")
            
            # Try to find user by email first
            user = None
            if '@' in email_or_username:
                # It's an email
                try:
                    user = User.objects.get(email=email_or_username)
                    print(f"DEBUG: Found user by email: {user.username}")
                except User.DoesNotExist:
                    print(f"DEBUG: No user found with email: {email_or_username}")
                    pass
            
            # If not found by email, try username
            if user is None:
                try:
                    user = User.objects.get(username=email_or_username)
                    print(f"DEBUG: Found user by username: {user.username}")
                except User.DoesNotExist:
                    print(f"DEBUG: No user found with username: {email_or_username}")
                    pass
            
            if user is None:
                # Let's see what users actually exist
                try:
                    all_users = User.objects.all()
                    print(f"DEBUG: Available users: {[u.username for u in all_users]}")
                    messages.error(request, f"No account found with '{email_or_username}'. Please visit /init-db/ first to create admin user.")
                except Exception as db_error:
                    messages.error(request, f"Database not ready. Please visit /init-db/ first. Error: {str(db_error)}")
                return render(request, 'testapp/working_login.html')
            
            # Check password
            print(f"DEBUG: Checking password for user: {user.username}")
            if user.check_password(password):
                print(f"DEBUG: Password correct for user: {user.username}")
                try:
                    # Try to login with session
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    
                    # Clear any password manager interference
                    response = redirect('index')
                    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response['Pragma'] = 'no-cache'
                    response['Expires'] = '0'
                    return response
                    
                except Exception as session_error:
                    print(f"DEBUG: Session error during login: {str(session_error)}")
                    # If session login fails, try to initialize database and retry
                    try:
                        from django.core.management import call_command
                        call_command('migrate', verbosity=0, interactive=False)
                        
                        # Try login again
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.username}! (Database initialized)")
                        return redirect('index')
                        
                    except Exception as retry_error:
                        print(f"DEBUG: Retry login failed: {str(retry_error)}")
                        # Show success but redirect to a safe page
                        messages.success(request, f"Login successful for {user.username}! Please visit /init-db/ to fix session issues.")
                        return render(request, 'testapp/working_login.html', {
                            'login_success': True, 
                            'user': user,
                            'session_error': True
                        })
            else:
                print(f"DEBUG: Password incorrect for user: {user.username}")
                messages.error(request, f"Incorrect password for user '{user.username}'.")
                
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            messages.error(request, f"Login failed: {str(e)}. Please visit /init-db/ first.")

    return render(request, 'testapp/working_login.html')    

def logout_view(request):
    """Logout user and redirect to home page"""
    try:
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, "You have been logged out successfully.")
        return redirect('index')
    except Exception as e:
        # If logout fails due to database issues, clear session manually
        try:
            request.session.flush()
        except:
            pass
        messages.info(request, "Logged out (session cleared).")
        return redirect('index')


def forgot_password_view(request):
    """Forgot password page"""
    if request.method == 'POST':
        email_or_username = request.POST.get('email_or_username', '').strip()
        
        if not email_or_username:
            messages.error(request, "Please provide your email or username.")
            return render(request, 'testapp/forgot_password.html')
        
        try:
            # Try to find user by email first
            user = None
            if '@' in email_or_username:
                try:
                    user = User.objects.get(email=email_or_username)
                except User.DoesNotExist:
                    pass
            
            # If not found by email, try username
            if user is None:
                try:
                    user = User.objects.get(username=email_or_username)
                except User.DoesNotExist:
                    pass
            
            if user is None:
                messages.error(request, "No account found with this email/username.")
                return render(request, 'testapp/forgot_password.html')
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # For development/demo purposes, show the reset link instead of sending email
            # In production, you would send this via email
            messages.success(request, f"Password reset link: {reset_link}")
            
            # Uncomment below for actual email sending in production:
            # try:
            #     send_mail(
            #         'Password Reset - MIT ADT Mess',
            #         f'Click this link to reset your password: {reset_link}',
            #         settings.DEFAULT_FROM_EMAIL,
            #         [user.email],
            #         fail_silently=False,
            #     )
            #     messages.success(request, "Password reset link sent to your email.")
            # except Exception as e:
            #     messages.error(request, "Failed to send email. Please try again.")
            
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
    
    return render(request, 'testapp/forgot_password.html')


def password_reset_confirm_view(request, uidb64, token):
    """Password reset confirmation page"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not new_password or not confirm_password:
                messages.error(request, "Please fill in both password fields.")
                return render(request, 'testapp/password_reset_confirm.html', {'valid_link': True})
            
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'testapp/password_reset_confirm.html', {'valid_link': True})
            
            if len(new_password) < 6:
                messages.error(request, "Password must be at least 6 characters long.")
                return render(request, 'testapp/password_reset_confirm.html', {'valid_link': True})
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            messages.success(request, "Password reset successful! You can now login with your new password.")
            return redirect('login')
        
        return render(request, 'testapp/password_reset_confirm.html', {'valid_link': True})
    else:
        messages.error(request, "Invalid or expired password reset link.")
        return render(request, 'testapp/password_reset_confirm.html', {'valid_link': False})


#after filling feedback then we have to submit the form using these 

# testapp/views.py
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import WeeklysuggestionForm
from django.db import IntegrityError

def weekly_suggestion(request):
    """
    Handles GET and POST for weekly suggestions with duplicate prevention.
    - Accepts ?mess=<mess_key> in querystring (or hidden input 'mess_name' in POST)
    - Builds day_fields for template (so template stays generic)
    - Validates mess_name and prevents NOT NULL insertion
    - Prevents duplicate submissions per email per period
    - Shows success message and redirects to 'suggestion_success'
    """
    # Import models inside function to avoid import-time errors
    from .models import SuggestionPeriod, Weekly_suggestion
    
    # Get current suggestion period
    current_period = None
    try:
        current_period = SuggestionPeriod.get_current_period()
    except Exception as period_error:
        # If period check fails, create a basic period for now
        messages.warning(request, "Suggestion period system is initializing. Please try again in a moment.")
    
    # Check if suggestion collection is currently active
    if not current_period or not current_period.is_submission_allowed():
        # Still build day_fields even when period is closed
        form = WeeklysuggestionForm()
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_fields = []
        for day in days:
            key_base = day.lower()
            bf_name = f"{key_base}_breakfast"
            lf_name = f"{key_base}_lunch"
            df_name = f"{key_base}_dinner"

            day_fields.append({
                "day": day,
                "bf_name": bf_name,
                "lf_name": lf_name,
                "df_name": df_name,
                "bf": form[bf_name] if bf_name in form.fields else None,
                "lf": form[lf_name] if lf_name in form.fields else None,
                "df": form[df_name] if df_name in form.fields else None,
            })
        
        return render(request, "testapp/weekly_suggestion.html", {
            "form": form,
            "period_closed": True,
            "current_period": current_period,
            "mess_name": None,
            "day_fields": day_fields,
            "week_start": date.today().strftime("%b %d, %Y"),
            "week_end": date.today().strftime("%b %d, %Y"),
            "deadline": date.today().strftime("%b %d, %Y"),
        })
    
    # Prefer querystring mess, but accept hidden input in POST too
    mess_name_from_query = request.GET.get('mess')
    mess_name_from_post = request.POST.get('mess_name') if request.method == "POST" else None
    mess_name_query_or_post = mess_name_from_query or mess_name_from_post

    # Use current period dates instead of calculating week
    start_of_week = current_period.start_date
    end_of_week = current_period.end_date
    deadline = current_period.submission_deadline

    # Days to render
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Check if user already submitted (for authenticated users)
    already_submitted = False
    if request.user.is_authenticated and hasattr(request.user, 'email') and request.user.email:
        try:
            # Check if user already submitted for this specific mess in this period
            mess_to_check = mess_name_query_or_post or 'MANET Mess'  # Default to MANET if no mess specified
            existing_suggestion = Weekly_suggestion.objects.filter(
                email=request.user.email,
                mess_name=mess_to_check,
                suggestion_period_start=current_period.start_date,
                suggestion_period_end=current_period.end_date
            ).exists()
            already_submitted = existing_suggestion
        except Exception:
            # If duplicate check fails, assume not submitted
            already_submitted = False

    if request.method == "POST":
        form = WeeklysuggestionForm(request.POST)

        # Always build day_fields from the form for template rendering
        day_fields = []
        for day in days:
            key_base = day.lower()
            bf_name = f"{key_base}_breakfast"
            lf_name = f"{key_base}_lunch"
            df_name = f"{key_base}_dinner"

            day_fields.append({
                "day": day,
                "bf_name": bf_name,
                "lf_name": lf_name,
                "df_name": df_name,
                "bf": form[bf_name] if bf_name in form.fields else None,
                "lf": form[lf_name] if lf_name in form.fields else None,
                "df": form[df_name] if df_name in form.fields else None,
            })

        if form.is_valid():
            # Determine final mess_name first (needed for duplicate check)
            mess_name = mess_name_from_query or mess_name_from_post or form.cleaned_data.get('mess_name')
            
            if not mess_name:
                # safe handling: add form error and fall through to render again
                form.add_error('mess_name', "Please select a mess.")
                context = {
                    "form": form,
                    "mess_name": mess_name_query_or_post,
                    "day_fields": day_fields,
                    "week_start": start_of_week.strftime("%b %d, %Y"),
                    "week_end": end_of_week.strftime("%b %d, %Y"),
                    "deadline": deadline.strftime("%b %d, %Y"),
                    "current_period": current_period,
                    "already_submitted": already_submitted
                }
                return render(request, "testapp/weekly_suggestion.html", context)
            
            # Check for duplicate submission by email + mess_name + period
            email = form.cleaned_data['email']
            try:
                existing_suggestion = Weekly_suggestion.objects.filter(
                    email=email,
                    mess_name=mess_name,
                    suggestion_period_start=current_period.start_date,
                    suggestion_period_end=current_period.end_date
                ).exists()
                
                if existing_suggestion:
                    messages.error(request, f"You have already submitted a weekly suggestion for {mess_name} in the period {current_period.name}. Only one suggestion per mess per week is allowed.")
                    context = {
                        "form": form,
                        "mess_name": mess_name_query_or_post,
                        "day_fields": day_fields,
                        "week_start": start_of_week.strftime("%b %d, %Y"),
                        "week_end": end_of_week.strftime("%b %d, %Y"),
                        "deadline": deadline.strftime("%b %d, %Y"),
                        "current_period": current_period,
                        "already_submitted": True
                    }
                    return render(request, "testapp/weekly_suggestion.html", context)
            except Exception:
                # If duplicate check fails, proceed with save attempt
                pass

            feedback = form.save(commit=False)
            feedback.mess_name = mess_name
            # Add period information
            feedback.suggestion_period_start = current_period.start_date
            feedback.suggestion_period_end = current_period.end_date
            
            try:
                feedback.save()
                messages.success(request, f"Thank you — your weekly suggestion for {mess_name} was submitted successfully.")
                return redirect(reverse('suggestion_success'))
            except IntegrityError:
                messages.error(request, f"You have already submitted a weekly suggestion for {mess_name} in the period {current_period.name}. Only one suggestion per mess per week is allowed.")
                context = {
                    "form": form,
                    "mess_name": mess_name_query_or_post,
                    "day_fields": day_fields,
                    "week_start": start_of_week.strftime("%b %d, %Y"),
                    "week_end": end_of_week.strftime("%b %d, %Y"),
                    "deadline": deadline.strftime("%b %d, %Y"),
                    "current_period": current_period,
                    "already_submitted": True
                }
                return render(request, "testapp/weekly_suggestion.html", context)
            except Exception as save_error:
                messages.error(request, f"Error saving suggestion: {str(save_error)}. Please try again.")
                context = {
                    "form": form,
                    "mess_name": mess_name_query_or_post,
                    "day_fields": day_fields,
                    "week_start": start_of_week.strftime("%b %d, %Y"),
                    "week_end": end_of_week.strftime("%b %d, %Y"),
                    "deadline": deadline.strftime("%b %d, %Y"),
                    "current_period": current_period,
                    "already_submitted": already_submitted
                }
                return render(request, "testapp/weekly_suggestion.html", context)

        # If form is invalid, render with errors and day_fields
        context = {
            "form": form,
            "mess_name": mess_name_query_or_post,
            "day_fields": day_fields,
            "week_start": start_of_week.strftime("%b %d, %Y"),
            "week_end": end_of_week.strftime("%b %d, %Y"),
            "deadline": deadline.strftime("%b %d, %Y"),
            "current_period": current_period,
            "already_submitted": already_submitted
        }
        return render(request, "testapp/weekly_suggestion.html", context)

    # GET -> unbound form (pre-fill mess_name if provided in query)
    initial = {}
    if mess_name_from_query:
        initial['mess_name'] = mess_name_from_query

    form = WeeklysuggestionForm(initial=initial)

    # Always build day_fields for GET requests
    day_fields = []
    for day in days:
        key_base = day.lower()
        bf_name = f"{key_base}_breakfast"
        lf_name = f"{key_base}_lunch"
        df_name = f"{key_base}_dinner"

        day_fields.append({
            "day": day,
            "bf_name": bf_name,
            "lf_name": lf_name,
            "df_name": df_name,
            "bf": form[bf_name] if bf_name in form.fields else None,
            "lf": form[lf_name] if lf_name in form.fields else None,
            "df": form[df_name] if df_name in form.fields else None,
        })

    context = {
        "form": form,
        "mess_name": mess_name_query_or_post,
        "day_fields": day_fields,
        "week_start": start_of_week.strftime("%b %d, %Y"),
        "week_end": end_of_week.strftime("%b %d, %Y"),
        "deadline": deadline.strftime("%b %d, %Y"),
        "current_period": current_period,
        "already_submitted": already_submitted
    }
    
    return render(request, "testapp/weekly_suggestion.html", context)

#feedback successs page
def suggestion_success(request):
    return render(request, "testapp/suggestion_success.html")



def mess_payment_select(request):
    mess = request.GET.get("mess", "")
    meal = request.GET.get("meal", "")
    qty = int(request.GET.get("qty", 1))

    # Updated price logic to match MANET mess pricing
    price = 0
    if meal == "Breakfast":
        price = 40
    elif meal == "Lunch":
        price = 60
    elif meal == "Dinner":
        price = 80

    total = price * qty

    context = {
        "mess": mess,
        "meal": meal,
        "qty": qty,
        "price": price,
        "total": total
    }

    return render(request, "testapp/payment.html", context)

from django.shortcuts import render, redirect
from .forms import MessFeedbackForm
from django.utils import timezone
from django.db import IntegrityError
from django.contrib import messages

def feedback_form(request):
    # Import models inside function to avoid import-time errors
    from .models import FeedbackPeriod, MessFeedback
    
    # Get current feedback period
    current_period = FeedbackPeriod.get_current_period()
    
    # Check if feedback collection is currently active
    if not current_period or not current_period.is_submission_allowed():
        messages.error(request, "Feedback submission is currently not available. Please check back during the active feedback period.")
        return render(request, "testapp/feedback.html", {
            "form": None,
            "period_closed": True,
            "current_period": current_period
        })
    
    # Initialize variables
    already_submitted = False
    
    # Check if user already submitted (for GET requests)
    if request.user.is_authenticated and hasattr(request.user, 'email') and request.user.email:
        existing_feedback = MessFeedback.objects.filter(
            email=request.user.email,
            feedback_period_start=current_period.start_date,
            feedback_period_end=current_period.end_date
        ).exists()
        already_submitted = existing_feedback
    
    if request.method == "POST":
        form = MessFeedbackForm(request.POST)
        if form.is_valid():
            try:
                # Check if user already submitted feedback for this period
                email = form.cleaned_data['email']
                existing_feedback = MessFeedback.objects.filter(
                    email=email,
                    feedback_period_start=current_period.start_date,
                    feedback_period_end=current_period.end_date
                ).exists()
                
                if existing_feedback:
                    messages.error(request, f"You have already submitted feedback for the period {current_period.name}. Duplicate submissions are not allowed.")
                    return render(request, "testapp/feedback.html", {
                        "form": form,
                        "current_period": current_period,
                        "already_submitted": True
                    })
                
                # Save feedback with period information
                feedback = form.save(commit=False)
                feedback.feedback_period_start = current_period.start_date
                feedback.feedback_period_end = current_period.end_date
                feedback.save()
                
                # Redirect to success page
                return render(request, "testapp/feedback_success.html", {
                    "period": current_period,
                    "next_period_info": "Next feedback period will be announced soon."
                })
                
            except IntegrityError as e:
                messages.error(request, "You have already submitted feedback for this period. Duplicate submissions are not allowed.")
                return render(request, "testapp/feedback.html", {
                    "form": form,
                    "current_period": current_period,
                    "already_submitted": True
                })
            except Exception as e:
                messages.error(request, f"An error occurred while submitting your feedback. Please try again. Error: {str(e)}")
                return render(request, "testapp/feedback.html", {
                    "form": form,
                    "current_period": current_period,
                    "already_submitted": False
                })
        else:
            # Form validation errors
            messages.error(request, "Please correct the errors below and try again.")
    else:
        form = MessFeedbackForm()

    return render(request, "testapp/feedback.html", {
        "form": form,
        "current_period": current_period,
        "already_submitted": already_submitted
    })

def thank_you(request):
    return render(request, "thank_you.html")

# testapp/views.py
# testapp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Notice, Complaint
from .forms import ComplaintForm

def home(request):
    # latest 5 notices
    notices = Notice.objects.order_by('-created_at')[:5]
    # render home template and pass notices + (optionally) an unbound complaint form
    form = ComplaintForm()  # for rendering the complaint form in the same page
    return render(request, 'testapp/index.html', {'notices': notices, 'form': form})
# testapp/views.py  (updated complaint handling)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import ComplaintForm
from .models import Notice, Complaint

# Single view that handles both "submit from home" and "standalone complaint page"
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .forms import ComplaintForm
from .models import Notice  # if you use Notice in index rendering
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def complaint_view(request):
    """
    GET: show a complaint form (standalone complaint page)
    POST: validate + save complaint. On success redirect to:
        - request.POST['next'] if provided
        - otherwise 'index' for inline/home submissions
        - otherwise 'complaint_success' for standalone page submissions

    On validation error: re-render the page that submitted the form (index or complaint page)

    Also supports AJAX POST: returns JSON { ok: True/False, errors: {...} }.
    """
    # Decide redirect/response targets
    default_next = request.POST.get('next') or request.GET.get('next') or None
    ref = request.POST.get('ref') or request.GET.get('ref') or ''

    if request.method == "POST":
        form = ComplaintForm(request.POST)
        
        if form.is_valid():
            try:
                complaint = form.save()
                # Successful save
                messages.success(request, "✅ Thank you — your complaint/suggestion was submitted successfully!")

                # If explicit next provided, redirect there (template should provide a safe path/name)
                if default_next:
                    # If default_next is a URL name, redirect will attempt to resolve it; if it's a path it'll also work.
                    try:
                        return redirect(default_next)
                    except Exception:
                        # If redirect by name failed, redirect to path directly
                        return redirect(default_next)

                # If came from index/home page (explicit ref or referer contains 'index') -> index
                referer = request.META.get('HTTP_REFERER', '')
                if ref == 'index' or 'index' in referer:
                    return redirect('index')

                # otherwise go to standalone success page
                return redirect('complaint_success')
                
            except Exception as exc:
                # Save failed unexpectedly: log and return a server error view
                logger.exception("Failed to save ComplaintForm: %s", exc)
                
                # Provide more specific error message
                error_msg = "There was an internal error saving your complaint. Please try again later."
                if "UNIQUE constraint failed" in str(exc):
                    error_msg = "A complaint with this information already exists. Please modify your submission."
                elif "NOT NULL constraint failed" in str(exc):
                    error_msg = "Please fill in all required fields."
                else:
                    error_msg = f"Database error: {str(exc)}. Please contact support if this persists."
                
                messages.error(request, error_msg)
                
                # If it's an AJAX request, return JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"ok": False, "error": str(exc)}, status=500)
                # Render the standalone form with the current form (it will show no-form-level errors)
                return render(request, 'testapp/complaint_form.html', {'form': form})

        else:
            # form invalid -> prepare error response
            logger.debug("Complaint form invalid: %s", form.errors)

            # If AJAX, return JSON with field errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Convert errors to a simple dict: field -> list_of_errors
                errors = {k: [str(e) for e in v] for k, v in form.errors.items()}
                return JsonResponse({"ok": False, "errors": errors}, status=400)

            # If the form was posted from index (inline widget), re-render index with notices + form errors:
            if default_next == 'index' or request.POST.get('ref') == 'index':
                notices = Notice.objects.order_by('-created_at')[:5]
                return render(request, 'testapp/index.html', {'form': form, 'notices': notices})

            # otherwise render the standalone complaint form with errors
            return render(request, 'testapp/complaint_form.html', {'form': form})

    # GET -> show the standalone complaint page
    form = ComplaintForm()
    return render(request, 'testapp/complaint_form.html', {'form': form})

def complaint_success(request):
    """Simple thank-you page after complaint submission."""
    return render(request, "testapp/complaint_success.html")


def all_notices(request):
    """Page showing all notices (optionally paginate)"""
    notices = Notice.objects.filter(is_published=True).order_by('-created_at')
    return render(request, "testapp/all_notices.html", {"notices": notices})


def admin_login_view(request):
    """
    Dedicated admin login page
    """
    if request.user.is_authenticated:
        # If already logged in, redirect to admin dashboard
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if user is admin/staff
                if user.is_staff or user.is_superuser or 'admin' in user.username.lower():
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Access denied. Admin privileges required.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please enter both username and password.")
    
    return render(request, 'testapp/admin_login.html')


def admin_dashboard_view(request):
    """
    Admin dashboard that redirects to appropriate mess admin page
    Based on username pattern: raj_admin, manet_admin, design_admin
    """
    if not request.user.is_authenticated:
        messages.error(request, "Please login as admin first.")
        return redirect('login')
    
    username = request.user.username.lower()
    
    # Check admin type based on username
    if 'raj' in username or username == 'admin':
        return redirect('admin_raj_mess')
    elif 'manet' in username:
        return redirect('admin_manet_mess')  
    elif 'design' in username:
        return redirect('admin_design_mess')
    else:
        # Default admin dashboard with options
        context = {
            'user': request.user,
            'admin_options': [
                {'name': 'RAJ Mess Admin', 'url': 'admin_raj_mess', 'icon': 'fas fa-utensils', 'color': '#4caf50'},
                {'name': 'MANET Mess Admin', 'url': 'admin_manet_mess', 'icon': 'fas fa-utensils', 'color': '#ff6b35'},
                {'name': 'Design Mess Admin', 'url': 'admin_design_mess', 'icon': 'fas fa-utensils', 'color': '#9c27b0'},
            ]
        }
        return render(request, 'testapp/admin_dashboard.html', context)
def admin_login_view(request):
    """
    Dedicated admin login page
    """
    if request.user.is_authenticated:
        # If already logged in, redirect to admin dashboard
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if user is admin/staff
                if user.is_staff or user.is_superuser or 'admin' in user.username.lower():
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Access denied. Admin privileges required.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please enter both username and password.")

    return render(request, 'testapp/admin_login.html')


def admin_dashboard_view(request):
    """
    Admin dashboard that redirects to appropriate mess admin page
    Based on username pattern: raj_admin, manet_admin, design_admin
    """
    if not request.user.is_authenticated:
        messages.error(request, "Please login as admin first.")
        return redirect('admin_login')
    
    username = request.user.username.lower()
    
    # Check admin type based on username
    if 'raj' in username or username == 'admin':
        return redirect('admin_raj_mess')
    elif 'manet' in username:
        return redirect('admin_manet_mess')  
    elif 'design' in username:
        return redirect('admin_design_mess')
    else:
        # Default admin dashboard with options
        context = {
            'user': request.user,
            'admin_options': [
                {'name': 'RAJ Mess Admin', 'url': 'admin_raj_mess', 'icon': 'fas fa-utensils', 'color': '#4caf50'},
                {'name': 'MANET Mess Admin', 'url': 'admin_manet_mess', 'icon': 'fas fa-utensils', 'color': '#ff6b35'},
                {'name': 'Design Mess Admin', 'url': 'admin_design_mess', 'icon': 'fas fa-utensils', 'color': '#9c27b0'},
            ]
        }
        return render(request, 'testapp/admin_dashboard.html', context)