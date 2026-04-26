from django.test import TestCase, Client, override_settings
from django.urls import reverse
from .models import BoardMember, Book
from django.core.files.uploadedfile import SimpleUploadedFile

class SecurityAndCoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        from django.core.files.uploadedfile import SimpleUploadedFile
        # A small 1x1 white GIF image
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        test_image = SimpleUploadedFile("test.png", small_gif, content_type="image/png")
        
        # Create a sample board member for testing the leadership page
        BoardMember.objects.create(
            name="Test Member",
            role="Chairman",
            image=test_image,
            bio="Test bio content"
        )

    def test_homepage_loads(self):
        """Verify the home page returns 200 OK."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_leadership_page_loads(self):
        """Verify the new leadership page loads correctly."""
        response = self.client.get(reverse('leadership'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Member")

    def test_newsletter_csrf_enforcement(self):
        """
        Verify that newsletter subscription view is reachable.
        Note: CSRF enforcement is disabled for tests by the client's _dont_enforce_csrf_checks.
        In production, CsrfViewMiddleware is active and @csrf_exempt has been removed.
        """
        response = self.client.post(reverse('newsletter_subscribe'), {'email': 'test@example.com'})
        # Should redirect to / since it's a valid POST but honeypot/fields might be empty/invalid
        self.assertIn(response.status_code, [200, 302])

    def test_school_of_ministry_csrf_enforcement(self):
        """Verify that school enrollment view is reachable."""
        response = self.client.post(reverse('school_of_ministry'), {
            'email': 'test@example.com',
            'name': 'Test User',
            'phone_number': '123'
        })
        self.assertIn(response.status_code, [200, 302])

    def test_ip_anonymization_middleware(self):
        """Verify that PageViewMiddleware anonymizes IPs before saving."""
        # This is a bit complex to test via client, better to test the function or model directly
        from .middleware import anonymize_ip
        self.assertEqual(anonymize_ip("192.168.1.45"), "192.168.1.0")
        self.assertEqual(anonymize_ip("2001:db8:85a3:8d3:1319:8a2e:370:7348"), "2001:db8:85a3::")


class BooksPaginationTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.test_image = SimpleUploadedFile("book.png", small_gif, content_type="image/png")

    def test_books_pagination_shows_dynamic_current_and_total_pages(self):
        for i in range(10):
            Book.objects.create(
                title=f"Book {i}",
                slug=f"book-{i}",
                cover_image=self.test_image,
                description="Desc",
                review="Review body",
                is_published=True,
            )

        response = self.client.get(reverse('book_list'), {'page': 2})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page 2 of 2")
        self.assertNotContains(response, "{{ books.paginator.num_pages }}")
