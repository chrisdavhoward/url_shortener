from django.test import TestCase
from .models import URL

class URLModelTest(TestCase):
    def test_create_short_code(self):
        """Test that create_short_code creates a unique 6-character code"""
        # Generate a short code
        code1 = URL.create_short_code()
        
        # Check the length of the code
        self.assertEqual(len(code1), 6, "Short code should be 6 characters long")
        
        # Create a URL with this code
        URL.objects.create(
            original_url="https://example.com/test1",
            short_code=code1
        )
        
        # Generate another short code
        code2 = URL.create_short_code()
        
        # Check that it's different from the first
        self.assertNotEqual(code1, code2, "Generated codes should be unique")
        
        # Check that it's not in the database
        self.assertFalse(URL.objects.filter(short_code=code2).exists(),
                         "Generated code should not exist in the database yet")
        
        # Create many URLs to increase chance of collision
        codes = [code1, code2]
        for i in range(20):
            url = URL.objects.create(
                original_url=f"https://example.com/test{i+2}",
                short_code=URL.create_short_code()
            )
            # Ensure each new code is unique
            self.assertNotIn(url.short_code, codes, "All codes should be unique")
            codes.append(url.short_code)