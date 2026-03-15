from django.contrib import admin
from .models import (
    DesignRating, Dish, DishRating, ManetRating, Weekly_suggestion, 
    design_menu, manet_menu, MessSelection, MessFeedback, FeedbackPeriod,
    SuggestionPeriod, Notice, Complaint
)

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'meal')

@admin.register(DishRating)
class DishRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'dish', 'rating')
    list_filter = ('dish', 'rating')
    search_fields = ('user__username', 'dish__name')

@admin.register(manet_menu)
class ManetMenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'meal')

@admin.register(ManetRating)
class ManetRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "dish", "rating")

@admin.register(DesignRating)
class DesignRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'design_menu', 'rating', 'created_at')

@admin.register(design_menu)
class DesignMenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'day', 'meal')

@admin.register(MessSelection)
class MessSelectionAdmin(admin.ModelAdmin):
    list_display = ['mess', 'meal']

@admin.register(Weekly_suggestion)
class WeeklySuggestionAdmin(admin.ModelAdmin):
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
        'submitted_at', 'suggestion_period_start', 'suggestion_period_end'
    )
    list_filter = ('mess_name', 'submitted_at', 'suggestion_period_start')
    search_fields = ('mess_name', 'student_name', 'email')
    list_per_page = 20
    readonly_fields = ('submitted_at', 'suggestion_period_start', 'suggestion_period_end')

@admin.register(MessFeedback)
class MessFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "full_name", "email", "department", "year", "mess_name", 
        "visit_date", "overall_rating", "submitted_at", "feedback_period_start", "feedback_period_end"
    )
    search_fields = ("full_name", "email", "department", "mess_name")
    list_filter = ("year", "mess_name", "visit_date", "overall_rating", "feedback_period_start")
    ordering = ("-submitted_at",)
    readonly_fields = ("submitted_at", "feedback_period_start", "feedback_period_end")

@admin.register(SuggestionPeriod)
class SuggestionPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "name", "start_date", "end_date", "submission_deadline", 
        "is_active", "created_at"
    )
    search_fields = ("name",)
    list_filter = ("is_active", "start_date", "end_date", "submission_deadline")
    ordering = ("-start_date",)
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("Period Information", {
            "fields": ("name", "start_date", "end_date", "submission_deadline")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Metadata", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-start_date')

@admin.register(FeedbackPeriod)
class FeedbackPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "name", "start_date", "end_date", "submission_deadline", 
        "is_active", "created_at"
    )
    search_fields = ("name",)
    list_filter = ("is_active", "start_date", "end_date", "submission_deadline")
    ordering = ("-start_date",)
    readonly_fields = ("created_at",)
    
    fieldsets = (
        ("Period Information", {
            "fields": ("name", "start_date", "end_date", "submission_deadline")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Metadata", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-start_date')

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    search_fields = ('title', 'body')
    list_filter = ('is_published', 'created_at')
    ordering = ('-created_at',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'mess_name', 'student_name', 'email', 'message_short', 'created_at')
    search_fields = ('student_name', 'email', 'mess_name', 'message')
    list_filter = ('mess_name', 'created_at')
    ordering = ('-created_at',)
    list_per_page = 25

    def message_short(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    message_short.short_description = 'Message'
