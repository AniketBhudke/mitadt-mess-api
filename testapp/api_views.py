from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import (
    Dish, DishRating, Notice, Complaint, Mess,
    manet_menu, ManetRating, design_menu, DesignRating,
    Weekly_suggestion, MessSelection, MessFeedback
)
from .serializers import (
    DishSerializer, DishRatingSerializer, NoticeSerializer, ComplaintSerializer,
    MessSerializer, ManetMenuSerializer, ManetRatingSerializer,
    DesignMenuSerializer, DesignRatingSerializer, WeeklySuggestionSerializer,
    MessSelectionSerializer, MessFeedbackSerializer, UserSerializer
)
from django.contrib.auth.models import User

# ============ DISH APIs ============

@extend_schema(
    summary="Get all dishes",
    description="Retrieve a list of all dishes available in all messes",
    responses={200: DishSerializer(many=True)}
)
@api_view(['GET'])
def dish_list_api(request):
    dishes = Dish.objects.all()
    serializer = DishSerializer(dishes, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="Get Raj Mess menu",
    description="Get dishes for Raj Mess filtered by day and meal type",
    parameters=[
        OpenApiParameter(name='day', type=OpenApiTypes.STR, description='Day of the week', required=False),
        OpenApiParameter(name='meal', type=OpenApiTypes.STR, description='Meal type (breakfast/lunch/dinner)', required=False),
    ],
    responses={200: DishSerializer(many=True)}
)
@api_view(['GET'])
def raj_mess_api(request):
    day = request.GET.get('day')
    meal = request.GET.get('meal')
    
    dishes = Dish.objects.filter(mess__name='RAJ')
    if day:
        dishes = dishes.filter(day=day)
    if meal:
        dishes = dishes.filter(meal=meal)
    
    serializer = DishSerializer(dishes, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="Rate a dish",
    description="Submit or update rating for a specific dish",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'dish_id': {'type': 'integer', 'description': 'ID of the dish to rate'},
                'rating': {'type': 'integer', 'description': 'Rating value (1-5)'}
            },
            'required': ['dish_id', 'rating']
        }
    },
    responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
)
@api_view(['POST'])
def rate_dish_api(request):
    dish_id = request.data.get("dish_id")
    rating = request.data.get("rating")
    
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    DishRating.objects.update_or_create(
        user=request.user,
        dish_id=dish_id,
        defaults={"rating": rating}
    )
    
    return Response({"message": "Rating saved successfully"})

# ============ MANET MESS APIs ============

@extend_schema(
    summary="Get Manet Mess menu",
    description="Get dishes for Manet Mess filtered by day and meal type",
    parameters=[
        OpenApiParameter(name='day', type=OpenApiTypes.STR, description='Day of the week', required=False),
        OpenApiParameter(name='meal', type=OpenApiTypes.STR, description='Meal type', required=False),
    ],
    responses={200: ManetMenuSerializer(many=True)}
)
@api_view(['GET'])
def manet_mess_api(request):
    day = request.GET.get('day')
    meal = request.GET.get('meal')
    
    dishes = manet_menu.objects.all()
    if day:
        dishes = dishes.filter(day=day)
    if meal:
        dishes = dishes.filter(meal=meal)
    
    serializer = ManetMenuSerializer(dishes, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="Rate Manet dish",
    description="Submit or update rating for a Manet mess dish",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'dish_id': {'type': 'integer'},
                'rating': {'type': 'integer', 'description': 'Rating (1-5)'}
            }
        }
    },
    responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
)
@api_view(['POST'])
def rate_manet_dish_api(request):
    dish_id = request.data.get("dish_id")
    rating = request.data.get("rating")
    
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    ManetRating.objects.update_or_create(
        user=request.user,
        dish_id=dish_id,
        defaults={"rating": rating}
    )
    
    return Response({"message": "Rating saved successfully"})

# ============ DESIGN MESS APIs ============

@extend_schema(
    summary="Get Design Mess menu",
    description="Get dishes for Design Mess filtered by day and meal type",
    parameters=[
        OpenApiParameter(name='day', type=OpenApiTypes.STR, description='Day of the week', required=False),
        OpenApiParameter(name='meal', type=OpenApiTypes.STR, description='Meal type', required=False),
    ],
    responses={200: DesignMenuSerializer(many=True)}
)
@api_view(['GET'])
def design_mess_api(request):
    day = request.GET.get('day')
    meal = request.GET.get('meal')
    
    dishes = design_menu.objects.all()
    if day:
        dishes = dishes.filter(day=day)
    if meal:
        dishes = dishes.filter(meal=meal)
    
    serializer = DesignMenuSerializer(dishes, many=True)
    return Response(serializer.data)

@extend_schema(
    summary="Rate Design dish",
    description="Submit or update rating for a Design mess dish",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'dish_id': {'type': 'integer'},
                'rating': {'type': 'integer', 'description': 'Rating (1-5)'}
            }
        }
    },
    responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
)
@api_view(['POST'])
def rate_design_dish_api(request):
    dish_id = request.data.get("dish_id")
    rating = request.data.get("rating")
    
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    DesignRating.objects.update_or_create(
        user=request.user,
        design_menu_id=dish_id,
        defaults={"rating": rating}
    )
    
    return Response({"message": "Rating saved successfully"})

# ============ MESS APIs ============

@extend_schema(
    summary="Get all messes",
    description="Retrieve list of all available messes",
    responses={200: MessSerializer(many=True)}
)
@api_view(['GET'])
def mess_list_api(request):
    messes = Mess.objects.all()
    serializer = MessSerializer(messes, many=True)
    return Response(serializer.data)

# ============ COMPLAINT API ============

@extend_schema(
    summary="Submit a complaint",
    description="Submit a new complaint about mess services",
    request=ComplaintSerializer,
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
        400: ComplaintSerializer
    }
)
@api_view(['POST'])
def complaint_api(request):
    serializer = ComplaintSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Complaint submitted successfully"
        })
    
    return Response(serializer.errors, status=400)

# ============ NOTICE API ============

@extend_schema(
    summary="Get published notices",
    description="Retrieve all published notices for the mess",
    responses={200: NoticeSerializer(many=True)}
)
@api_view(['GET'])
def notice_api(request):
    notices = Notice.objects.filter(is_published=True).order_by('-created_at')
    serializer = NoticeSerializer(notices, many=True)
    return Response(serializer.data)

# ============ FEEDBACK APIs ============

@extend_schema(
    summary="Submit feedback",
    description="Submit feedback about mess services",
    request=MessFeedbackSerializer,
    responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
)
@api_view(['POST'])
def feedback_api(request):
    serializer = MessFeedbackSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Feedback submitted successfully"})
    
    return Response(serializer.errors, status=400)

# ============ WEEKLY SUGGESTION API ============

@extend_schema(
    summary="Submit weekly meal suggestion",
    description="Submit suggestions for weekly meal menu",
    request=WeeklySuggestionSerializer,
    responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
)
@api_view(['POST'])
def weekly_suggestion_api(request):
    serializer = WeeklySuggestionSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Suggestion submitted successfully"})
    
    return Response(serializer.errors, status=400)

# ============ MESS SELECTION API ============

@extend_schema(
    summary="Select mess for payment",
    description="Submit mess selection for payment",
    request=MessSelectionSerializer,
    responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
)
@api_view(['POST'])
def mess_selection_api(request):
    serializer = MessSelectionSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Mess selection saved successfully"})
    
    return Response(serializer.errors, status=400)

# ============ AUTHENTICATION APIs ============

@extend_schema(
    summary="Login user",
    description="Authenticate user with email and password",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'description': 'User email'},
                'password': {'type': 'string', 'description': 'User password'}
            },
            'required': ['email', 'password']
        }
    },
    responses={
        200: {'type': 'object', 'properties': {'message': {'type': 'string'}, 'user': UserSerializer}},
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
@api_view(['POST'])
def login_api(request):
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    
    if not email or not password:
        return Response({"error": "Email and password are required"}, status=400)
    
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            # In a real app, you'd return a JWT token here
            return Response({
                "message": "Login successful",
                "user": UserSerializer(user).data
            })
        else:
            return Response({"error": "Invalid password"}, status=400)
    except User.DoesNotExist:
        return Response({"error": "No account found with this email"}, status=400)

@extend_schema(
    summary="Register user",
    description="Create a new user account",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'email': {'type': 'string'},
                'password': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'}
            },
            'required': ['username', 'email', 'password']
        }
    },
    responses={
        201: {'type': 'object', 'properties': {'message': {'type': 'string'}, 'user': UserSerializer}},
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
@api_view(['POST'])
def register_api(request):
    """Register a new user via API"""
    try:
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        
        if not username or not email or not password:
            return Response({"error": "Username, email, and password are required"}, status=400)
        
        # Validate password length
        if len(password) < 6:
            return Response({"error": "Password must be at least 6 characters long"}, status=400)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)
        
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=400)
        
        try:
            # Ensure database is ready
            User.objects.count()  # Test database access
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            return Response({
                "message": "Account created successfully",
                "user": UserSerializer(user).data
            }, status=201)
            
        except Exception as db_error:
            # If database error, try to initialize and retry once
            try:
                from django.core.management import call_command
                call_command('migrate', verbosity=0, interactive=False)
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                return Response({
                    "message": "Account created successfully (after database initialization)",
                    "user": UserSerializer(user).data
                }, status=201)
            except Exception as retry_error:
                return Response({
                    "error": "Database not ready. Please visit /init-db/ first, then try again.",
                    "debug": str(retry_error)
                }, status=500)
                
    except Exception as e:
        return Response({
            "error": "Failed to create account",
            "debug": str(e)
        }, status=400)

# ============ USER API ============

@extend_schema(
    summary="Get user profile",
    description="Get authenticated user's profile information",
    responses={200: UserSerializer}
)
@api_view(['GET'])
def user_profile_api(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
def users_list_api(request):
    """List all users (for debugging)"""
    try:
        users = User.objects.all()
        return Response({
            'count': users.count(),
            'users': [{'id': u.id, 'username': u.username, 'email': u.email, 'is_active': u.is_active} for u in users[:10]]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)