from django.conf import settings
from django.urls import reverse

def get_website_homepage_url(website):
    """
    Generate the correct homepage URL for a website
    Returns: URL string with ?page=home parameter
    """
    if website.is_custom_domain_active and website.custom_domain:
        # For custom domains
        return f"https://{website.custom_domain}/?page=home"
    else:
        # For subdomains
        if settings.DEBUG:
            return f"http://{website.subdomain}.localhost:8000/?page=home"
        else:
            # In production, use your actual domain
            production_domain = getattr(settings, 'PRODUCTION_DOMAIN', 'yourdomain.com')
            return f"https://{website.subdomain}.{production_domain}/?page=home"

def get_website_url(website, page_name='home'):
    """
    Generate URL for any page on a website
    """
    if website.is_custom_domain_active and website.custom_domain:
        # For custom domains
        if page_name == 'home':
            return f"https://{website.custom_domain}/?page=home"
        else:
            return f"https://{website.custom_domain}/{page_name}/"
    else:
        # For subdomains
        if settings.DEBUG:
            if page_name == 'home':
                return f"http://{website.subdomain}.localhost:8000/?page=home"
            else:
                return f"http://{website.subdomain}.localhost:8000/{page_name}/"
        else:
            production_domain = getattr(settings, 'PRODUCTION_DOMAIN', 'yourdomain.com')
            if page_name == 'home':
                return f"https://{website.subdomain}.{production_domain}/?page=home"
            else:
                return f"https://{website.subdomain}.{production_domain}/{page_name}/"
