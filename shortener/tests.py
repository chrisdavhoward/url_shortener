from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .models import URL
from .forms import URLForm
from .views import get_client_ip
from .spam_detection import is_spam_url

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
    
    def test_get_recent_urls_by_ip(self):
        """Test the get_recent_urls_by_ip method for rate limiting"""
        # Create some test URLs with the same IP
        test_ip = "192.168.1.1"
        
        # Create an old URL (outside the time window)
        old_url = URL.objects.create(
            original_url="https://example.com/old",
            short_code="old123",
            ip_address=test_ip
        )
        # Set created_at to 15 minutes ago
        old_url.created_at = timezone.now() - timedelta(minutes=15)
        old_url.save()
        
        # Create some recent URLs
        for i in range(3):
            URL.objects.create(
                original_url=f"https://example.com/recent{i}",
                short_code=f"rec{i}23",
                ip_address=test_ip
            )
        
        # Add a URL from a different IP
        URL.objects.create(
            original_url="https://example.com/other",
            short_code="other1",
            ip_address="10.0.0.1"
        )
        
        # Test get_recent_urls_by_ip with a 10-minute window
        recent_urls = URL.get_recent_urls_by_ip(test_ip, minutes=10)
        
        # Should have 3 recent URLs from our test IP
        self.assertEqual(recent_urls.count(), 3, 
                        "Should find 3 URLs created in the last 10 minutes")
        
        # Test with a larger window that includes the old URL
        all_urls = URL.get_recent_urls_by_ip(test_ip, minutes=20)
        self.assertEqual(all_urls.count(), 4,
                        "Should find 4 URLs with a 20-minute window")


class SpamDetectionTest(TestCase):
    def test_spam_detection(self):
        """Test that spam detection correctly identifies spam URLs"""
        # Test non-spam URLs
        safe_urls = [
            "https://example.com",
            "https://github.com/django/django",
            "https://docs.python.org/3/tutorial/index.html",
            "https://www.wikipedia.org/",
        ]
        
        for url in safe_urls:
            is_spam, reason = is_spam_url(url)
            self.assertFalse(is_spam, f"URL {url} incorrectly flagged as spam: {reason}")
        
        # Test spam URLs
        spam_urls = [
            "https://best-casino-games.xyz/win-money",
            "https://get-viagra-cheap.com",
            "https://make-money-fast-online.top",
            "https://sub1.sub2.sub3.sub4.example.com"  # Too many subdomains
        ]
        
        for url in spam_urls:
            is_spam, reason = is_spam_url(url)
            self.assertTrue(is_spam, f"URL {url} should be flagged as spam")
            self.assertIsNotNone(reason, "Spam reason should be provided")


class URLFormTest(TestCase):
    def test_form_validation(self):
        """Test that the form correctly validates URLs"""
        # Test valid URL
        form = URLForm(data={'original_url': 'https://example.com'})
        self.assertTrue(form.is_valid(), "Form should accept valid URL")
        
        # Test invalid URL format
        form = URLForm(data={'original_url': 'not-a-url'})
        self.assertFalse(form.is_valid(), "Form should reject invalid URL format")
        
        # Test empty submission
        form = URLForm(data={'original_url': ''})
        self.assertFalse(form.is_valid(), "Form should reject empty submission")
        
        # Test spam URL validation
        form = URLForm(data={'original_url': 'https://online-casino-games.xyz'})
        self.assertFalse(form.is_valid(), "Form should reject spam URL")
        self.assertIn('spam', form.errors['original_url'][0].lower(),
                    "Error message should mention spam")


class ViewsTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory
        self.factory = RequestFactory()
    
    def test_get_client_ip(self):
        """Test the get_client_ip helper function"""
        # Test with REMOTE_ADDR
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        ip = get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
        
        # Test with X-Forwarded-For
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 10.0.0.2'
        ip = get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')
    
    def test_rate_limiting(self):
        """Test that rate limiting prevents excessive URL creation"""
        # Create a test client
        client = self.client
        
        # Create URLs up to the limit
        for i in range(10):
            response = client.post(reverse('index'), {
                'original_url': f'https://example.com/test{i}'
            })
            # Should be successful
            self.assertEqual(response.status_code, 200)
            # If we got a short URL in the context, it was successful
            self.assertIn('short_url', response.context)
        
        # Try to create one more URL (should be rate limited)
        response = client.post(reverse('index'), {
            'original_url': 'https://example.com/one-too-many'
        })
        # Should still return 200 (the page loads) but with an error message
        self.assertEqual(response.status_code, 200)
        # Check that we didn't get a short URL in the context
        self.assertNotIn('short_url', response.context)
        # Check that we have a message
        messages = list(response.context['messages'])
        self.assertTrue(len(messages) > 0, "Should have an error message")
        self.assertIn('rate limit', str(messages[0]).lower(), 
                    "Message should mention rate limit")
    
    def test_redirect_view(self):
        """Test that short URLs correctly redirect to original URLs"""
        # Create a test URL
        test_url = URL.objects.create(
            original_url='https://example.com/test',
            short_code='test12'
        )
        
        # Test the redirect
        response = self.client.get(f'/{test_url.short_code}')
        self.assertEqual(response.status_code, 301, 
                        "Should return a 301 Permanent Redirect")
        self.assertEqual(response.url, test_url.original_url,
                        "Should redirect to the original URL")
        
        # Test a non-existent short code
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404,
                        "Should return a 404 for non-existent short codes")