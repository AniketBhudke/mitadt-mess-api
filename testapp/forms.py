from django import forms
from .models import Dish, design_menu, manet_menu
from django import forms
from .models import Dish

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['name', 'name', 'image', 'day', 'meal']

from django import forms
from .models import MessSelection

class MessForm(forms.ModelForm):
    class Meta:
        model = MessSelection
        fields = ['mess', 'meal']



class ManetForm(forms.ModelForm):
    class Meta:
        model = manet_menu
        fields = ['name', 'image', 'day', 'meal']  

class DesignForm(forms.ModelForm):
    class Meta:
        model = design_menu
        fields = ['name', 'image', 'day', 'meal']  



from django import forms
from django import forms
from .models import Weekly_suggestion

# --- Unique Dish Lists ---

UNIQUE_BREAKFAST = [
    "Kanda Poha", "Fruit", "Wada Sample", "Sprouts", "Veg Upma",
    "Aloo Sabudana Khichadi", "Misal Pav", "Bread Besan Toast", "Mix Veg Paratha"
]

UNIQUE_LUNCH = [
    "Bean Salad", "Moong Hara Payaz", "Rajma Masala", "Peas Pulao",
    "Chapati", "Curd", "Roasted Papad", "Beetroot Pachadi", "Gobi Mutter",
    "Paneer Makhaniwala", "Bhurani Raita", "Rasgulla", "Green Salad",
    "Chow Chow Dal", "Chawli Usal", "Dal Makhani", "Mattha", "Hot & Sour Soup",
    "Dry Manchurian", "Veg Hakka Noodles", "Coriander Rice", "Bundi Raita",
    "Chutneys", "Slice Cake", "Lacha Payaz", "Kache Kele Ki Sabji",
    "Chole Amritsari", "Kulcha", "Kokam Sarbat", "Toss Salad", "Corn Palak Dry",
    "Veg Handi", "Dum Aloo Kashmiri", "Rice", "Masala Bhat", "Kanda Bhaji with Mirchi",
    "Aloo Chat", "Cabbage Foghat", "Steamed Rice", "Masala Puri", "Cucumber Raita", "Shrikhand"
]

UNIQUE_DINNER = [
    "Green Salad", "Dudhi Dry", "Mix Veg Curry", "Plain Varan", "Jeera Rice",
    "Chapati", "Curd", "Sheera", "Black Chana Usal", "Steam Rice", "Papad",
    "Chilli Paneer", "Toss Salad", "Kadhi Pakoda", "Dal Khichadi", "Tawa Paratha",
    "Veg Raita", "Balushahi", "Cucumber Salad", "Mutter Paneer", "Veg Dum Biryani",
    "Masala Bhat", "Bundi Raita", "Sev Kheer", "Jeera Aloo", "Gatta Curry", "Jalebi",
    "Veg Hariyali", "Chana Hara Payaz", "Butter Pav", "Kesar Peda", "Pav Bhaji",
    "Hyderabadi Biryani", "Dal/Rice", "Kala Jamun"
]


# --- Helper to convert list to Django choices ---
def make_choices(lst):
    return [(dish, dish) for dish in lst]

from django import forms
from .models import Weekly_suggestion

# ✅ You already have these lists — just keep them imported
# UNIQUE_BREAKFAST, UNIQUE_LUNCH, UNIQUE_DINNER must exist

def make_choices(items):
    return [(i, i) for i in items]

from django import forms
from .models import Weekly_suggestion



class WeeklysuggestionForm(forms.ModelForm):
    class Meta:
        model = Weekly_suggestion
        fields = "__all__"

    # ✅ Mess Dropdown (Required)
    mess_name = forms.ChoiceField(
        choices=[
            ("", "Select Mess"),
            ("MANET Mess", "MANET Mess"),
            ("Design Mess", "Design Mess"),
            ("Sofa Mess", "Sofa Mess"),
            ("Raj Mess", "Raj Mess"),
            ("Sangeet Mess", "Sangeet Mess"),
        ],
        label="Select Your Mess",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define dish choices for each meal type
        breakfast_choices = [
            ('', 'Select Dish'),
            ("Kanda Poha", "Kanda Poha"),
            ("Fruit", "Fruit"), 
            ("Wada Sample", "Wada Sample"),
            ("Sprouts", "Sprouts"),
            ("Veg Upma", "Veg Upma"),
            ("Aloo Sabudana Khichadi", "Aloo Sabudana Khichadi"),
            ("Misal Pav", "Misal Pav"),
            ("Bread Besan Toast", "Bread Besan Toast"),
            ("Mix Veg Paratha", "Mix Veg Paratha"),
            ("Tea/Coffee", "Tea/Coffee"),
            ("Aloo Paratha", "Aloo Paratha"),
            ("Poha", "Poha"),
            ("Upma", "Upma"),
        ]

        lunch_choices = [
            ('', 'Select Dish'),
            ("Bean Salad", "Bean Salad"),
            ("Rajma Masala", "Rajma Masala"),
            ("Peas Pulao", "Peas Pulao"),
            ("Chapati", "Chapati"),
            ("Curd", "Curd"),
            ("Roasted Papad", "Roasted Papad"),
            ("Beetroot Pachadi", "Beetroot Pachadi"),
            ("Paneer Makhaniwala", "Paneer Makhaniwala"),
            ("Bhurani Raita", "Bhurani Raita"),
            ("Green Salad", "Green Salad"),
            ("Dal Makhani", "Dal Makhani"),
            ("Hot & Sour Soup", "Hot & Sour Soup"),
            ("Veg Hakka Noodles", "Veg Hakka Noodles"),
            ("Dal Rice", "Dal Rice"),
            ("Vegetable Curry", "Vegetable Curry"),
            ("Rajma Rice", "Rajma Rice"),
            ("Mixed Vegetables", "Mixed Vegetables"),
            ("Chole Rice", "Chole Rice"),
            ("Aloo Gobi", "Aloo Gobi"),
        ]

        dinner_choices = [
            ('', 'Select Dish'),
            ("Green Salad", "Green Salad"),
            ("Mix Veg Curry", "Mix Veg Curry"),
            ("Plain Varan", "Plain Varan"),
            ("Jeera Rice", "Jeera Rice"),
            ("Chapati", "Chapati"),
            ("Curd", "Curd"),
            ("Black Chana Usal", "Black Chana Usal"),
            ("Steam Rice", "Steam Rice"),
            ("Chilli Paneer", "Chilli Paneer"),
            ("Kadhi Pakoda", "Kadhi Pakoda"),
            ("Dal Khichadi", "Dal Khichadi"),
            ("Mutter Paneer", "Mutter Paneer"),
            ("Veg Dum Biryani", "Veg Dum Biryani"),
            ("Jeera Aloo", "Jeera Aloo"),
            ("Pav Bhaji", "Pav Bhaji"),
            ("Paneer Curry", "Paneer Curry"),
            ("Dal Tadka", "Dal Tadka"),
            ("Roti", "Roti"),
            ("Palak Paneer", "Palak Paneer"),
        ]

        # Apply choices to all meal fields
        meal_fields = [
            'monday_breakfast', 'tuesday_breakfast', 'wednesday_breakfast', 
            'thursday_breakfast', 'friday_breakfast', 'saturday_breakfast', 'sunday_breakfast',
            'monday_lunch', 'tuesday_lunch', 'wednesday_lunch',
            'thursday_lunch', 'friday_lunch', 'saturday_lunch', 'sunday_lunch',
            'monday_dinner', 'tuesday_dinner', 'wednesday_dinner',
            'thursday_dinner', 'friday_dinner', 'saturday_dinner', 'sunday_dinner',
        ]

        for field_name in meal_fields:
            if field_name in self.fields:
                if 'breakfast' in field_name:
                    self.fields[field_name].choices = breakfast_choices
                elif 'lunch' in field_name:
                    self.fields[field_name].choices = lunch_choices
                elif 'dinner' in field_name:
                    self.fields[field_name].choices = dinner_choices
                
                self.fields[field_name].required = True
                self.fields[field_name].widget.attrs.update({
                    "required": "required",
                    "class": "form-select"
                })

        # ✅ Student Fields Mandatory with placeholders
        if 'student_name' in self.fields:
            self.fields['student_name'].required = True
            self.fields['student_name'].widget.attrs.update({
                "placeholder": "Enter Student Name",
                "class": "form-control",
                "required": "required"
            })

        if 'email' in self.fields:
            self.fields['email'].required = True
            self.fields['email'].widget.attrs.update({
                "placeholder": "Enter Email",
                "class": "form-control",
                "required": "required"
            })

        # ✅ Mess dropdown styling
        self.fields["mess_name"].widget.attrs.update({
            "class": "form-select",
            "required": "required"
        })

from django import forms
from .models import MessFeedback

class MessFeedbackForm(forms.ModelForm):
    class Meta:
        model = MessFeedback
        fields = "__all__"
        widgets = {
            "visit_date": forms.DateInput(attrs={"type": "date"}),
        }

from django import forms
from .models import Complaint

# testapp/forms.py
# testapp/forms.py
from django import forms
from .models import Complaint

from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['student_name', 'email', 'mess_name', 'message']  # added mess_name field

        # Optional: make the form look cleaner
        widgets = {
            'student_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
            }),
            'mess_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter mess name (e.g., Raj Mess)',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your complaint or suggestion here...',
                'rows': 5,
            }),
        }

        labels = {
            'student_name': 'Student Name',
            'email': 'Email',
            'mess_name': 'Mess Name',
            'message': 'Message',
        }
