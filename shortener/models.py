from django.db import models
import random
import string
import time
from django.utils import timezone
from datetime import timedelta, datetime

class URL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.original_url} -> {self.short_code}"
    
    @classmethod
    def create_short_code(cls):
        """Generate a random 6-character string for the short URL."""
        max_attempts = 10
        chars = string.ascii_letters + string.digits
        
        for _ in range(max_attempts):
            # Generate a random code
            short_code = ''.join(random.choice(chars) for _ in range(6))
            
            # Just check if the code exists, don't create anything yet
            if not cls.objects.filter(short_code=short_code).exists():
                # This code appears to be available
                return short_code
        
        # Fallback: Use timestamp-based approach
        timestamp = str(int(time.time()))
        fallback_code = random.choice(chars) + timestamp[-5:]
        
        # Final check to ensure this doesn't exist either
        if cls.objects.filter(short_code=fallback_code).exists():
            # Add microsecond precision as last resort
            ms = str(datetime.now().microsecond)[:3]
            # Combine 2 random chars with timestamp and microseconds
            fallback_code = random.choice(chars) + random.choice(chars) + timestamp[-2:] + ms[:2]
    
        
        return fallback_code
    
    @classmethod
    def get_recent_urls_by_ip(cls, ip_address, minutes=10):
        """Get URLs created by this IP address in the last X minutes."""
        time_threshold = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            ip_address=ip_address,
            created_at__gt=time_threshold
        )