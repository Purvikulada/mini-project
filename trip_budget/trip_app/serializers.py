# trip_app/serializers.py
from rest_framework import serializers
from .models import Trip # Import the Trip model from your local models.py

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