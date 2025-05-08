from django import forms

class URLForm(forms.Form):
    original_url = forms.URLField(
        required=True,
        max_length=2000,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your long URL here (e.g., https://example.com/long/url)',
        })
    )