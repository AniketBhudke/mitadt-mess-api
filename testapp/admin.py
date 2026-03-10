from django.contrib import admin
from .models import DesignRating, Dish, DishRating, ManetRating, Weekly_suggestion, design_menu, manet_menu,MessSelection

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'meal')

@admin.register(DishRating)
class DishRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish', 'rating')
    list_filter = ('dish', 'rating')
    search_fields = ('user__username', 'dish__name')

@admin.register(manet_menu)
class manet_menuAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'meal')

from django.contrib import admin
from .models import ManetRating

@admin.register(ManetRating)
class ManetRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "dish", "rating")

@admin.register(DesignRating)
class DesignRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'design_menu', 'rating', 'created_at')


@admin.register(design_menu)
class design_menuAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'meal')


@admin.register(MessSelection)
class MessSelection(admin.ModelAdmin):
    list_display = ['mess', 'meal']

from django.contrib import admin

@admin.register(Weekly_suggestion)
class WeeklyFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'mess_name',
        'student_name',
        'email',
        'monday_breakfast', 'monday_lunch', 'monday_dinner',
        'tuesday_breakfast', 'tuesday_lunch', 'tuesday_dinner',
        'wednesday_breakfast', 'wednesday_lunch', 'wednesday_dinner',
        'thursday_breakfast', 'thursday_lunch', 'thursday_dinner',
        'friday_breakfast', 'friday_lunch', 'friday_dinner',
        'saturday_breakfast', 'saturday_lunch', 'saturday_dinner',
        'sunday_breakfast', 'sunday_lunch', 'sunday_dinner',
        'submitted_at',
    )
    list_filter = ('mess_name', 'submitted_at')
    search_fields = ('mess_name', 'student_name', 'email')
    list_per_page = 20

from django.contrib import admin
from .models import MessFeedback

class MessFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "email", "department", "year", "mess_name", 
        "visit_date", "overall_rating", "submitted_at"
    )

    search_fields = ("full_name", "email", "department", "mess_name")

    list_filter = ("year", "mess_name", "visit_date", "overall_rating")

    ordering = ("-submitted_at",)  # latest first

    readonly_fields = ("submitted_at",)  # cannot edit timestamp

admin.site.register(MessFeedback, MessFeedbackAdmin)

from django.contrib import admin
from .models import Notice, Complaint

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    ordering = ('-created_at',)

from django.contrib import admin
from .models import Complaint, Notice

# Prevent duplicate registration warning for Notice
try:
    admin.site.unregister(Notice)
except admin.sites.NotRegistered:
    pass


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    # Display relevant fields including new mess_name and created_at
    list_display = ('id', 'mess_name', 'student_name', 'email', 'message_short', 'created_at')

    # Fields you can search for
    search_fields = ('student_name', 'email', 'mess_name', 'message')

    # Sort by newest first
    ordering = ('-created_at',)

    # Show 25 per page
    list_per_page = 25

    # Custom short version of message (so admin list isn't huge)
    def message_short(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    message_short.short_description = 'Message'


# Re-register Notice safely
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_published', 'created_at' if hasattr(Notice, 'created_at') else 'id')
    search_fields = ('title',)


from django.contrib import admin
from .models import Notice

# optional safe unregister
try:
    admin.site.unregister(Notice)
except Exception:
    pass

class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "is_published")
    search_fields = ("title", "body")

admin.site.register(Notice, NoticeAdmin)
