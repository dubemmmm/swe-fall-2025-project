from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .location_utils import get_client_ip, get_location_from_ip, reverse_geocode, geocode
from decimal import Decimal, InvalidOperation
from pets.models import PetProfile


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
            return redirect('users:home')

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
            return redirect('users:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('landing')


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
    return render(request, 'users/home.html')


@login_required
def public_profile(request, user_id):
    """
    View public profile of another user (for playdate organizers to review requesters)
    """
    profile_user = get_object_or_404(User, id=user_id)

    # Get user's pets
    pets = PetProfile.objects.filter(owner=profile_user, is_playdate_available=True).prefetch_related('photos', 'traits')

    context = {
        'profile_user': profile_user,
        'pets': pets,
    }

    return render(request, 'users/public_profile.html', context)


def calculate_pet_compatibility(pet1, pet2):
    """
    Calculate compatibility score between two pets based on various factors.
    Returns a score from 0 to 100 and breakdown of factors.
    """
    score = 0
    max_score = 0
    factors = []

    # 1. Species Match (20 points)
    max_score += 20
    if pet1.species == pet2.species:
        score += 20
        factors.append({'name': 'Species Match', 'score': 20, 'max': 20, 'status': 'perfect', 'detail': f'Both are {pet1.get_species_display()}s'})
    else:
        factors.append({'name': 'Species Match', 'score': 0, 'max': 20, 'status': 'poor', 'detail': f'{pet1.name} is a {pet1.get_species_display()}, {pet2.name} is a {pet2.get_species_display()}'})

    # 2. Size Compatibility (15 points)
    max_score += 15
    size_map = {'SMALL': 1, 'MEDIUM': 2, 'LARGE': 3}
    size1 = size_map.get(pet1.general_size, 2)
    size2 = size_map.get(pet2.general_size, 2)
    size_diff = abs(size1 - size2)

    if size_diff == 0:
        size_score = 15
        size_status = 'perfect'
        size_detail = f'Both are {pet1.get_general_size_display()} sized'
    elif size_diff == 1:
        size_score = 10
        size_status = 'good'
        size_detail = f'{pet1.name} is {pet1.get_general_size_display()}, {pet2.name} is {pet2.get_general_size_display()} - Minor difference'
    else:
        size_score = 5
        size_status = 'fair'
        size_detail = f'{pet1.name} is {pet1.get_general_size_display()}, {pet2.name} is {pet2.get_general_size_display()} - Significant difference'

    score += size_score
    factors.append({'name': 'Size Compatibility', 'score': size_score, 'max': 15, 'status': size_status, 'detail': size_detail})

    # 3. Energy Level Match (25 points)
    max_score += 25
    energy_map = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
    energy1 = energy_map.get(pet1.energy_level, 2)
    energy2 = energy_map.get(pet2.energy_level, 2)
    energy_diff = abs(energy1 - energy2)

    if energy_diff == 0:
        energy_score = 25
        energy_status = 'perfect'
        energy_detail = f'Both have {pet1.get_energy_level_display()} energy'
    elif energy_diff == 1:
        energy_score = 15
        energy_status = 'good'
        energy_detail = f'{pet1.name} has {pet1.get_energy_level_display()} energy, {pet2.name} has {pet2.get_energy_level_display()} energy - Compatible'
    else:
        energy_score = 5
        energy_status = 'fair'
        energy_detail = f'{pet1.name} has {pet1.get_energy_level_display()} energy, {pet2.name} has {pet2.get_energy_level_display()} energy - May need supervision'

    score += energy_score
    factors.append({'name': 'Energy Level Match', 'score': energy_score, 'max': 25, 'status': energy_status, 'detail': energy_detail})

    # 4. Shared Traits (20 points)
    max_score += 20
    pet1_traits = set(pet1.traits.values_list('trait', flat=True))
    pet2_traits = set(pet2.traits.values_list('trait', flat=True))
    common_traits = pet1_traits & pet2_traits

    if len(common_traits) >= 3:
        trait_score = 20
        trait_status = 'perfect'
        trait_detail = f'Share {len(common_traits)} traits: {", ".join(list(common_traits)[:3])}'
    elif len(common_traits) >= 2:
        trait_score = 15
        trait_status = 'good'
        trait_detail = f'Share {len(common_traits)} traits: {", ".join(common_traits)}'
    elif len(common_traits) == 1:
        trait_score = 10
        trait_status = 'fair'
        trait_detail = f'Share 1 trait: {list(common_traits)[0]}'
    else:
        trait_score = 0
        trait_status = 'poor'
        trait_detail = 'No shared traits listed'

    score += trait_score
    factors.append({'name': 'Shared Traits', 'score': trait_score, 'max': 20, 'status': trait_status, 'detail': trait_detail})

    # 5. Age Compatibility (10 points) - Based on age string parsing
    max_score += 10
    try:
        # Try to extract numeric age from age string
        age1_num = int(''.join(filter(str.isdigit, pet1.age.split()[0]))) if pet1.age else 0
        age2_num = int(''.join(filter(str.isdigit, pet2.age.split()[0]))) if pet2.age else 0

        if age1_num and age2_num:
            age_diff = abs(age1_num - age2_num)
            if age_diff <= 2:
                age_score = 10
                age_status = 'perfect'
                age_detail = f'Similar ages: {pet1.age} and {pet2.age}'
            elif age_diff <= 5:
                age_score = 7
                age_status = 'good'
                age_detail = f'Compatible ages: {pet1.age} and {pet2.age}'
            else:
                age_score = 4
                age_status = 'fair'
                age_detail = f'Different ages: {pet1.age} and {pet2.age}'
        else:
            age_score = 5
            age_status = 'unknown'
            age_detail = 'Age information incomplete'
    except:
        age_score = 5
        age_status = 'unknown'
        age_detail = 'Could not determine age compatibility'

    score += age_score
    factors.append({'name': 'Age Compatibility', 'score': age_score, 'max': 10, 'status': age_status, 'detail': age_detail})

    # 6. Playdate Availability (10 points)
    max_score += 10
    if pet1.is_playdate_available and pet2.is_playdate_available:
        avail_score = 10
        avail_status = 'perfect'
        avail_detail = 'Both pets are available for playdates'
    else:
        avail_score = 0
        avail_status = 'poor'
        avail_detail = 'One or both pets may not be available'

    score += avail_score
    factors.append({'name': 'Playdate Availability', 'score': avail_score, 'max': 10, 'status': avail_status, 'detail': avail_detail})

    # Calculate percentage
    percentage = int((score / max_score) * 100) if max_score > 0 else 0

    # Determine overall rating
    if percentage >= 80:
        rating = 'Excellent Match'
        rating_class = 'excellent'
    elif percentage >= 60:
        rating = 'Good Match'
        rating_class = 'good'
    elif percentage >= 40:
        rating = 'Fair Match'
        rating_class = 'fair'
    else:
        rating = 'Needs Consideration'
        rating_class = 'poor'

    return {
        'score': score,
        'max_score': max_score,
        'percentage': percentage,
        'rating': rating,
        'rating_class': rating_class,
        'factors': factors
    }


@login_required
def pet_compatibility(request, pet1_id, pet2_id):
    """
    View to display compatibility score between two pets
    """
    pet1 = get_object_or_404(PetProfile, id=pet1_id)
    pet2 = get_object_or_404(PetProfile, id=pet2_id)

    # Calculate compatibility
    compatibility = calculate_pet_compatibility(pet1, pet2)

    context = {
        'pet1': pet1,
        'pet2': pet2,
        'compatibility': compatibility,
    }

    return render(request, 'users/pet_compatibility.html', context)
