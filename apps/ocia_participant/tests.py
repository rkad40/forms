from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from main.models import SiteSettings
from ocia_participant.models import OCIAParticipantSettings

def add_session_to_request(request):
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

class NavigationViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        SiteSettings.objects.create(
            pk=1,
            title="Test Site",
            icon="test-icon.png",
            banner_bg_color="#ffffff",
            banner_fg_color="#000000"
        )

        OCIAParticipantSettings.objects.create(
            pk=1,
            access_code='pray247',
            liturgical_year='2025-26',
            enable_editing=True
        )

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('OCIAParticipantNavigationView'))
        self.assertRedirects(response, reverse('OCIAParticipantErrorView'))

class StartViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.objects.create(
            pk=1,
            title="Test Site",
            icon="test-icon.png",
            banner_bg_color="#ffffff",
            banner_fg_color="#000000"
        )
        OCIAParticipantSettings.objects.create(
            pk=1, 
            access_code='pray247', 
            liturgical_year='2025-26', 
            enable_editing=True
        )

    def test_redirects_to_login(self):
        response = self.client.get(reverse('OCIAParticipantStartView'))
        self.assertRedirects(response, reverse('OCIAParticipantLoginView'))

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_view_get(self):
        response = self.client.get(reverse('OCIAParticipantLoginView'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ocia/ocia-participant-login-page.html')
        self.assertIn('form', response.context)

class ErrorViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_error_message_displayed(self):
        session = self.client.session
        session['participant_error_message'] = 'Test error'
        session.save()
        response = self.client.get(reverse('OCIAParticipantErrorView'))
        self.assertContains(response, 'Test error')

class NavigationViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('OCIAParticipantNavigationView'))
        self.assertRedirects(response, reverse('OCIAParticipantErrorView'))

from ocia_participant.views import validate_email

class EmailValidationTests(TestCase):
    def test_valid_email(self):
        self.assertTrue(validate_email('test@example.com'))

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            validate_email('invalid-email')

