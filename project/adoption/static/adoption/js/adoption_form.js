// Form elements
const form = document.getElementById('petAdoptionForm');
const uploadArea = document.getElementById('uploadArea');
const photoUpload = document.getElementById('photoUpload');
const uploadPrompt = document.getElementById('uploadPrompt');
const imagePreview = document.getElementById('imagePreview');
const previewImage = document.getElementById('previewImage');
const removeImageBtn = document.getElementById('removeImageBtn');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const submitLoader = document.getElementById('submitLoader');

// Toast elements
const toast = document.getElementById('toast');
const toastIcon = document.getElementById('toastIcon');
const toastTitle = document.getElementById('toastTitle');
const toastDescription = document.getElementById('toastDescription');

// Image preview data
let imageData = null;

// Upload area click handler
uploadArea.addEventListener('click', (e) => {
    if (!imagePreview.style.display || imagePreview.style.display === 'none') {
        photoUpload.click();
    }
});

// File input change handler
photoUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            showToast('error', 'Image size must be less than 5MB', '');
            photoUpload.value = '';
            return;
        }

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showToast('error', 'Please upload an image file', 'Only PNG, JPG, and JPEG files are allowed');
            photoUpload.value = '';
            return;
        }

        // Read and preview image
        const reader = new FileReader();
        reader.onloadend = () => {
            imageData = reader.result;
            previewImage.src = imageData;
            uploadPrompt.style.display = 'none';
            imagePreview.style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }
});

// Remove image button handler
removeImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    imageData = null;
    photoUpload.value = '';
    previewImage.src = '';
    uploadPrompt.style.display = 'flex';
    imagePreview.style.display = 'none';
    clearError('photoError');
});

// Form validation
function validateForm() {
    let isValid = true;

    // Pet Name validation
    const petName = document.getElementById('petName').value.trim();
    if (petName.length === 0) {
        showError('petNameError', 'Pet name is required');
        isValid = false;
    } else if (petName.length < 2) {
        showError('petNameError', 'Pet name must be at least 2 characters');
        isValid = false;
    } else {
        clearError('petNameError');
    }

    // Animal Type validation
    const animalType = document.getElementById('animalType').value;
    if (!animalType) {
        showError('animalTypeError', 'Please select an animal type');
        isValid = false;
    } else {
        clearError('animalTypeError');
    }

    // Age validation
    const age = document.getElementById('age').value;
    if (!age) {
        showError('ageError', 'Age is required');
        isValid = false;
    } else if (isNaN(age) || Number(age) < 0) {
        showError('ageError', 'Age must be a valid number');
        isValid = false;
    } else {
        clearError('ageError');
    }

    // Gender validation
    const gender = document.getElementById('gender').value;
    if (!gender) {
        showError('genderError', 'Please select a gender');
        isValid = false;
    } else {
        clearError('genderError');
    }

    // Description validation
    const description = document.getElementById('description').value.trim();
    if (description.length < 10) {
        showError('descriptionError', 'Description must be at least 10 characters');
        isValid = false;
    } else {
        clearError('descriptionError');
    }

    return isValid;
}

// Show error message
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = message;
    
    // Add error class to input
    const inputId = elementId.replace('Error', '');
    const inputElement = document.getElementById(inputId);
    if (inputElement) {
        inputElement.classList.add('error');
    }
}

// Clear error message
function clearError(elementId) {
    const errorElement = document.getElementById(elementId);
    errorElement.textContent = '';
    
    // Remove error class from input
    const inputId = elementId.replace('Error', '');
    const inputElement = document.getElementById(inputId);
    if (inputElement) {
        inputElement.classList.remove('error');
    }
}

// Mock API submission
async function submitPetListing(data) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            // Simulate 90% success rate
            if (Math.random() > 0.1) {
                resolve({ 
                    success: true, 
                    id: Math.random().toString(36).substr(2, 9) 
                });
            } else {
                reject(new Error('Network error. Please try again.'));
            }
        }, 1500);
    });
}

// Form submit handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validate form
    if (!validateForm()) {
        return;
    }

    // Disable submit button
    submitBtn.disabled = true;
    submitText.style.display = 'none';
    submitLoader.style.display = 'flex';

    // Collect form data
    const formData = {
        petName: document.getElementById('petName').value.trim(),
        animalType: document.getElementById('animalType').value,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        description: document.getElementById('description').value.trim(),
        photo: imageData,
        vaccinated: document.getElementById('vaccinated').checked,
        goodWithKids: document.getElementById('goodWithKids').checked,
        spayedNeutered: document.getElementById('spayedNeutered').checked,
    };

    try {
        // Submit to mock API
        await submitPetListing(formData);
        
        // Show success toast
        showToast(
            'success', 
            'Pet listing posted successfully!', 
            `${formData.petName} is now available for adoption.`
        );

        // Reset form
        form.reset();
        imageData = null;
        previewImage.src = '';
        uploadPrompt.style.display = 'flex';
        imagePreview.style.display = 'none';
        
        // Clear all error messages
        ['petNameError', 'animalTypeError', 'ageError', 'genderError', 'descriptionError', 'photoError'].forEach(clearError);
        
    } catch (error) {
        // Show error toast
        showToast(
            'error', 
            'Failed to post listing', 
            error.message || 'An unexpected error occurred'
        );
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitText.style.display = 'inline';
        submitLoader.style.display = 'none';
    }
});

// Show toast notification
function showToast(type, title, description) {
    // Set toast content
    toastTitle.textContent = title;
    toastDescription.textContent = description;
    
    // Set icon type
    toastIcon.className = `toast-icon ${type}`;
    
    // Show toast
    toast.classList.add('show');
    
    // Hide toast after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}

// Real-time validation on input
document.getElementById('petName').addEventListener('input', () => {
    const petName = document.getElementById('petName').value.trim();
    if (petName.length >= 2) {
        clearError('petNameError');
    }
});

document.getElementById('animalType').addEventListener('change', () => {
    if (document.getElementById('animalType').value) {
        clearError('animalTypeError');
    }
});

document.getElementById('age').addEventListener('input', () => {
    const age = document.getElementById('age').value;
    if (age && !isNaN(age) && Number(age) >= 0) {
        clearError('ageError');
    }
});

document.getElementById('gender').addEventListener('change', () => {
    if (document.getElementById('gender').value) {
        clearError('genderError');
    }
});

document.getElementById('description').addEventListener('input', () => {
    const description = document.getElementById('description').value.trim();
    if (description.length >= 10) {
        clearError('descriptionError');
    }
});