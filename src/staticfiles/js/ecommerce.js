class AtomicReviewManager {
    constructor(subdomain = null) {
        this.currentPage = 1;
        this.hasMore = true;
        this.currentSort = 'newest';
        this.currentFilter = 'all';
        this.currentProductId = null;
        this.currentSubdomain = subdomain;
        this.reviews = [];
        
        console.log(`Atomic Review Manager initialized with subdomain: ${subdomain}`);
    }

    async loadReviews(productId, page = 1, sort = 'newest', filter = 'all') {
        try {
            this.currentProductId = productId;
            this.currentPage = page;
            this.currentSort = sort;
            this.currentFilter = filter;

            console.log(`📝 Loading reviews for product ${productId}, page ${page}`);

            const response = await fetch(`/builder/reviews/${this.currentSubdomain}/${productId}/?page=${page}&sort=${sort}&filter=${filter}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('📦 API Response received');

            if (data.success) {
                // Store reviews for atomic updates
                if (page === 1) {
                    this.reviews = data.reviews;
                } else {
                    this.reviews = [...this.reviews, ...data.reviews];
                }
                
                // Update ALL atomic elements on the page
                this.updateAllAtomicElements(data);
                
                this.currentPage = page;
                this.hasMore = data.has_more || false;
                
                // Update load more button
                this.updateLoadMoreButton();
                
                return data;
            } else {
                console.error('❌ API error:', data.error);
                this.showMessage('Error loading reviews: ' + data.error, 'error');
                return null;
            }
        } catch (error) {
            console.error('❌ Network error:', error);
            this.showMessage('Error loading reviews', 'error');
            return null;
        }
    }

    updateAllAtomicElements(data) {
        // 1. Update statistics elements
        this.updateStatisticsAtomic(data.statistics);
        
        // 2. Update review list container structure
        this.updateReviewListStructure(data.reviews);
        
        // 3. Update individual review elements
        this.updateIndividualReviewElements();
    }

    updateStatisticsAtomic(statistics) {
        if (!statistics) return;
        
        console.log('📊 Updating atomic statistics elements');
        
        // 1. Average Rating Number
        document.querySelectorAll('[data-review-average]').forEach(el => {
            el.textContent = statistics.average_rating ? statistics.average_rating.toFixed(1) : '0.0';
        });
        
        // 2. Total Review Count
        document.querySelectorAll('[data-review-total]').forEach(el => {
            const count = statistics.total_reviews || 0;
            el.textContent = count;
        });
        
        // 3. Individual Star Counts
        [5, 4, 3, 2, 1].forEach(rating => {
            const ratingData = statistics.rating_distribution?.find(r => r.rating === rating);
            const count = ratingData ? ratingData.count : 0;
            
            document.querySelectorAll(`[data-review-count="${rating}"]`).forEach(el => {
                el.textContent = count;
            });
        });
        
        // 4. Rating Bars (progress bars)
        document.querySelectorAll('[data-review-rating-bar]').forEach(barContainer => {
            this.updateRatingBar(barContainer, statistics);
        });
        
        // 5. Star Display (visual stars)
        document.querySelectorAll('[data-review-stars]').forEach(container => {
            this.updateStarDisplay(container, statistics.average_rating);
        });
    }

    updateRatingBar(container, statistics) {
        if (!statistics || !statistics.rating_distribution) return;
        
        const totalReviews = statistics.total_reviews || 0;
        
        // Create individual rating bars
        for (let rating = 5; rating >= 1; rating--) {
            const ratingData = statistics.rating_distribution.find(r => r.rating === rating);
            const count = ratingData ? ratingData.count : 0;
            const percentage = totalReviews > 0 ? (count / totalReviews) * 100 : 0;
            
            // Find or create bar for this rating
            let bar = container.querySelector(`[data-rating="${rating}"]`);
            if (!bar) {
                bar = document.createElement('div');
                bar.dataset.rating = rating;
                bar.className = 'review-rating-bar';
                container.appendChild(bar);
            }
            
            // Update bar content
            bar.innerHTML = `
                <span class="rating-label">${rating} Stars</span>
                <div class="rating-progress">
                    <div class="rating-progress-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="rating-count">${count}</span>
            `;
        }
    }

    updateStarDisplay(container, averageRating) {
        if (!container || averageRating === undefined) return;
        
        // Clear existing stars
        container.innerHTML = '';
        
        // Create individual star elements
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('span');
            star.className = 'review-star';
            star.dataset.starIndex = i;
            
            if (averageRating >= i) {
                star.className += ' star-full';
                star.textContent = '★';
            } else if (averageRating >= i - 0.5) {
                star.className += ' star-half';
                star.textContent = '★';
            } else {
                star.className += ' star-empty';
                star.textContent = '★';
            }
            
            container.appendChild(star);
        }
        
        // Also add the average rating number if container has data-show-rating
        if (container.dataset.showRating === 'true') {
            const ratingText = document.createElement('span');
            ratingText.className = 'review-average-text';
            ratingText.textContent = averageRating.toFixed(1);
            container.appendChild(ratingText);
        }
    }

    updateReviewListStructure(reviews) {
        const container = document.querySelector('.reviews-list-container');
        if (!container) return;
        
        // Get or create reviews list
        let reviewsList = container.querySelector('.reviews-list');
        if (!reviewsList) {
            reviewsList = document.createElement('div');
            reviewsList.className = 'reviews-list';
            container.appendChild(reviewsList);
        }
        
        // Clear if first page
        if (this.currentPage === 1) {
            reviewsList.innerHTML = '';
        }
        
        // Handle empty state
        if (!reviews || reviews.length === 0) {
            if (this.currentPage === 1) {
                reviewsList.innerHTML = `
                    <div class="no-reviews-message">
                        No reviews yet. Be the first to review!
                    </div>
                `;
            }
            return;
        }
        
        // Create atomic review structure
        reviews.forEach((review, index) => {
            this.createAtomicReviewElement(review, reviewsList, index);
        });
        
        // Initialize helpful buttons
        this.initializeAtomicHelpfulButtons();
    }

    createAtomicReviewElement(review, container, reviewIndex) {
        // Create a wrapper with minimal structure
        const reviewWrapper = document.createElement('div');
        reviewWrapper.className = 'review-atomic-wrapper';
        reviewWrapper.dataset.reviewIndex = reviewIndex;
        reviewWrapper.dataset.reviewId = review.id;
        
        // Add ONLY atomic data attributes - no HTML content!
        reviewWrapper.innerHTML = `
            <!-- Each piece of data is completely separate -->
            <div class="review-user" data-review-user="${review.id}"></div>
            <div class="review-rating" data-review-rating="${review.id}"></div>
            <div class="review-date" data-review-date="${review.id}"></div>
            <div class="review-title" data-review-title="${review.id}"></div>
            <div class="review-content" data-review-content="${review.id}"></div>
            <div class="review-helpful" data-review-helpful="${review.id}"></div>
            ${review.is_verified ? '<div class="review-verified" data-review-verified="' + review.id + '"></div>' : ''}
        `;
        
        container.appendChild(reviewWrapper);
        
        // Now populate each atomic element
        this.updateSingleReviewElements(review);
    }

    updateSingleReviewElements(review) {
        if (!review) return;
        
        // 1. User Name
        document.querySelectorAll(`[data-review-user="${review.id}"]`).forEach(el => {
            el.textContent = this.escapeHtml(review.user_name);
            el.className = 'review-user-name';
        });
        
        // 2. Rating Stars
        document.querySelectorAll(`[data-review-rating="${review.id}"]`).forEach(el => {
            el.className = 'review-user-rating';
            el.innerHTML = '';
            
            for (let i = 1; i <= 5; i++) {
                const star = document.createElement('span');
                star.className = 'user-rating-star';
                
                if (review.rating >= i) {
                    star.className += ' star-full';
                    star.textContent = '★';
                } else if (review.rating >= i - 0.5) {
                    star.className += ' star-half';
                    star.textContent = '★';
                } else {
                    star.className += ' star-empty';
                    star.textContent = '★';
                }
                
                el.appendChild(star);
            }
        });
        
        // 3. Date
        document.querySelectorAll(`[data-review-date="${review.id}"]`).forEach(el => {
            const date = new Date(review.created_at);
            el.textContent = date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            el.className = 'review-date-text';
        });
        
        // 4. Title
        document.querySelectorAll(`[data-review-title="${review.id}"]`).forEach(el => {
            el.textContent = this.escapeHtml(review.title);
            el.className = 'review-title-text';
        });
        
        // 5. Content
        document.querySelectorAll(`[data-review-content="${review.id}"]`).forEach(el => {
            el.textContent = this.escapeHtml(review.comment);
            el.className = 'review-content-text';
        });
        
        // 6. Helpful Button
        document.querySelectorAll(`[data-review-helpful="${review.id}"]`).forEach(el => {
            el.innerHTML = `
                <button class="atomic-helpful-btn" data-review-id="${review.id}">
                    Helpful (${review.helpful_count || 0})
                </button>
            `;
            el.className = 'review-helpful-container';
        });
        
        // 7. Verified Badge
        if (review.is_verified) {
            document.querySelectorAll(`[data-review-verified="${review.id}"]`).forEach(el => {
                el.innerHTML = '<span class="verified-badge">✓ Verified</span>';
                el.className = 'review-verified-badge';
            });
        }
    }

    updateIndividualReviewElements() {
        // Update each review in our stored list
        this.reviews.forEach(review => {
            this.updateSingleReviewElements(review);
        });
    }

    updateLoadMoreButton() {
        const loadMoreBtn = document.querySelector('.atomic-load-more');
        if (!loadMoreBtn) return;
        
        loadMoreBtn.style.display = this.hasMore ? 'block' : 'none';
        loadMoreBtn.disabled = !this.hasMore;
        
        if (!this.hasMore && this.reviews.length > 0) {
            loadMoreBtn.textContent = 'No more reviews';
        } else {
            loadMoreBtn.textContent = 'Load More Reviews';
        }
    }

    initializeAtomicHelpfulButtons() {
        document.querySelectorAll('.atomic-helpful-btn').forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                const reviewId = button.dataset.reviewId;
                
                if (!reviewId) return;
                
                button.disabled = true;
                const originalText = button.textContent;
                button.textContent = 'Voting...';
                
                try {
                    const response = await fetch(`/builder/review/helpful/${this.currentSubdomain}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify({ review_id: reviewId })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        button.textContent = `Helpful (${data.helpful_count})`;
                        button.disabled = true;
                        button.classList.add('voted');
                        this.showMessage('Thanks for your feedback!', 'success');
                    } else {
                        button.disabled = false;
                        button.textContent = originalText;
                        this.showMessage(data.error || 'Error voting', 'error');
                    }
                } catch (error) {
                    console.error('Error voting:', error);
                    button.disabled = false;
                    button.textContent = originalText;
                    this.showMessage('Error voting', 'error');
                }
            });
        });
    }

    initializeAtomicReviewForm() {
        const form = document.querySelector('.atomic-review-form');
        if (!form) return;
        
        const productId = form.dataset.productId;
        
        // Initialize star rating
        this.initializeAtomicStarInput(form);
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const rating = formData.get('rating');
            const title = formData.get('title');
            const comment = formData.get('comment');
            
            if (!rating || !title || !comment) {
                this.showMessage('Please fill all fields', 'error');
                return;
            }
            
            const submitBtn = form.querySelector('.atomic-submit-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            try {
                const response = await fetch(`/builder/review/submit/${this.currentSubdomain}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        product_id: productId,
                        rating: parseInt(rating),
                        title: title.trim(),
                        comment: comment.trim()
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showMessage('Review submitted successfully!', 'success');
                    form.reset();
                    this.resetAtomicStarRating(form);
                    this.loadReviews(productId, 1, this.currentSort, this.currentFilter);
                } else {
                    this.showMessage(data.error || 'Error submitting', 'error');
                }
            } catch (error) {
                console.error('Submit error:', error);
                this.showMessage('Error submitting review', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Review';
            }
        });
    }

    initializeAtomicStarInput(form) {
        const starContainer = form.querySelector('.atomic-star-input');
        if (!starContainer) return;
        
        starContainer.innerHTML = '';
        
        // Create 5 stars
        for (let i = 5; i >= 1; i--) {
            const input = document.createElement('input');
            input.type = 'radio';
            input.id = `atomic-star-${i}`;
            input.name = 'rating';
            input.value = i;
            
            const label = document.createElement('label');
            label.htmlFor = `atomic-star-${i}`;
            label.textContent = '★';
            label.className = 'atomic-star-label';
            
            input.addEventListener('change', () => {
                // Update all star labels
                starContainer.querySelectorAll('.atomic-star-label').forEach((label, index) => {
                    if (5 - index <= i) {
                        label.classList.add('selected');
                    } else {
                        label.classList.remove('selected');
                    }
                });
            });
            
            starContainer.appendChild(input);
            starContainer.appendChild(label);
        }
    }

    resetAtomicStarRating(form) {
        const starContainer = form.querySelector('.atomic-star-input');
        if (!starContainer) return;
        
        starContainer.querySelectorAll('input[type="radio"]').forEach(input => {
            input.checked = false;
        });
        
        starContainer.querySelectorAll('.atomic-star-label').forEach(label => {
            label.classList.remove('selected');
        });
    }

    showMessage(message, type = 'info') {
        // Create simple message
        const messageDiv = document.createElement('div');
        messageDiv.className = `atomic-message atomic-message-${type}`;
        messageDiv.textContent = message;
        
        // Add to page
        document.body.appendChild(messageDiv);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize Atomic System
function initializeAtomicReviewSystem() {
    console.log('🔧 Initializing Atomic Review System');
    
    // Get subdomain (use your existing logic)
    let subdomain = null;
    const host = window.location.hostname;
    
    if (host.includes('localhost')) {
        const parts = host.split('.');
        if (parts.length >= 2 && parts[0] !== 'localhost') {
            subdomain = parts[0];
        }
    } else {
        const parts = host.split('.');
        if (parts.length >= 3) {
            subdomain = parts[0];
        }
    }
    
    // Fallback to data attribute
    if (!subdomain) {
        const container = document.querySelector('[data-review-subdomain]');
        subdomain = container ? container.dataset.reviewSubdomain : null;
    }
    
    if (!subdomain) {
        console.error('❌ No subdomain found');
        return;
    }
    
    // Initialize manager
    window.atomicReviewManager = new AtomicReviewManager(subdomain);
    
    // Initialize form if present
    window.atomicReviewManager.initializeAtomicReviewForm();
    
    // Load reviews for any product on page
    document.querySelectorAll('[data-review-product]').forEach(container => {
        const productId = container.dataset.reviewProduct;
        if (productId) {
            window.atomicReviewManager.loadReviews(productId);
        }
    });
    
    // Event listeners
    document.addEventListener('change', (e) => {
        if (e.target.matches('[data-review-sort]')) {
            const container = e.target.closest('[data-review-product]');
            if (container && window.atomicReviewManager) {
                const productId = container.dataset.reviewProduct;
                const sort = e.target.value || 'newest';
                window.atomicReviewManager.loadReviews(productId, 1, sort, 'all');
            }
        }
        
        if (e.target.matches('[data-review-filter]')) {
            const container = e.target.closest('[data-review-product]');
            if (container && window.atomicReviewManager) {
                const productId = container.dataset.reviewProduct;
                const filter = e.target.value || 'all';
                window.atomicReviewManager.loadReviews(productId, 1, 'newest', filter);
            }
        }
    });
    
    // Load more
    document.addEventListener('click', (e) => {
        if (e.target.matches('.atomic-load-more')) {
            e.preventDefault();
            if (window.atomicReviewManager && window.atomicReviewManager.currentProductId) {
                window.atomicReviewManager.loadReviews(
                    window.atomicReviewManager.currentProductId,
                    window.atomicReviewManager.currentPage + 1,
                    window.atomicReviewManager.currentSort,
                    window.atomicReviewManager.currentFilter
                );
            }
        }
    });
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAtomicReviewSystem);
} else {
    initializeAtomicReviewSystem();
}



