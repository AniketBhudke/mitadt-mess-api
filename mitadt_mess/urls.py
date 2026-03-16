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
from django.shortcuts import render
from testapp import views
from testapp.api_home import api_home
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Database initialization (for debugging)
    path('init-db/', views.initialize_database, name='init_db'),
    path('fix-periods/', views.fix_periods, name='fix_periods'),
    path('health/', views.health_check, name='health_check'),
    path('check-users/', views.check_users_view, name='check_users'),
    path('populate-data/', views.populate_sample_data, name='populate_data'),
    path('fix-sessions/', views.fix_sessions, name='fix_sessions'),
    path('test-day-fields/', views.test_day_fields_debug, name='test_day_fields'),
    
    # Frontend URLs
    path('', views.index_view, name='index'),
    path('responsive-test/', lambda request: render(request, 'testapp/responsive_test.html'), name='responsive_test'),
    path('signup/', views.simple_signup_view, name='signup'),  # Use working signup page
    path('old-signup/', views.sign_up_views, name='old_signup'),  # Keep old one as backup
    path('test-signup/', lambda request: render(request, 'testapp/signup_test.html'), name='test_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # Mess Pages
    path('raj_mess/', views.raj_mess_view, name='raj_mess'),
    path('design_mess/', views.design_mess_view, name='design_mess'),
    path('manet_mess/', views.manet_mess_view, name='manet_mess'),
    
    # Admin Pages
    path('admin/', admin.site.urls),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin_raj_mess/', views.add_dish, {'mess_id': 1}, name='admin_raj_mess'),
    path('admin_design_mess/', views.design_mess_admin_view, name='admin_design_mess'),
    path('admin_manet_mess/', views.manet_add_dish, name='admin_manet_mess'),
    
    # Actions
    path('add_dish/<int:mess_id>/', views.add_dish, name='add_dish'),
    path('delete-dish/<int:id>/', views.delete_dish, name='delete_dish'),
    path("rate_design_dish/", views.rate_design_dish, name="rate_design_dish"),
    path("rate-manet/", views.rate_manet_dish, name="rate_manet_dish"),
    path("rate-dish/", views.rate_dish, name="rate_dish"),
    
    # Other Pages
    path("payment_selection/", views.mess_payment_select, name="payment_selection"),
    path("feedback/", views.feedback_form, name="feedback"),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('weekly_suggestion/', views.weekly_suggestion, name='weekly_suggestion'),
    path('suggestion_success/', views.suggestion_success, name='suggestion_success'),
    path('notices/', views.all_notices, name='all_notices'),
    path('delete-notice/<int:id>/<int:mess_id>/', views.delete_notice, name='delete_notice'),
    path('complaint/', views.complaint_view, name='complaint'),
    path("complaint/success/", views.complaint_success, name="complaint_success"),
    
    # API URLs
    path('api/', include('testapp.api_urls')),
    path('api/home/', api_home, name='api_home'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]



from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
