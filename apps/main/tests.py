from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from main.models import SiteSettings

from proj.config import dev, prod


class DeploymentSecuritySettingsTests(SimpleTestCase):
    def test_production_requires_https(self):
        self.assertFalse(prod.DEBUG)
        self.assertTrue(prod.HTTP_ROOT.startswith('https://'))
        self.assertTrue(prod.SESSION_COOKIE_SECURE)
        self.assertTrue(prod.CSRF_COOKIE_SECURE)
        self.assertTrue(prod.SECURE_SSL_REDIRECT)
        self.assertGreater(prod.SECURE_HSTS_SECONDS, 0)
        self.assertTrue(prod.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertFalse(prod.SECURE_HSTS_PRELOAD)
        self.assertTrue(
            all(origin.startswith('https://') for origin in prod.CSRF_TRUSTED_ORIGINS)
        )

    def test_development_supports_local_http(self):
        self.assertTrue(dev.DEBUG)
        self.assertTrue(dev.HTTP_ROOT.startswith('http://'))
        self.assertFalse(dev.SESSION_COOKIE_SECURE)
        self.assertFalse(dev.CSRF_COOKIE_SECURE)


class HomePageTests(TestCase):
    def setUp(self):
        self.site = SiteSettings.objects.create(
            title='Sacred Heart Forms',
            icon='/static/main/site/img/favicon.png',
            banner_bg_color='#123456',
            banner_fg_color='#ffffff',
        )

    def test_home_page_displays_default_form_link(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OCIA Participant Form')
        self.assertContains(response, reverse('OCIAParticipantEntryView'))

    def test_home_page_displays_configured_html(self):
        self.site.home_page_content = (
            '<h2>Choose a form</h2><a href="/example/">Example</a>'
        )
        self.site.save()

        response = self.client.get(reverse('home'))

        self.assertContains(response, '<h2>Choose a form</h2>', html=True)
        self.assertContains(response, '<a href="/example/">Example</a>', html=True)
        self.assertNotContains(response, 'OCIA Participant Form')
