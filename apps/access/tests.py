from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminAuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="administrator",
            email="admin@example.com",
            password="correct-horse-battery-staple",
            is_staff=True,
        )

    def test_admin_redirects_to_custom_login(self):
        response = self.client.get(reverse("admin:index"))
        self.assertRedirects(response, f"{reverse('admin_login')}?next={reverse('admin:index')}")

    def test_successful_login_redirects_to_admin(self):
        response = self.client.post(
            reverse("admin_login"),
            {"username": self.user.username, "password": "correct-horse-battery-staple"},
        )
        self.assertRedirects(response, reverse("admin:index"))

    def test_non_staff_user_cannot_login(self):
        user = get_user_model().objects.create_user("member", password="a-safe-password")
        response = self.client.post(
            reverse("admin_login"),
            {"username": user.username, "password": "a-safe-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_password_reset_sends_link_to_staff_user(self):
        response = self.client.post(reverse("password_reset"), {"email": self.user.email})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/admin/reset/", mail.outbox[0].body)

    def test_password_reset_does_not_email_non_staff_user(self):
        get_user_model().objects.create_user(
            "member-with-email",
            email="member@example.com",
            password="a-safe-password",
        )
        response = self.client.post(
            reverse("password_reset"), {"email": "member@example.com"}
        )
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(mail.outbox, [])


class EmailModeTests(TestCase):
    def test_email_backend_matches_debug_mode(self):
        expected_backend = (
            "django.core.mail.backends.console.EmailBackend"
            if settings.DEBUG
            else "django.core.mail.backends.smtp.EmailBackend"
        )
        self.assertEqual(
            settings.EMAIL_BACKEND,
            expected_backend,
        )
