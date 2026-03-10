from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Dish
from .serializers import DishSerializer

@extend_schema(
    summary="Get all dishes",
    description="Retrieve a list of all dishes available in the mess",
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
        OpenApiParameter(name='day', type=OpenApiTypes.STR, description='Day of the week', required=True),
        OpenApiParameter(name='meal', type=OpenApiTypes.STR, description='Meal type (breakfast/lunch/dinner)', required=True),
    ],
    responses={200: DishSerializer(many=True)}
)
@api_view(['GET'])
def raj_mess_api(request):

    # get values from URL
    day = request.GET.get('day')
    meal = request.GET.get('meal')

    # filter database
    dishes = Dish.objects.filter(day=day, meal=meal)

    # convert to JSON
    serializer = DishSerializer(dishes, many=True)

    return Response(serializer.data)

from .models import DishRating
from django.contrib.auth.models import User

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

    DishRating.objects.update_or_create(
        user=request.user,
        dish_id=dish_id,
        defaults={"rating": rating}
    )

    return Response({
        "message": "Rating saved"
    })

from .serializers import ComplaintSerializer

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
            "message": "Complaint submitted"
        })

    return Response(serializer.errors)

from .models import Notice
from .serializers import NoticeSerializer

@extend_schema(
    summary="Get published notices",
    description="Retrieve all published notices for the mess",
    responses={200: NoticeSerializer(many=True)}
)
@api_view(['GET'])
def notice_api(request):

    notices = Notice.objects.filter(is_published=True)

    serializer = NoticeSerializer(notices, many=True)

    return Response(serializer.data)