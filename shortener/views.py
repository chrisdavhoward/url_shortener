from django.shortcuts import render, get_object_or_404
from django.http import HttpResponsePermanentRedirect
from .models import URL
from .forms import URLForm
from django.contrib import messages

def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def index(request):
    """Home page with URL shortening form."""
    form = URLForm()
    context = {'form': form}
    
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['original_url']
            
            # Get client IP
            ip_address = get_client_ip(request)
            
            # Check rate limiting (max 10 URLs per 10 minutes)
            recent_urls = URL.get_recent_urls_by_ip(ip_address, minutes=10)
            if recent_urls.count() >= 10:
                messages.error(
                    request, 
                    "Rate limit exceeded. Please try again later."
                )
            else:
                # Check if this URL already has a short code
                existing_url = URL.objects.filter(original_url=original_url).first()
                if existing_url:
                    short_code = existing_url.short_code
                else:
                    # Create a new short URL
                    short_code = URL.create_short_code()
                    URL.objects.create(
                        original_url=original_url, 
                        short_code=short_code,
                        ip_address=ip_address
                    )
                
                # Build the full short URL
                short_url = request.build_absolute_uri(f'/{short_code}')
                context['short_url'] = short_url
        
        # Always update the form in the context
        context['form'] = form
    
    return render(request, 'shortener/index.html', context)

def redirect_to_original(request, short_code):
    """Redirect from short URL to original URL with a 301 status code."""
    url_obj = get_object_or_404(URL, short_code=short_code)
    return HttpResponsePermanentRedirect(url_obj.original_url)