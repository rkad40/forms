from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from main.models import SiteSettings
from ocia_participant.models import (
    OCIAParticipant,
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
