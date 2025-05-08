from django import forms

class URLForm(forms.Form):
    original_url = forms.URLField(
        label='Enter your long URL',
        max_length=2000,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/long/url'})
    )