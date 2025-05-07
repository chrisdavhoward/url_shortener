from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import URL
from .forms import URLForm

def index(request):
    """Home page with URL shortening form."""
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            original_url = form.cleaned_data['original_url']
            
            # Check if this URL already has a short code
            existing_url = URL.objects.filter(original_url=original_url).first()
            if existing_url:
                short_url = request.build_absolute_uri(f'/{existing_url.short_code}')
                return render(request, 'shortener/success.html', {'short_url': short_url})
            
            # Create a new short URL
            short_code = URL.create_short_code()
            URL.objects.create(original_url=original_url, short_code=short_code)
            
            # Build the full short URL
            short_url = request.build_absolute_uri(f'/{short_code}')
            return render(request, 'shortener/success.html', {'short_url': short_url})
    else:
        form = URLForm()
    
    return render(request, 'shortener/index.html', {'form': form})

def redirect_to_original(request, short_code):
    """Redirect from short URL to original URL."""
    url_obj = get_object_or_404(URL, short_code=short_code)
    return redirect(url_obj.original_url)