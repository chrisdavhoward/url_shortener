from django import forms
from .spam_detection import is_spam_url

class URLForm(forms.Form):
    original_url = forms.URLField(
        required=True,
        max_length=2000,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your long URL here (e.g., https://example.com/long/url)',
        })
    )
    
    def clean_original_url(self):
        """Validate that the URL is not spam."""
        url = self.cleaned_data['original_url']
        
        # Check if URL is spam
        is_spam, reason = is_spam_url(url)
        if is_spam:
            raise forms.ValidationError(
                f"This URL has been flagged as potential spam. Reason: {reason}"
            )
        
        return url