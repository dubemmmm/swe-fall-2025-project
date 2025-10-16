/**
 * Geolocation utilities for getting user's current location.
 * Use this in your registration/profile forms to automatically detect location.
 */

/**
 * Get the user's current location using the browser's Geolocation API.
 * This will prompt the user to allow location access.
 *
 * @returns {Promise} Resolves with {latitude, longitude} or rejects with error
 */
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        // Check if geolocation is supported
        if (!navigator.geolocation) {
            reject(new Error('Geolocation is not supported by your browser'));
            return;
        }

        // Request current position
        navigator.geolocation.getCurrentPosition(
            // Success callback
            (position) => {
                resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy // in meters
                });
            },
            // Error callback
            (error) => {
                let errorMessage = '';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage = 'User denied location permission';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage = 'Location information unavailable';
                        break;
                    case error.TIMEOUT:
                        errorMessage = 'Location request timed out';
                        break;
                    default:
                        errorMessage = 'Unknown error occurred';
                }
                reject(new Error(errorMessage));
            },
            // Options
            {
                enableHighAccuracy: true,  // Use GPS if available
                timeout: 10000,            // 10 second timeout
                maximumAge: 300000         // Accept cached position up to 5 minutes old
            }
        );
    });
}

/**
 * Get human-readable address from coordinates using reverse geocoding.
 * Uses OpenStreetMap's Nominatim API.
 *
 * @param {number} latitude - Latitude coordinate
 * @param {number} longitude - Longitude coordinate
 * @returns {Promise} Resolves with address string
 */
async function getAddressFromCoordinates(latitude, longitude) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`,
            {
                headers: {
                    'User-Agent': 'PetNextDoorApp/1.0'
                }
            }
        );

        if (!response.ok) {
            throw new Error('Failed to get address');
        }

        const data = await response.json();
        const address = data.address || {};

        // Build a readable address
        const parts = [];
        if (address.city) parts.push(address.city);
        else if (address.town) parts.push(address.town);

        if (address.state) parts.push(address.state);
        if (address.country) parts.push(address.country);

        return parts.join(', ') || data.display_name;
    } catch (error) {
        console.error('Error getting address:', error);
        return null;
    }
}

/**
 * Complete function to get location and update form fields.
 * Call this when the user clicks "Use My Location" button.
 *
 * @param {string} latFieldId - ID of the latitude input field
 * @param {string} lonFieldId - ID of the longitude input field
 * @param {string} addressFieldId - ID of the address input field (optional)
 * @param {Function} successCallback - Optional callback on success
 * @param {Function} errorCallback - Optional callback on error
 */
async function autoFillLocation(latFieldId, lonFieldId, addressFieldId = null, successCallback = null, errorCallback = null) {
    try {
        // Show loading state
        console.log('Getting your location...');

        // Get coordinates
        const coords = await getCurrentLocation();

        // Update latitude and longitude fields
        document.getElementById(latFieldId).value = coords.latitude;
        document.getElementById(lonFieldId).value = coords.longitude;

        // Get and update address if field is provided
        if (addressFieldId) {
            const address = await getAddressFromCoordinates(coords.latitude, coords.longitude);
            if (address) {
                document.getElementById(addressFieldId).value = address;
            }
        }

        console.log('Location set successfully!');

        // Call success callback if provided
        if (successCallback) {
            successCallback(coords);
        }

    } catch (error) {
        console.error('Error getting location:', error.message);

        // Call error callback if provided
        if (errorCallback) {
            errorCallback(error);
        } else {
            alert('Could not get your location. Please enter it manually or check location permissions.');
        }
    }
}

// Example usage:
// Add a button to your form:
// <button type="button" onclick="autoFillLocation('id_latitude', 'id_longitude', 'id_location')">
//     Use My Current Location
// </button>
