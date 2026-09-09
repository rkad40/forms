from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.core import mail
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlparse
import re
from main.models import SiteSettings
from ocia_participant.forms import OCIAParticipantForm
from ocia_participant.models import (
    OCIAParticipant,
    OCIAParticipantAccessToken,
    OCIAParticipantEngagement,
    OCIAParticipantMarriage,
    OCIAParticipantParent,
    OCIAParticipantSettings,
)

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
        SiteSettings.objects.create(
            pk=1,
            title="Test Site",
            icon="test-icon.png",
            banner_bg_color="#ffffff",
            banner_fg_color="#000000",
        )
        OCIAParticipantSettings.objects.create(
            pk=1,
            access_code="pray247",
            liturgical_year="2025-26",
            enable_editing=True,
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('OCIAParticipantLoginView'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ocia/ocia-participant-login-page.html')
        self.assertIn('form', response.context)


class ErrorViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.objects.create(
            pk=1,
            title="Test Site",
            icon="test-icon.png",
            banner_bg_color="#ffffff",
            banner_fg_color="#000000",
        )

    def test_error_message_displayed(self):
        session = self.client.session
        session['participant_error_message'] = 'Test error'
        session.save()
        response = self.client.get(reverse('OCIAParticipantErrorView'))
        self.assertContains(response, 'Test error')


class NavigationWithoutSessionViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.objects.create(
            pk=1,
            title="Test Site",
            icon="test-icon.png",
            banner_bg_color="#ffffff",
            banner_fg_color="#000000",
        )
        OCIAParticipantSettings.objects.create(
            pk=1,
            access_code="pray247",
            liturgical_year="2025-26",
            enable_editing=True,
        )

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

class ParticipantDeleteRecordTests(TestCase):
    def setUp(self):
        self.client = Client()
        SiteSettings.objects.create(
            pk=1,
            title="Test Site",
            icon="test-icon.png",
            banner_bg_color="#ffffff",
            banner_fg_color="#000000",
        )
        OCIAParticipantSettings.objects.create(
            pk=1,
            access_code="pray247",
            liturgical_year="2025-26",
            enable_editing=True,
        )
        self.participant = OCIAParticipant.objects.create(
            first_name="Alice",
            last_name="Participant",
            email="alice@example.com",
            liturgical_year="2025-26",
        )
        self.other_participant = OCIAParticipant.objects.create(
            first_name="Bob",
            last_name="Participant",
            email="bob@example.com",
            liturgical_year="2025-26",
        )
        self._login_as(self.participant)

    def _login_as(self, participant):
        session = self.client.session
        session["participant_id"] = participant.id
        session.save()

    def _delete_url(self, category, record):
        return reverse(
            "OCIAParticipantDeleteRecordView",
            kwargs={"category": category, "id": record.id},
        )

    def test_participant_can_delete_own_records(self):
        records = (
            ("marriage", OCIAParticipantMarriage.objects.create(participant=self.participant)),
            ("engagement", OCIAParticipantEngagement.objects.create(participant=self.participant)),
            ("parent", OCIAParticipantParent.objects.create(participant=self.participant)),
        )

        for category, record in records:
            with self.subTest(category=category):
                response = self.client.post(self._delete_url(category, record))
                self.assertRedirects(response, reverse("OCIAParticipantNavigationView"))
                self.assertFalse(type(record).objects.filter(pk=record.pk).exists())

    def test_participant_cannot_delete_another_participants_records(self):
        records = (
            ("marriage", OCIAParticipantMarriage.objects.create(participant=self.other_participant)),
            ("engagement", OCIAParticipantEngagement.objects.create(participant=self.other_participant)),
            ("parent", OCIAParticipantParent.objects.create(participant=self.other_participant)),
        )

        for category, record in records:
            with self.subTest(category=category):
                response = self.client.post(self._delete_url(category, record))
                self.assertEqual(response.status_code, 404)
                self.assertTrue(type(record).objects.filter(pk=record.pk).exists())

    def test_delete_requires_post(self):
        record = OCIAParticipantMarriage.objects.create(participant=self.participant)

        response = self.client.get(self._delete_url("marriage", record))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(OCIAParticipantMarriage.objects.filter(pk=record.pk).exists())

    def test_unknown_category_does_not_delete_record(self):
        record = OCIAParticipantMarriage.objects.create(participant=self.participant)

        response = self.client.post(self._delete_url("unknown", record))

        self.assertRedirects(response, reverse("OCIAParticipantErrorView"))
        self.assertTrue(OCIAParticipantMarriage.objects.filter(pk=record.pk).exists())

    def test_logged_out_request_cannot_delete_record(self):
        record = OCIAParticipantMarriage.objects.create(participant=self.participant)
        self.client = Client()

        response = self.client.post(self._delete_url("marriage", record))

        self.assertRedirects(response, reverse("OCIAParticipantErrorView"))
        self.assertTrue(OCIAParticipantMarriage.objects.filter(pk=record.pk).exists())

    def test_deletion_is_blocked_when_editing_is_disabled(self):
        record = OCIAParticipantMarriage.objects.create(participant=self.participant)
        settings = OCIAParticipantSettings.objects.get(pk=1)
        settings.enable_editing = False
        settings.save()

        response = self.client.post(self._delete_url("marriage", record))

        self.assertRedirects(response, reverse("OCIAParticipantErrorView"))
        self.assertTrue(OCIAParticipantMarriage.objects.filter(pk=record.pk).exists())


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    HTTP_ROOT="https://testserver",
)
class ParticipantAccessTokenTests(TestCase):
    def setUp(self):
        SiteSettings.objects.create(
            pk=1,
            title="Test Site",
            icon="test-icon.png",
            banner_bg_color="#ffffff",
            banner_fg_color="#000000",
        )
        OCIAParticipantSettings.objects.create(
            pk=1,
            access_code="pray247",
            liturgical_year="2025-26",
            enable_editing=True,
        )
        self.participant = OCIAParticipant.objects.create(
            first_name="Alice",
            last_name="Participant",
            email="alice@example.com",
            liturgical_year="2025-26",
        )
        mail.outbox = []

    def _request_link(self, email="alice@example.com"):
        requesting_client = Client()
        response = requesting_client.post(
            reverse("OCIAParticipantLoginView"),
            {"email": email},
        )
        self.assertEqual(response.status_code, 302)
        response = requesting_client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        match = re.search(r"https://testserver\S+", mail.outbox[0].body)
        self.assertIsNotNone(match)
        return urlparse(match.group(0)).path

    def test_existing_participant_can_confirm_in_different_browser(self):
        path = self._request_link()
        access_record = OCIAParticipantAccessToken.objects.get()
        raw_token = path.rstrip("/").split("/")[-1]

        self.assertNotEqual(access_record.token_hash, raw_token)

        receiving_client = Client(enforce_csrf_checks=True)
        response = receiving_client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<meta name="referrer" content="origin">', html=True)

        access_record.refresh_from_db()
        self.assertTrue(access_record.is_valid)
        self.assertIsNone(access_record.used_on)
        self.assertNotIn("participant_id", receiving_client.session)

        response = receiving_client.post(
            path,
            {"csrfmiddlewaretoken": receiving_client.cookies["csrftoken"].value},
            HTTP_ORIGIN="http://testserver",
        )
        self.assertRedirects(response, reverse("OCIAParticipantNavigationView"))

        access_record.refresh_from_db()
        self.assertFalse(access_record.is_valid)
        self.assertIsNotNone(access_record.used_on)
        self.assertEqual(receiving_client.session["participant_id"], self.participant.id)

    def test_used_token_cannot_be_replayed(self):
        path = self._request_link()
        client = Client()
        self.assertEqual(client.get(path).status_code, 200)
        self.assertEqual(client.post(path).status_code, 302)

        response = Client().get(path)
        self.assertRedirects(response, reverse("OCIAParticipantErrorView"))

    def test_tampered_and_expired_tokens_are_rejected(self):
        path = self._request_link()
        tampered_path = path[:-1] + ("a" if path[-1] != "a" else "b")
        response = Client().get(tampered_path)
        self.assertRedirects(response, reverse("OCIAParticipantErrorView"))

        access_record = OCIAParticipantAccessToken.objects.get()
        access_record.expires_on = timezone.now() - timedelta(seconds=1)
        access_record.save(update_fields=["expires_on"])
        response = Client().get(path)
        self.assertRedirects(response, reverse("OCIAParticipantErrorView"))

    def test_new_request_invalidates_previous_unused_token(self):
        first_path = self._request_link()
        mail.outbox = []
        second_path = self._request_link()

        response = Client().get(first_path)
        self.assertRedirects(response, reverse("OCIAParticipantErrorView"))
        self.assertEqual(Client().get(second_path).status_code, 200)

    def test_new_participant_confirmation_authorizes_creation(self):
        path = self._request_link("new@example.com")
        receiving_client = Client()

        self.assertEqual(receiving_client.get(path).status_code, 200)
        response = receiving_client.post(path)
        self.assertRedirects(response, reverse("OCIAParticipantCreateView"))
        self.assertTrue(receiving_client.session["participant_create_enabled"])
        self.assertEqual(receiving_client.session["participant_email"], "new@example.com")

        access_record = OCIAParticipantAccessToken.objects.get()
        self.assertEqual(
            access_record.purpose,
            OCIAParticipantAccessToken.Purpose.NEW,
        )
        self.assertFalse(access_record.is_valid)

    def test_legacy_existing_link_remains_compatible(self):
        client = Client()
        session = client.session
        session["participant_access_code"] = "legacy-code"
        session["participant_id_temp"] = self.participant.id
        session.save()

        response = client.get(
            reverse(
                "OCIAParticipantAccessConfirmationExistingView",
                kwargs={"code": "legacy-code"},
            )
        )

        self.assertRedirects(response, reverse("OCIAParticipantNavigationView"))
        self.assertEqual(client.session["participant_id"], self.participant.id)


class ParticipantEmailIdentityTests(TestCase):
    def test_model_save_normalizes_email(self):
        participant = OCIAParticipant.objects.create(
            first_name="Alice",
            last_name="Participant",
            email="  Alice.Example@Example.COM  ",
        )

        participant.refresh_from_db()
        self.assertEqual(participant.email, "alice.example@example.com")

    def test_database_rejects_normalized_duplicate(self):
        OCIAParticipant.objects.create(
            first_name="Alice",
            last_name="One",
            email="alice@example.com",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                OCIAParticipant.objects.create(
                    first_name="Alice",
                    last_name="Two",
                    email="  ALICE@EXAMPLE.COM ",
                )

    def test_form_rejects_another_participants_email_case_insensitively(self):
        OCIAParticipant.objects.create(
            first_name="Alice",
            last_name="One",
            email="alice@example.com",
        )
        participant = OCIAParticipant.objects.create(
            first_name="Bob",
            last_name="Two",
            email="bob@example.com",
        )
        form = OCIAParticipantForm(
            instance=participant,
            data={
                "first_name": "Bob",
                "last_name": "Two",
                "email": " ALICE@EXAMPLE.COM ",
                "num_marriages": "0",
                "marital_status": "married",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("already exists", form.errors["email"][0])

    def test_form_allows_current_participants_normalized_email(self):
        participant = OCIAParticipant.objects.create(
            first_name="Alice",
            last_name="Participant",
            email="alice@example.com",
        )
        form = OCIAParticipantForm(
            instance=participant,
            data={
                "first_name": "Alice",
                "last_name": "Participant",
                "email": " ALICE@EXAMPLE.COM ",
                "num_marriages": "0",
                "marital_status": "married",
            },
        )

        form.is_valid()
        self.assertNotIn("email", form.errors)
        self.assertEqual(form.cleaned_data["email"], "alice@example.com")
