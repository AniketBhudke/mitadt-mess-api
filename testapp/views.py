from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import  login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.

def index_view(request):
    return render(request, 'testapp/index.html')

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

    return render(request, 'testapp/MANET_mess.html', {
        'days': days,
        'meals': meals,
        'selected_day': selected_day,
        'selected_meal': selected_meal,
        'dishes': dishes,
        'rating_range': range(1,6)
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

    context = {
        'days': days,
        'meals': meals,
        'selected_day': selected_day,
        'selected_meal': selected_meal,
        'dishes': dishes,
        'rating_range': range(1, 6),
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
            return redirect('admin_design_mess')
    else:
        form = DesignForm()

    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    meals = ["breakfast", "lunch", "dinner"]

    menu = {}
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

    context = {
        'days': days,
        'meals': meals,
        'selected_day': selected_day,
        'selected_meal': selected_meal,
        'dishes': dishes,
        'rating_range': range(1,6)
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
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, "Please provide both email and password.")
            return render(request, 'testapp/login.html')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                messages.success(request, "Logged in successfully.")
                return redirect('index')
            else:
                messages.error(request, "Incorrect password.")
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
        except Exception as e:
            messages.error(request, "Login failed. Please try again.")

    return render(request, 'testapp/login.html')
    return render(request, 'testapp/login.html')    

def logout_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('index')
        
    return render(request,'testapp/logput.html')


#after filling feedback then we have to submit the form using these 

# testapp/views.py
# testapp/views.py
from django.shortcuts import render, redirect
from .forms import WeeklysuggestionForm

# testapp/views.py
# testapp/views.py
from datetime import date, timedelta
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import WeeklysuggestionForm

def weekly_suggestion(request):
    """
    Handles GET and POST for weekly suggestions.
    - Accepts ?mess=<mess_key> in querystring (or hidden input 'mess_name' in POST)
    - Builds day_fields for template (so template stays generic)
    - Validates mess_name and prevents NOT NULL insertion
    - Shows success message and redirects to 'suggestion_success'
    """

    # Prefer querystring mess, but accept hidden input in POST too
    mess_name_from_query = request.GET.get('mess')
    mess_name_from_post = request.POST.get('mess_name') if request.method == "POST" else None
    mess_name_query_or_post = mess_name_from_query or mess_name_from_post

    # Prepare week info: start and end of current week + deadline (previous day)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)          # Sunday
    # Set submission deadline to previous Sunday 23:59 (you can change)
    deadline = start_of_week - timedelta(days=1)

    # Days to render
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    if request.method == "POST":
        form = WeeklysuggestionForm(request.POST)

        # Build day_fields from the bound form for template rendering (BoundField objects)
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
            feedback = form.save(commit=False)

            # Determine final mess_name (querystring > posted hidden > form field)
            mess_name = mess_name_from_query or mess_name_from_post or form.cleaned_data.get('mess_name')

            if not mess_name:
                # safe handling: add form error and fall through to render again
                form.add_error('mess_name', "Please select a mess.")
            else:
                feedback.mess_name = mess_name
                feedback.save()
                messages.success(request, "Thank you — your weekly feedback was submitted.")
                return redirect(reverse('suggestion_success'))

        # If invalid or mess_name missing, render with errors
        context = {
            "form": form,
            "mess_name": mess_name_query_or_post,
            "day_fields": day_fields,
            "week_start": start_of_week.strftime("%b %d, %Y"),
            "week_end": end_of_week.strftime("%b %d, %Y"),
            "deadline": deadline.strftime("%b %d, %Y"),
        }
        return render(request, "testapp/weekly_suggestion.html", context)

    else:
        # GET -> unbound form (pre-fill mess_name if provided in query)
        initial = {}
        if mess_name_from_query:
            initial['mess_name'] = mess_name_from_query

        form = WeeklysuggestionForm(initial=initial)

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
        }
        return render(request, "testapp/weekly_suggestion.html", context)

#feedback successs page
def suggestion_success(request):
    return render(request, "testapp/suggestion_success.html")



def mess_payment_select(request):
    mess = request.GET.get("mess")
    meal = request.GET.get("meal")
    qty = int(request.GET.get("qty", 1))

    # Price logic (you can change)
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
        "total": total
    }

    return render(request, "testapp/payment.html", context)

from django.shortcuts import render, redirect
from .forms import MessFeedbackForm

def feedback_form(request):
    if request.method == "POST":
        form = MessFeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "testapp/thankyou.html")
    else:
        form = MessFeedbackForm()

    return render(request, "testapp/feedback.html", {"form": form})

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
        # Uncomment for quick debugging in dev server logs:
        # logger.debug("Complaint POST received: %s", request.POST)
        # print("DEBUG complaint_post:", request.POST)

        if form.is_valid():
            try:
                form.save()
            except Exception as exc:
                # Save failed unexpectedly: log and return a server error view
                logger.exception("Failed to save ComplaintForm: %s", exc)
                messages.error(request, "There was an internal error saving your complaint. Please try again later.")
                # If it's an AJAX request, return JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({"ok": False, "error": "internal_server_error"}, status=500)
                # Render the standalone form with the current form (it will show no-form-level errors)
                return render(request, 'testapp/complaint_form.html', {'form': form})

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
    notices = Notice.objects.order_by('-created_at')
    return render(request, 'testapp/complaint_form.html', {'notices': notices})
# testapp/views.py


# testapp/views.py
from django.shortcuts import render
from .models import Notice

def all_notices(request):
    # fetch all notices (newest first)
    notices = Notice.objects.order_by('-created_at')
    notices = Notice.objects.filter(is_published=True).order_by('-created_at')
    return render(request, "testapp/all_notices.html", {"notices": notices})
