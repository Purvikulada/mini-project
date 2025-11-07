# trip_app/serializers.py
from rest_framework import serializers
from .models import Trip 
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model() # Get the currently active user model

class TripSerializer(serializers.ModelSerializer):
    """
    Serializer to handle JSON conversion for the Trip model.
    It includes both user input fields and suggested output fields.
    """
    class Meta:
        model = Trip
        # Fields the API will read/write
        fields = [
            'id', 
            'location', 
            'duration_days', 
            'user_budget',          # User Input
            'suggested_total_cost', # Suggested Output
            'suggested_plan'        # Suggested Output
        ]
        # Fields that should only be written by the backend, not by the user in the POST request
        read_only_fields = ['suggested_total_cost', 'suggested_plan']


# --- New Authentication Serializers ---

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for User Registration.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for User Login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            # Authenticate the user against Django's backend
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            
            if not user:
                raise AuthenticationFailed('Invalid credentials. Check username and password.')
            
            # Store the user object in the validated data for the view to use
            data['user'] = user
            return data
        
        raise serializers.ValidationError('Must include "username" and "password".')