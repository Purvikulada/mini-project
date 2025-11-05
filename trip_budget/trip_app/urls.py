# trip_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TripSuggestionViewSet, 
    UserRegisterView, 
    UserLoginView, 
    UserLogoutView, 
    UserDashboardView
)

# Router for the TripSuggestion API endpoint
router = DefaultRouter()
router.register(r'suggest', TripSuggestionViewSet, basename='trip-suggestion')

urlpatterns = [
    # API endpoints for Trip Suggestions (CRUD)
    path('api/', include(router.urls)),
    
    # API endpoints for Authentication
    path('api/register/', UserRegisterView.as_view(), name='register'),
    path('api/login/', UserLoginView.as_view(), name='login'),
    path('api/logout/', UserLogoutView.as_view(), name='logout'),
    
    # Protected Dashboard/Profile endpoint
    path('api/dashboard/', UserDashboardView.as_view(), name='dashboard'),
]