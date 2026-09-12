from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import AdminInvite
from .email import email_backend_for_debug


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminAuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin@example.com",
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
        self.assertRedirects(response, reverse("access_actions"))

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
        self.assertEqual(
            email_backend_for_debug(True),
            "django.core.mail.backends.console.EmailBackend",
        )
        self.assertEqual(
            email_backend_for_debug(False),
            "django.core.mail.backends.smtp.EmailBackend",
        )


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminActionsTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="staff@example.com",
            email="staff@example.com",
            password="a-safe-password",
            is_staff=True,
        )
        self.admin = get_user_model().objects.create_superuser(
            username="owner@example.com",
            email="owner@example.com",
            password="a-safe-password",
        )

    def test_actions_require_login(self):
        response = self.client.get(reverse("access_actions"))
        self.assertRedirects(
            response,
            f"{reverse('admin_login')}?next={reverse('access_actions')}",
        )

    def test_staff_actions_do_not_show_admin_invite(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("access_actions"))
        self.assertContains(response, "Go to Admin Dashboard")
        self.assertNotContains(response, "Send Admin Invite")

    def test_updating_email_also_updates_username(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("access_update_information"),
            {
                "first_name": "Pat",
                "last_name": "Staff",
                "email": "new.staff@example.com",
            },
        )
        self.assertRedirects(response, reverse("access_actions"))
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.email, "new.staff@example.com")
        self.assertEqual(self.staff.username, "new.staff@example.com")

    def test_staff_cannot_send_admin_invite(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("send_admin_invite"))
        self.assertEqual(response.status_code, 403)

    def test_admin_invite_creates_superuser_and_is_single_use(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("send_admin_invite"),
            {"email": "new.admin@example.com"},
        )
        self.assertRedirects(response, reverse("access_actions"))
        self.assertEqual(len(mail.outbox), 1)
        invite = AdminInvite.objects.get(email="new.admin@example.com")
        invite_path = mail.outbox[0].body.splitlines()[3]

        self.client.logout()
        response = self.client.get(invite_path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "new.admin@example.com")
        response = self.client.post(
            invite_path,
            {
                "first_name": "New",
                "last_name": "Admin",
                "password1": "another-safe-password-934",
                "password2": "another-safe-password-934",
            },
        )
        self.assertRedirects(response, reverse("admin_login"))
        user = get_user_model().objects.get(username="new.admin@example.com")
        self.assertEqual(user.email, user.username)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        invite.refresh_from_db()
        self.assertIsNotNone(invite.used_at)

        self.assertEqual(self.client.get(invite_path).status_code, 404)
