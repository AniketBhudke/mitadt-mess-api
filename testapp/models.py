from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# Shared choices
MEALS = [
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
]

DAYS = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]


class Mess(models.Model):
    name = models.CharField(max_length=50)   # RAJ, SOFA, MIT Boys, MIT Girls etc.

    def __str__(self):
        return self.name


class Dish(models.Model):
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to="dish_images/", blank=True, null=True)
    day = models.CharField(max_length=50, choices=DAYS, blank=True)
    meal = models.CharField(max_length=50, choices=MEALS, blank=True)

    def average_rating(self):
        avg = self.ratings.aggregate(avg=Avg('rating'))["avg"]
        return round(avg, 1) if avg else 0

    def user_rating(self, user):
        if user.is_authenticated:
            r = self.ratings.filter(user=user).first()
            return r.rating if r else 0
        return 0

    def __str__(self):
        return self.name


class DishRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, related_name='ratings', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'dish')

    def __str__(self):
        return f"{self.user.username} → {self.dish.name} ({self.rating})"


# MANET menu model (keeps original lowercase name)
class manet_menu(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='testapp/images', blank=True, null=True)
    meal = models.CharField(max_length=50, choices=MEALS)
    day = models.CharField(max_length=10, choices=DAYS)

    def average_rating(self):
        avg = self.ratings.aggregate(avg=Avg('rating'))["avg"]
        return round(avg, 1) if avg else 0

    def user_rating(self, user):
        if user.is_authenticated:
            r = self.ratings.filter(user=user).first()
            return r.rating if r else 0
        return 0

    def __str__(self):
        return f"{self.name} ({self.day} - {self.meal})"


class ManetRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey(manet_menu, related_name='ratings', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=0)  # 1..5

    class Meta:
        unique_together = ('user', 'dish')

    def __str__(self):
        return f"{self.user.username} rated {self.dish.name} → {self.rating}"


# design_menu, sangeet_menu, sofa_menu (keeps original names)
class design_menu(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='testapp/images/design', blank=True, null=True)
    meal = models.CharField(max_length=40, choices=MEALS)
    day = models.CharField(max_length=40, choices=DAYS)

    def __str__(self):
        return f"{self.name} ({self.day} - {self.meal})"




# Ratings for design/sofa/sangeet (keeps original class names)
class DesignRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    design_menu = models.ForeignKey(design_menu, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'design_menu')

    def __str__(self):
        return f"{self.user.username} - {self.design_menu.name} ({self.rating})"

# Weekly suggestion (keeps original class name)
class Weekly_suggestion(models.Model):
    # Mess choices (shared across all messes)
    MESS_CHOICES = [
        ('MANET Mess', 'MANET Mess'),
        ('Design Mess', 'Design Mess'),
        ('Sofa Mess', 'Sofa Mess'),
        ('Raj Mess', 'Raj Mess'),
        ('Sangeet Mess', 'Sangeet Mess'),
    ]

    mess_name = models.CharField(max_length=100, choices=MESS_CHOICES)
    student_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Monday
    monday_breakfast = models.CharField(max_length=100)
    monday_lunch = models.CharField(max_length=100)
    monday_dinner = models.CharField(max_length=100)

    # Tuesday
    tuesday_breakfast = models.CharField(max_length=100)
    tuesday_lunch = models.CharField(max_length=100)
    tuesday_dinner = models.CharField(max_length=100)

    # Wednesday
    wednesday_breakfast = models.CharField(max_length=100)
    wednesday_lunch = models.CharField(max_length=100)
    wednesday_dinner = models.CharField(max_length=100)

    # Thursday
    thursday_breakfast = models.CharField(max_length=100)
    thursday_lunch = models.CharField(max_length=100)
    thursday_dinner = models.CharField(max_length=100)

    # Friday
    friday_breakfast = models.CharField(max_length=100)
    friday_lunch = models.CharField(max_length=100)
    friday_dinner = models.CharField(max_length=100)

    # Saturday
    saturday_breakfast = models.CharField(max_length=100)
    saturday_lunch = models.CharField(max_length=100)
    saturday_dinner = models.CharField(max_length=100)

    # Sunday
    sunday_breakfast = models.CharField(max_length=100)
    sunday_lunch = models.CharField(max_length=100)
    sunday_dinner = models.CharField(max_length=100)

    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Add suggestion period tracking (similar to feedback system)
    suggestion_period_start = models.DateField(null=True, blank=True)
    suggestion_period_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.mess_name} - Weekly Feedback"

    class Meta:
        # Prevent duplicate suggestions from same email in same period
        unique_together = ['email', 'suggestion_period_start', 'suggestion_period_end']


class MessSelection(models.Model):
    MESS_CHOICES = [
        ('MANET Mess', 'MANET Mess'),
        ('Sofa Mess', 'Sofa Mess'),
        ('Raj Mess', 'Raj Mess'),
        ('Sangeet Mess', 'Sangeet Mess'),
        ('Design Mess', 'Design Mess'),
    ]

    MEAL_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mess = models.CharField(max_length=50, choices=MESS_CHOICES)
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES)
    date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} → {self.mess} → {self.meal}"


class MessFeedback(models.Model):
    YEAR_CHOICES = [
        ("First Year", "First Year"),
        ("Second Year", "Second Year"),
        ("Third Year", "Third Year"),
        ("Fourth Year", "Fourth Year"),
        ("DOME VISITOR", "DOME VISITOR"),
        ("Dean/Director/Faculty/Staff", "Dean/Director/Faculty/Staff"),
        ("Other", "Other"),
    ]

    MESS_CHOICES = [
        ("Raj Mess", "Raj Mess"),
        ("MANET Mess", "MANET Mess"),
        ("Sangeet Mess", "Sangeet Mess"),
        ("Design Mess", "Design Mess"),
        ("Sofa Mess", "Sofa Mess"),
    ]

    email = models.EmailField()
    full_name = models.CharField(max_length=100)
    department = models.CharField(max_length=200)
    year = models.CharField(max_length=50, choices=YEAR_CHOICES)
    mess_name = models.CharField(max_length=50, choices=MESS_CHOICES)

    alumni = models.CharField(max_length=5)
    dome_visitor = models.CharField(max_length=5)

    contact = models.CharField(max_length=15)
    visit_date = models.DateField()

    food_rating = models.IntegerField()
    food_comment = models.TextField()

    service_rating = models.IntegerField()
    service_comment = models.TextField()

    cleanliness_rating = models.IntegerField()
    cleanliness_comment = models.TextField()

    overall_rating = models.IntegerField()
    suggestion = models.TextField()

    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Add feedback period tracking
    feedback_period_start = models.DateField(null=True, blank=True)
    feedback_period_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        # Prevent duplicate feedback from same email in same period
        unique_together = ['email', 'feedback_period_start', 'feedback_period_end']


class SuggestionPeriod(models.Model):
    """Model to define weekly suggestion collection periods"""
    name = models.CharField(max_length=100, help_text="e.g., 'Week 1 - March 2026'")
    start_date = models.DateField()
    end_date = models.DateField()
    submission_deadline = models.DateField(help_text="Last date to submit suggestions")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"
    
    @classmethod
    def get_current_period(cls):
        """Get the currently active suggestion period"""
        from django.utils import timezone
        today = timezone.now().date()
        return cls.objects.filter(
            is_active=True,
            start_date__lte=today,
            submission_deadline__gte=today
        ).first()
    
    def is_submission_allowed(self):
        """Check if submissions are still allowed for this period"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.is_active and today <= self.submission_deadline
    
    def clean(self):
        """Validate model data"""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")
        if self.submission_deadline and self.end_date and self.submission_deadline > self.end_date:
            raise ValidationError("Submission deadline cannot be after end date.")
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Suggestion Period"
        verbose_name_plural = "Suggestion Periods"


class FeedbackPeriod(models.Model):
    """Model to define feedback collection periods"""
    name = models.CharField(max_length=100, help_text="e.g., 'Week 1 - March 2026'")
    start_date = models.DateField()
    end_date = models.DateField()
    submission_deadline = models.DateField(help_text="Last date to submit feedback")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"
    
    @classmethod
    def get_current_period(cls):
        """Get the currently active feedback period"""
        from django.utils import timezone
        today = timezone.now().date()
        return cls.objects.filter(
            is_active=True,
            start_date__lte=today,
            submission_deadline__gte=today
        ).first()
    
    def is_submission_allowed(self):
        """Check if submissions are still allowed for this period"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.is_active and today <= self.submission_deadline
    
    def clean(self):
        """Validate model data"""
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")
        if self.submission_deadline and self.end_date and self.submission_deadline > self.end_date:
            raise ValidationError("Submission deadline cannot be after end date.")
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Feedback Period"
        verbose_name_plural = "Feedback Periods"


class Notice(models.Model):
    title = models.CharField(max_length=220)
    body = models.TextField()
    attachment = models.FileField(upload_to="notices/", null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Complaint(models.Model):
    student_name = models.CharField(max_length=100)
    email = models.EmailField()
    mess_name = models.CharField(max_length=100, blank=True, null=True)   # new field
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # optional, for date display

    def __str__(self):
        return f"{self.student_name} - {self.mess_name or 'N/A'}"
