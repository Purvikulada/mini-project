# trip_app/services.py
import random
from decimal import Decimal

# Define simple cost constants for mock data (In a real app, this would be a DB or API)
DAILY_COST_ESTIMATES = {
    'paris': 150.00,  # Mock Hotel Cost per day
    'tokyo': 180.00,
    'nyc': 200.00,
    'london': 140.00
}

def fetch_points_of_interest(location):
    """MOCK function to fetch POIs for a location."""
    if 'paris' in location.lower():
        return [
            {'name': 'Eiffel Tower (Visit)', 'category': 'landmark', 'daily_visitors': 10000, 'cost': 30, 'time_needed': 3},
            {'name': 'Louvre Museum (Entry)', 'category': 'museum', 'daily_visitors': 8000, 'cost': 22, 'time_needed': 4},
            {'name': 'Notre Dame Cathedral (Exterior)', 'category': 'landmark', 'daily_visitors': 6000, 'cost': 0, 'time_needed': 2},
        ]
    # Default plan for other locations
    return [
        {'name': 'Local Landmark Tour', 'category': 'sightseeing', 'cost': 20, 'time_needed': 3},
        {'name': 'Explore Downtown Area', 'category': 'explore', 'cost': 0, 'time_needed': 3},
    ]


def generate_trip_suggestion(location, duration_days, user_budget):
    """
    Generates a trip plan and cost based on user constraints.
    """
    location = location.lower()
    
    # Step 1: Calculate Fixed Costs (Accommodation)
    daily_fixed_cost = DAILY_COST_ESTIMATES.get(location, 100) # Default to $100/day
    total_fixed_cost = Decimal(daily_fixed_cost) * duration_days
    
    activity_budget = user_budget - total_fixed_cost
    
    if activity_budget < 0:
        return None, None, total_fixed_cost # Budget failure

    # Step 2: Plan Activities based on remaining Budget and Duration
    all_pois = fetch_points_of_interest(location)
    
    daily_poi_budget = activity_budget / duration_days
    plan = {}
    total_activity_cost = Decimal(0)
    
    available_pois = all_pois[:] # Copy of POIs to track what's visited

    for day in range(1, duration_days + 1):
        day_plan = []
        current_day_cost = Decimal(0)
        current_time_spent = 0
        
        # Simple selection: Find the most expensive unvisited POI that fits today's budget
        affordable_and_unvisited = [p for p in available_pois if Decimal(p['cost']) <= (daily_poi_budget - current_day_cost)]
        
        if affordable_and_unvisited:
            # Sort by cost (as a proxy for importance)
            affordable_and_unvisited.sort(key=lambda x: x['cost'], reverse=True)
            
            poi = affordable_and_unvisited[0] # Pick the best fit
            poi_cost = Decimal(poi['cost'])
            
            day_plan.append({
                'activity': poi['name'],
                'cost': float(poi_cost),
                'time_hours': poi['time_needed'],
            })
            current_day_cost += poi_cost
            available_pois.remove(poi) # Remove from list so it's not visited again
            
        # Add a buffer for meals and local transport
        meal_buffer = Decimal(45)
        day_plan.append({
            'activity': 'Meals & Local Transport Buffer',
            'cost': float(meal_buffer),
            'time_hours': 0,
            'note': 'Allocate this for food and short travel.'
        })
        
        total_activity_cost += current_day_cost + meal_buffer
        plan[f'Day {day}'] = day_plan

    # Step 3: Final Cost Calculation
    final_suggested_cost = total_fixed_cost + total_activity_cost
    
    return plan, final_suggested_cost, total_fixed_cost