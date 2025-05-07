from django.db import models
import random
import string

class URL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.original_url} -> {self.short_code}"
    
    @classmethod
    def create_short_code(cls):
        """Generate a random 6-character string for the short URL."""
        chars = string.ascii_letters + string.digits
        short_code = ''.join(random.choice(chars) for _ in range(6))
        
        # Make sure the code is unique
        while cls.objects.filter(short_code=short_code).exists():
            short_code = ''.join(random.choice(chars) for _ in range(6))
            
        return short_code