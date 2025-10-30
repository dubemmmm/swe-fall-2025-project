// Pet Profile Form JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // File upload preview functionality
    const profilePicInput = document.getElementById('id_profile_picture');
    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(e) {
            const files = e.target.files;
            if (files.length > 0) {
                const uploadArea = document.querySelector('.photo-upload-area');
                const uploadText = uploadArea.querySelector('.upload-text');
                if (uploadText) {
                    uploadText.textContent = `Selected: ${files[0].name}`;
                }
            }
        });
    }

    // Cancel button functionality
    const cancelBtn = document.querySelector('.cancel-btn');
    if (cancelBtn && cancelBtn.tagName === 'BUTTON') {
        cancelBtn.addEventListener('click', function() {
            window.history.back();
        });
    }
});
