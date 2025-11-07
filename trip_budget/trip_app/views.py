# trip_app/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login, logout, get_user_model

from .models import Trip
from .serializers import TripSerializer, UserRegisterSerializer, UserLoginSerializer
from .services import generate_trip_suggestion # Import your service function

# --- Authentication Views ---

class UserRegisterView(APIView):
    """
    API view for user registration. Uses AllowAny permission.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # Optionally, log the user in immediately after registration
            login(request, user) 
            return Response(
                {"username": user.username, "email": user.email, "message": "Registration successful and user logged in."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """
    API view for user login. Uses AllowAny permission.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Pass the request context to the serializer for authentication function
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user) # Use Django's built-in login mechanism
            
            return Response(
                {"username": user.username, "message": "Login successful."},
                status=status.HTTP_200_OK
            )
        # AuthenticationFailed is handled by raise_exception=True in the serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    """
    API view for user logout. Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserDashboardView(APIView):
    """
    A simple view for the user's dashboard. Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Fetch the user's existing trips
        user_trips = Trip.objects.filter(user=user) # Assuming you will link trips to users later
        trip_serializer = TripSerializer(user_trips, many=True)
        
        return Response({
            "message": f"Welcome back to your dashboard, {user.username}!",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            
            "trips_planned": trip_serializer.data,
            "note": "This is a protected dashboard endpoint."
        }, status=status.HTTP_200_OK)


# --- Trip Suggestion View (Existing) ---

class TripSuggestionViewSet(viewsets.ModelViewSet):
    # Ensure only authenticated users can create trips
    permission_classes = [IsAuthenticated] 
    
    # We will adjust this queryset to only show trips belonging to the authenticated user later
    queryset = Trip.objects.all() 
    serializer_class = TripSerializer
    
    # Override perform_create to link the trip to the currently logged-in user
    def perform_create(self, serializer):
        # Assuming we add a 'user' ForeignKey field to the Trip model
        serializer.save(user=self.request.user) 

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
        
        self.perform_create(serializer) # This now links the trip to the user

        # Return the complete result
        return Response(serializer.data, status=status.HTTP_201_CREATED)