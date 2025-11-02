# trip_app/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Trip
from .serializers import TripSerializer
from .services import generate_trip_suggestion # Import your service function

class TripSuggestionViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        location = serializer.validated_data.get('location')
        duration_days = serializer.validated_data.get('duration_days')
        user_budget = serializer.validated_data.get('user_budget')

        # CALL THE CORE SUGGESTION SERVICE
        suggested_plan, final_cost, fixed_cost = generate_trip_suggestion(location, duration_days, user_budget)

        if suggested_plan is None:
            # Handle the case where the budget is too low
            return Response(
                {"error": "Budget Constraint Failed", 
                 "message": f"Your budget is too low for fixed costs (estimated ${fixed_cost:.2f}) for this trip. Please increase your budget or decrease the duration/cost expectation.",
                 "estimated_fixed_cost": fixed_cost},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the serializer data with the generated plan and cost
        serializer.validated_data['suggested_plan'] = suggested_plan
        serializer.validated_data['suggested_total_cost'] = final_cost
        
        self.perform_create(serializer)

        # Return the complete result
        return Response(serializer.data, status=status.HTTP_201_CREATED)