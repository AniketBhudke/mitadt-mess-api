from django.urls import path
from .api_views import *

urlpatterns = [

    path('raj-mess/', raj_mess_api),

    path('rate-dish/', rate_dish_api),

    path('complaint/', complaint_api),

    path('notices/', notice_api),

]