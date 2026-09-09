from django.test import SimpleTestCase

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
