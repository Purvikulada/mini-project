from django.db import models
from django.conf import settings # Import settings

class Trip(models.Model):
    # Link the trip to the user who created it
    # Use settings.AUTH_USER_MODEL for the recommended way to reference the User model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trips') 
    
    # User Input Fields
    location = models.CharField(max_length=255)
    duration_days = models.IntegerField()
    user_budget = models.DecimalField(max_digits=10, decimal_places=2) # The crucial new input

    # Suggested Output Fields
    suggested_total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    suggested_plan = models.JSONField(null=True, blank=True) # Stores the daily itinerary
    
    # Optional: For tracking against the suggestion
    actual_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Plan for {self.location} | User: {self.user.username} | Budget: ${self.user_budget}"