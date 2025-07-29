from rest_framework import serializers
from .models import User, Journey

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'password', 'phone', 'email', 'upi', 'licence', 'rating']

class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = '__all__'
