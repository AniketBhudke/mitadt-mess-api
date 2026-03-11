from rest_framework import serializers
from .models import (
    Dish, DishRating, Notice, Complaint, Mess,
    manet_menu, ManetRating, design_menu, DesignRating,
    Weekly_suggestion, MessSelection, MessFeedback
)
from django.contrib.auth.models import User

class DishSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Dish
        fields = '__all__'
    
    def get_average_rating(self, obj):
        return obj.average_rating()


class DishRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishRating
        fields = '__all__'


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'


class MessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mess
        fields = '__all__'


class ManetMenuSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = manet_menu
        fields = '__all__'
    
    def get_average_rating(self, obj):
        return obj.average_rating()


class ManetRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManetRating
        fields = '__all__'


class DesignMenuSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = design_menu
        fields = '__all__'
    
    def get_average_rating(self, obj):
        return obj.average_rating()


class DesignRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignRating
        fields = '__all__'


class WeeklySuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weekly_suggestion
        fields = '__all__'


class MessSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessSelection
        fields = '__all__'


class MessFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessFeedback
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']