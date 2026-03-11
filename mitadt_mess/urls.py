"""
URL configuration for mitadt_mess project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from testapp import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect root to API documentation
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='index'),
    
    path('admin/', admin.site.urls),
    path('signup/', views.sign_up_views, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #  Student Raj Mess Menu Page
    path('raj_mess/', views.raj_mess_view, name='raj_mess'),

#     Raj Mess Admin Page
    path('admin_raj_mess/', views.add_dish, {'mess_id': 1}, name='admin_raj_mess'),

    #  Add/Delete handlers
    path('add_dish/<int:mess_id>/', views.add_dish, name='add_dish'),
    path('delete-dish/<int:id>/', views.delete_dish, name='delete_dish'),

    path('design_mess/',views.design_mess_view,name='design_mess'),
    path('admin_design_mess/', views.design_mess_admin_view, name='admin_design_mess'),
    path("rate_design_dish/", views.rate_design_dish, name="rate_design_dish"),


    path('manet_mess/', views.manet_mess_view, name='manet_mess'),
    path('admin_manet_mess/', views.manet_add_dish, name='admin_manet_mess'),
    path("rate-manet/", views.rate_manet_dish, name="rate_manet_dish"),

    path("rate-dish/", views.rate_dish, name="rate_dish"),

    path("payment_selection/", views.mess_payment_select, name="payment_selection"),

    path("feedback/", views.feedback_form, name="feedback"),
    path('thank-you/', views.thank_you, name='thank_you'),

    path('weekly_suggestion/', views.weekly_suggestion, name='weekly_suggestion'),
    path('suggestion_success/', views.suggestion_success, name='suggestion_success'),
    
    path('notices/', views.all_notices, name='all_notices'), 
    path('delete-notice/<int:id>/<int:mess_id>/', views.delete_notice, name='delete_notice'), # <-- View All should point here
    path('complaint/', views.complaint_view, name='complaint'),
    path("complaint/success/", views.complaint_success, name="complaint_success"),  # ✅ new
    
    path('api/', include('testapp.api_urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]



from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
