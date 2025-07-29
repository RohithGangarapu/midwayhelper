import requests
from haversine import haversine, Unit
from geopy.geocoders import Nominatim
from app.models import *
geolocator = Nominatim(user_agent="midway",timeout=10)

def get_coordinates(city_name):
    location = geolocator.geocode(city_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        raise ValueError(f"Could not find coordinates for {city_name}")

def get_route_coords(source_latlon, dest_latlon):
    """Fetches coordinates from OSRM"""
    url = f"http://router.project-osrm.org/route/v1/driving/{source_latlon[1]},{source_latlon[0]};{dest_latlon[1]},{dest_latlon[0]}?overview=full&geometries=geojson"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['routes'][0]['geometry']['coordinates']
    else:
        raise Exception(f"OSRM Error: {response.status_code}, {response.text}")

def is_route_similar(route1, route2, threshold_km=2.0, min_overlap_ratio=0.6):
    """Check if two routes overlap based on haversine distance"""
    if not route1 or not route2:
        return False

    matches = 0
    for pt2 in route2:
        latlon2 = pt2[::-1]  # [lat, lon]
        for pt1 in route1:
            latlon1 = pt1[::-1]
            dist = haversine(latlon1, latlon2, unit=Unit.KILOMETERS)
            if dist <= threshold_km:
                matches += 1
                break

    ratio = matches / len(route2)
    return ratio >= min_overlap_ratio, round(ratio * 100, 2)

def find_matching_routes(req,new_source, new_dest, overlap_ratio=0.6):
    # Step 1: Get new route from OSRM
    new_route = get_route_coords(get_coordinates(new_source), get_coordinates(new_dest))

    # Step 2: Load all existing journeys
    matches = []
    all_journeys = Journey.objects.all()
    user=User.objects.get(id=req.session.get("user"))
    for journey in all_journeys:
        if journey.user!=user:
            existing_route = get_route_coords((journey.source_lat,journey.source_lon),(journey.dest_lat,journey.dest_lon))
        
            # Step 3: Compare each stored route with new route
            is_match, percent = is_route_similar(new_route, existing_route, min_overlap_ratio=overlap_ratio)
            print(is_match,percent)
            if is_match:
                matches.append(
                journey
                )
    return matches