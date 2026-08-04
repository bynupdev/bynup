class AuthManager {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupAuthLinks();
        this.setupContextDetection();
    }
    
    setupAuthLinks() {
        // Make auth links context-aware
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-auth-context]')) {
                e.preventDefault();
                this.handleAuthClick(e.target);
            }
        });
    }
    
    setupContextDetection() {
        // Detect if we're on a built website
        const websiteData = document.querySelector('[data-website-info]');
        if (websiteData) {
            this.context = 'website';
            this.websiteId = websiteData.dataset.websiteId;
            this.websiteName = websiteData.dataset.websiteName;
        } else {
            this.context = 'builder';
        }
    }
    
    handleAuthClick(element) {
        const action = element.dataset.authAction;
        const url = this.getAuthUrl(action);
        
        if (url) {
            window.location.href = url;
        }
    }
    
    getAuthUrl(action) {
        const baseUrls = {
            login: '/accounts/login/',
            register: '/accounts/register/',
            logout: '/accounts/logout/'
        };
        
        let url = baseUrls[action];
        
        if (this.context === 'website' && this.websiteId) {
            if (action === 'register') {
                url = `/accounts/website/register/${this.websiteSlug}/`;
            } else if (action === 'login') {
                url += `?website_id=${this.websiteId}`;
            }
        }
        
        return url;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});