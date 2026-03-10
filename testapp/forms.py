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

    # ✅ Weekly Fields
    monday_breakfast = forms.ChoiceField(choices=make_choices([]))
    monday_lunch = forms.ChoiceField(choices=make_choices([]))
    monday_dinner = forms.ChoiceField(choices=make_choices([]))

    tuesday_breakfast = forms.ChoiceField(choices=make_choices([]))
    tuesday_lunch = forms.ChoiceField(choices=make_choices([]))
    tuesday_dinner = forms.ChoiceField(choices=make_choices([]))

    wednesday_breakfast = forms.ChoiceField(choices=make_choices([]))
    wednesday_lunch = forms.ChoiceField(choices=make_choices([]))
    wednesday_dinner = forms.ChoiceField(choices=make_choices([]))

    thursday_breakfast = forms.ChoiceField(choices=make_choices([]))
    thursday_lunch = forms.ChoiceField(choices=make_choices([]))
    thursday_dinner = forms.ChoiceField(choices=make_choices([]))

    friday_breakfast = forms.ChoiceField(choices=make_choices([]))
    friday_lunch = forms.ChoiceField(choices=make_choices([]))
    friday_dinner = forms.ChoiceField(choices=make_choices([]))

    saturday_breakfast = forms.ChoiceField(choices=make_choices([]))
    saturday_lunch = forms.ChoiceField(choices=make_choices([]))
    saturday_dinner = forms.ChoiceField(choices=make_choices([]))

    sunday_breakfast = forms.ChoiceField(choices=make_choices([]))
    sunday_lunch = forms.ChoiceField(choices=make_choices([]))
    sunday_dinner = forms.ChoiceField(choices=make_choices([]))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        meal_fields = [
            'monday_breakfast', 'monday_lunch', 'monday_dinner',
            'tuesday_breakfast', 'tuesday_lunch', 'tuesday_dinner',
            'wednesday_breakfast', 'wednesday_lunch', 'wednesday_dinner',
            'thursday_breakfast', 'thursday_lunch', 'thursday_dinner',
            'friday_breakfast', 'friday_lunch', 'friday_dinner',
            'saturday_breakfast', 'saturday_lunch', 'saturday_dinner',
            'sunday_breakfast', 'sunday_lunch', 'sunday_dinner',
        ]

        # ✅ Map dishes by type
        meal_map = {
            'breakfast': UNIQUE_BREAKFAST,
            'lunch': UNIQUE_LUNCH,
            'dinner': UNIQUE_DINNER,
        }

        # ✅ Apply common settings to fields
        for field in meal_fields:
            meal_type = field.split('_')[1]
            dish_list = meal_map[meal_type]

            self.fields[field].choices = [('', 'Select Dish')] + [(d, d) for d in dish_list]
            self.fields[field].required = True
            self.fields[field].widget.attrs.update({
                "required": "required",
                "class": "form-select"
            })

        # ✅ Student Fields Mandatory with placeholders
        for f in ["student_name", "email"]:
            self.fields[f].required = True
            self.fields[f].widget.attrs.update({
                "placeholder": f"Enter {f.replace('_',' ').title()}",
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
