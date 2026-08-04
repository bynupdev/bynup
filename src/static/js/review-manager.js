document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('reviewForm');
            const submitBtn = document.querySelector('.submitBtn');
            const successPopup = document.getElementById('successPopup');
            
            if (form) {
                form.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    // Disable button and show loading
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Submitting...';
                    
                    try {
                        // Get form data
                        const formData = new FormData(form);
                        
                        // Submit to backend
                        const response = await fetch(form.action, {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            // Show success popup
                            showSuccessPopup();
                            
                            // Reset form
                            form.reset();
                            resetStarRating();
                            
                            // Reload page after 2 seconds to show new review
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                            
                        } else {
                            // Show error message
                            alert(data.error || 'Error submitting review');
                        }
                        
                    } catch (error) {
                        console.error('Error:', error);
                        alert('Network error. Please try again.');
                    } finally {
                        // Re-enable button
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Submit Review';
                    }
                });
            }
            
            function showSuccessPopup() {
                // Show popup
                successPopup.classList.add('show');
                
                // Hide after 2 seconds
                setTimeout(() => {
                    successPopup.classList.remove('show');
                }, 2000);
            }
            
            function resetStarRating() {
                // Uncheck all star ratings
                const starInputs = form.querySelectorAll('input[name="rating"]');
                starInputs.forEach(input => {
                    input.checked = false;
                });
                
                // Reset star colors
                const starLabels = form.querySelectorAll('.star-rating label');
                starLabels.forEach(label => {
                    label.style.color = '#e4e5e9';
                });
            }
            
            // Star rating visual feedback
            const starInputs = document.querySelectorAll('.star-rating input');
            starInputs.forEach(input => {
                input.addEventListener('change', function() {
                    const value = parseInt(this.value);
                    const labels = document.querySelectorAll('.star-rating label');
                    
                    labels.forEach((label, index) => {
                        if (5 - index <= value) {
                            label.style.color = '#ffc107';
                        } else {
                            label.style.color = '#e4e5e9';
                        }
                    });
                });
            });
            
            // Initial star rating reset
            resetStarRating();
        });