from django.contrib import admin
from .models import URL

class URLAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'original_url', 'created_at')
    search_fields = ('short_code', 'original_url')
    readonly_fields = ('created_at',)

admin.site.register(URL, URLAdmin)