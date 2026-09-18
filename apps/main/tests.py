from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from main.models import HomePageLink, SiteSettings

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
        self.public_link = HomePageLink.objects.create(
            site_settings=self.site,
            title='OCIA Participant Form',
            description='Open the participant form.',
            url=reverse('OCIAParticipantEntryView'),
            rank=20,
        )

    def test_home_page_displays_configured_link(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.site.title)
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
        self.assertContains(response, 'OCIA Participant Form')

    def test_links_are_ordered_by_rank_and_inactive_links_are_hidden(self):
        HomePageLink.objects.create(
            site_settings=self.site,
            title='First Link',
            url='/first/',
            rank=10,
        )
        HomePageLink.objects.create(
            site_settings=self.site,
            title='Inactive Link',
            url='/inactive/',
            rank=1,
            active=False,
        )

        response = self.client.get(reverse('home'))
        content = response.content.decode()

        self.assertLess(content.index('First Link'), content.index('OCIA Participant Form'))
        self.assertNotContains(response, 'Inactive Link')

    def test_link_visibility_matches_user_access_level(self):
        HomePageLink.objects.create(
            site_settings=self.site,
            title='Staff Link',
            url='/staff/',
            verbosity=HomePageLink.Visibility.STAFF,
        )
        HomePageLink.objects.create(
            site_settings=self.site,
            title='Admin Link',
            url='/admin-only/',
            verbosity=HomePageLink.Visibility.ADMIN,
        )
        staff = get_user_model().objects.create_user(
            username='staff@example.com',
            password='safe-password',
            is_staff=True,
        )
        administrator = get_user_model().objects.create_superuser(
            username='admin@example.com',
            password='safe-password',
        )

        response = self.client.get(reverse('home'))
        self.assertNotContains(response, 'Staff Link')
        self.assertNotContains(response, 'Admin Link')

        self.client.force_login(staff)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Staff Link')
        self.assertNotContains(response, 'Admin Link')

        self.client.force_login(administrator)
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Staff Link')
        self.assertContains(response, 'Admin Link')

    def test_django_admin_return_link_targets_admin_actions(self):
        administrator = get_user_model().objects.create_superuser(
            username='owner@example.com',
            password='safe-password',
        )
        self.client.force_login(administrator)

        response = self.client.get(reverse('admin:index'))

        self.assertContains(response, 'href="/admin/actions/"')
