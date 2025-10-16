from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .location_utils import get_client_ip, get_location_from_ip, reverse_geocode, geocode
from decimal import Decimal, InvalidOperation


def register(request):
    """
    User registration view with automatic location detection.
    Supports both browser geolocation and IP-based fallback.
    """
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        profile_name = request.POST.get('profile_name')
        phone_number = request.POST.get('phone_number', '')
        bio = request.POST.get('bio', '')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        profile_photo = request.FILES.get('profile_photo')

        # Validate required fields
        if not all([username, email, password, profile_name, location]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/register.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, 'users/register.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered. Please login instead.')
            return render(request, 'users/register.html')

        # Handle location data
        # Priority: Browser geolocation > IP-based > Manual input
        try:
            if latitude and longitude:
                # User provided coordinates from browser geolocation
                latitude = Decimal(latitude)
                longitude = Decimal(longitude)

                # If no readable address provided, reverse geocode
                if not location or location.strip() == '':
                    location = reverse_geocode(latitude, longitude) or "Location not specified"
            else:
                # No coordinates from browser, try IP-based location as fallback
                ip_address = get_client_ip(request)
                ip_location = get_location_from_ip(ip_address)

                if ip_location:
                    latitude = ip_location['latitude']
                    longitude = ip_location['longitude']
                    # Use IP location if user didn't provide one
                    if not location or location.strip() == '':
                        location = ip_location['location']
                    messages.info(request, f'Location detected from IP: {ip_location["location"]}')
                else:
                    # IP geolocation failed, set coordinates to None
                    latitude = None
                    longitude = None
                    messages.warning(request, 'Could not detect your location automatically. You can update it later in your profile.')
        except (ValueError, InvalidOperation) as e:
            # Invalid coordinate format
            latitude = None
            longitude = None
            messages.warning(request, 'Invalid location coordinates. You can update your location later.')

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                profile_name=profile_name,
                phone_number=phone_number,
                bio=bio,
                location=location,
                latitude=latitude,
                longitude=longitude,
            )

            # Handle profile photo if provided
            if profile_photo:
                user.profile_photo = profile_photo
                user.save()

            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome to Pet Next Door, {profile_name}!')
            return redirect('home')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'users/register.html')

    return render(request, 'users/register.html')


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.profile_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """View user profile"""
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    """
    Edit user profile including location.
    Supports both browser geolocation and manual address entry with geocoding.
    """
    user = request.user

    if request.method == 'POST':
        # Get form data
        profile_name = request.POST.get('profile_name')
        phone_number = request.POST.get('phone_number', '')
        bio = request.POST.get('bio', '')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        profile_photo = request.FILES.get('profile_photo')
        use_manual_address = request.POST.get('use_manual_address') == 'true'

        # Validate required fields
        if not profile_name:
            messages.error(request, 'Profile name is required.')
            return render(request, 'users/edit_profile.html', {'user': user})

        # Handle location updates
        try:
            if use_manual_address and location:
                # User entered a manual address - geocode it
                geocode_result = geocode(location)

                if geocode_result:
                    latitude = geocode_result['latitude']
                    longitude = geocode_result['longitude']
                    location = geocode_result['display_name']
                    messages.success(request, f'Address found: {location}')
                else:
                    messages.warning(request, 'Could not find that address. Please try a different format.')
                    return render(request, 'users/edit_profile.html', {'user': user})

            elif latitude and longitude:
                # User used browser geolocation
                latitude = Decimal(latitude)
                longitude = Decimal(longitude)

                # If no readable address provided, reverse geocode
                if not location or location.strip() == '':
                    location = reverse_geocode(latitude, longitude) or "Location not specified"

            # Update user profile
            user.profile_name = profile_name
            user.phone_number = phone_number
            user.bio = bio

            if location:
                user.location = location
            if latitude:
                user.latitude = latitude
            if longitude:
                user.longitude = longitude

            if profile_photo:
                user.profile_photo = profile_photo

            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')

        except (ValueError, InvalidOperation) as e:
            messages.error(request, f'Invalid location data: {str(e)}')
            return render(request, 'users/edit_profile.html', {'user': user})
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return render(request, 'users/edit_profile.html', {'user': user})

    return render(request, 'users/edit_profile.html', {'user': user})


def home(request):
    """Homepage view"""
    return render(request, 'home.html')
