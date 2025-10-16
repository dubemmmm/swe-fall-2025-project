"""
Location utility functions for the users app.
Provides IP-based geolocation as a fallback option.
"""
import requests
from decimal import Decimal


def get_location_from_ip(ip_address):
    """
    Get approximate location (latitude, longitude) from IP address.
    Uses a free IP geolocation service.

    Note: This is less accurate than browser geolocation but works as a fallback.

    Args:
        ip_address (str): The user's IP address

    Returns:
        dict: Contains 'latitude', 'longitude', 'city', 'region', 'country'
              Returns None if lookup fails
    """
    try:
        # Using ip-api.com (free tier: 45 requests/minute)
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data.get('status') == 'success':
                return {
                    'latitude': Decimal(str(data.get('lat'))),
                    'longitude': Decimal(str(data.get('lon'))),
                    'city': data.get('city'),
                    'region': data.get('regionName'),
                    'country': data.get('country'),
                    'location': f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
                }
    except Exception as e:
        print(f"Error getting location from IP: {e}")

    return None


def get_client_ip(request):
    """
    Extract the client's IP address from the request.
    Handles proxies and load balancers.

    Args:
        request: Django request object

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def reverse_geocode(latitude, longitude):
    """
    Convert latitude/longitude to a human-readable address.
    Uses OpenStreetMap's Nominatim API (free, no API key needed).

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        str: Formatted address or None if lookup fails
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'PetNextDoorApp/1.0'  # Nominatim requires a user agent
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})

            # Build a readable address
            parts = []
            if address.get('city'):
                parts.append(address['city'])
            elif address.get('town'):
                parts.append(address['town'])

            if address.get('state'):
                parts.append(address['state'])

            if address.get('country'):
                parts.append(address['country'])

            return ', '.join(parts) if parts else data.get('display_name')

    except Exception as e:
        print(f"Error reverse geocoding: {e}")

    return None


def geocode(address):
    """
    Convert a street address to latitude/longitude coordinates (geocoding).
    Uses OpenStreetMap's Nominatim API (free, no API key needed).

    Args:
        address (str): Street address, city, or any location description
                      Example: "123 Main St, New York, NY"

    Returns:
        dict: Contains 'latitude', 'longitude', 'display_name' (formatted address)
              Returns None if lookup fails
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,  # Only get the best match
            'addressdetails': 1
        }
        headers = {
            'User-Agent': 'PetNextDoorApp/1.0'  # Nominatim requires a user agent
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data and len(data) > 0:
                result = data[0]
                return {
                    'latitude': Decimal(result['lat']),
                    'longitude': Decimal(result['lon']),
                    'display_name': result.get('display_name', address)
                }

    except Exception as e:
        print(f"Error geocoding address: {e}")

    return None
