from django.urls import path
from .api_views import *

urlpatterns = [
    # Authentication APIs
    path('auth/login/', login_api, name='login_api'),
    path('auth/register/', register_api, name='register_api'),
    
    # Dish APIs
    path('dishes/', dish_list_api, name='dish_list_api'),
    path('raj-mess/', raj_mess_api, name='raj_mess_api'),
    path('rate-dish/', rate_dish_api, name='rate_dish_api'),
    
    # Manet Mess APIs
    path('manet-mess/', manet_mess_api, name='manet_mess_api'),
    path('rate-manet-dish/', rate_manet_dish_api, name='rate_manet_dish_api'),
    
    # Design Mess APIs
    path('design-mess/', design_mess_api, name='design_mess_api'),
    path('rate-design-dish/', rate_design_dish_api, name='rate_design_dish_api'),
    
    # Mess APIs
    path('messes/', mess_list_api, name='mess_list_api'),
    
    # Complaint & Notice APIs
    path('complaint/', complaint_api, name='complaint_api'),
    path('notices/', notice_api, name='notice_api'),
    
    # Feedback & Suggestion APIs
    path('feedback/', feedback_api, name='feedback_api'),
    path('weekly-suggestion/', weekly_suggestion_api, name='weekly_suggestion_api'),
    path('mess-selection/', mess_selection_api, name='mess_selection_api'),
    
    # User API
    path('user/profile/', user_profile_api, name='user_profile_api'),
    path('auth/users/', users_list_api, name='users_list_api'),
]