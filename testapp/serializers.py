from rest_framework import serializers
from .models import Dish, DishRating, Notice, Complaint

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'


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