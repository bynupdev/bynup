// Create a file: static/builder/js/bynup-branding.js

(function() {
    // Check if branding should be shown (passed from Django)
    if (typeof window.BYNUP_CONFIG !== 'undefined' && !window.BYNUP_CONFIG.showBranding) {
        return; // Don't show branding for paid users
    }
    
    // Create branding element
    const style = document.createElement('style');
    style.textContent = `
        .bynup-branding {
            position: fixed;
            bottom: 16px;
            right: 16px;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .bynup-branding a {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(8px);
            padding: 8px 16px;
            border-radius: 40px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            text-decoration: none;
            color: #4a5568;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .bynup-branding a:hover {
            background: white;
            box-shadow: 0 4px 16px rgba(67, 97, 238, 0.15);
            transform: translateY(-1px);
            color: #4361ee;
        }
        .bynup-branding .bynup-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            border-radius: 6px;
            color: white;
            font-size: 11px;
            font-weight: 700;
        }
        .bynup-branding .bynup-text strong {
            font-weight: 700;
            background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        @media (max-width: 768px) {
            .bynup-branding { bottom: 12px; right: 12px; }
            .bynup-branding a { padding: 6px 12px; font-size: 12px; }
        }
    `;
    document.head.appendChild(style);
    
    const branding = document.createElement('div');
    branding.className = 'bynup-branding';
    branding.innerHTML = `
        <a href="https://bynup.store" target="_blank" rel="noopener">
            <span class="bynup-icon">b</span>
            <span class="bynup-text">Powered by <strong>bynUp</strong></span>
        </a>
    `;
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => document.body.appendChild(branding));
    } else {
        document.body.appendChild(branding);
    }
})();