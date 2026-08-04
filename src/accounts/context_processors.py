from builder.models import PublishedPage

def auth_context(request):
    """
    Add authentication context to all templates
    """
    context = {}
    
    # Detect if we're on a built website
    website = None
    if hasattr(request, 'published_page') and request.published_page:
        website = request.published_page
    elif hasattr(request, 'domain_type') and request.domain_type == 'custom':
        if hasattr(request, 'published_page') and request.published_page:
            website = request.published_page
    
    context['website'] = website
    context['is_builder_context'] = website is None
    context['is_website_context'] = website is not None
    
    return context
