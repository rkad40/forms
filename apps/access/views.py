import hashlib
import logging
import secrets
from datetime import timedelta
from hmac import compare_digest

from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail, send_mass_mail
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import (
    AdminAuthenticationForm,
    AdminInviteForm,
    NewAdminForm,
    UserInformationForm,
)
from .models import AdminInvite


logger = logging.getLogger(__name__)


def _token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _require_staff(request):
    if not request.user.is_active or not request.user.is_staff:
        raise PermissionDenied


class AccessLoginView(LoginView):
    authentication_form = AdminAuthenticationForm
    template_name = "access/login.html"

    def get_success_url(self):
        return reverse("access_actions")

    def form_valid(self, form):
        response = super().form_valid(form)
        self._notify_admins_of_first_login()
        return response

    def _notify_admins_of_first_login(self):
        try:
            with transaction.atomic():
                invite = (
                    AdminInvite.objects.select_for_update()
                    .filter(
                        accepted_user=self.request.user,
                        used_at__isnull=False,
                        first_login_notified_at__isnull=True,
                    )
                    .first()
                )
                if invite is None:
                    return
                admin_emails = list(
                    get_user_model()
                    .objects.filter(
                        is_active=True,
                        is_superuser=True,
                    )
                    .exclude(email="")
                    .values_list("email", flat=True)
                    .distinct()
                )
                name = self.request.user.get_full_name() or self.request.user.email
                messages_to_send = tuple(
                    (
                        "New Sacred Heart Forms staff member signed in",
                        (
                            f"{name} ({self.request.user.email}) signed in for the "
                            "first time after accepting an invitation."
                        ),
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                    )
                    for email in admin_emails
                )
                if messages_to_send:
                    send_mass_mail(messages_to_send)
                invite.first_login_notified_at = timezone.now()
                invite.save(update_fields=("first_login_notified_at",))
        except Exception:
            # A notification failure must not prevent a valid staff login. Leaving
            # the timestamp empty allows the next login to retry delivery.
            logger.exception("Unable to notify administrators of a first staff login.")


@login_required
def actions(request):
    _require_staff(request)
    return render(request, "access/actions.html")


@login_required
def update_information(request):
    _require_staff(request)
    form = UserInformationForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your information has been updated.")
        return redirect("access_actions")
    return render(request, "access/update_information.html", {"form": form})


@login_required
def send_admin_invite(request):
    _require_staff(request)
    if not request.user.is_superuser:
        raise PermissionDenied

    form = AdminInviteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        token = secrets.token_urlsafe(32)
        with transaction.atomic():
            AdminInvite.objects.filter(
                email__iexact=email, used_at__isnull=True, is_valid=True
            ).update(is_valid=False)
            invite = AdminInvite.objects.create(
                email=email,
                token_hash=_token_hash(token),
                invited_by=request.user,
                expires_at=timezone.now() + timedelta(hours=48),
            )
        invite_url = request.build_absolute_uri(
            reverse(
                "admin_invite_accept",
                kwargs={"uid": invite.uid, "token": token},
            )
        )
        send_mail(
            "Sacred Heart Forms administrator invitation",
            (
                "You have been invited to administer Sacred Heart Forms.\n\n"
                f"Create your account using this one-time link:\n{invite_url}\n\n"
                "This link expires in 48 hours."
            ),
            None,
            [email],
        )
        messages.success(request, f"An administrator invitation was created for {email}.")
        return redirect("access_actions")
    return render(request, "access/send_admin_invite.html", {"form": form})


def accept_admin_invite(request, uid, token):
    invite = get_object_or_404(AdminInvite, uid=uid)
    if not invite.is_usable() or not compare_digest(invite.token_hash, _token_hash(token)):
        raise Http404("This administrator invitation is invalid or has expired.")

    form = NewAdminForm(
        request.POST or None,
        invited_email=invite.email,
    )
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            invite = AdminInvite.objects.select_for_update().get(pk=invite.pk)
            if not invite.is_usable() or not compare_digest(
                invite.token_hash, _token_hash(token)
            ):
                raise Http404("This administrator invitation is invalid or has expired.")
            email = invite.email.strip().lower()
            if get_user_model().objects.filter(
                Q(username__iexact=email) | Q(email__iexact=email)
            ).exists():
                raise Http404("This administrator invitation is no longer available.")
            user = get_user_model().objects.create_user(
                username=email,
                email=email,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                password=form.cleaned_data["password1"],
                is_staff=True,
                is_superuser=False,
            )
            invite.accepted_user = user
            invite.used_at = timezone.now()
            invite.is_valid = False
            invite.save(update_fields=("accepted_user", "used_at", "is_valid"))
        messages.success(request, "Your staff account is ready. Please log in.")
        return redirect("admin_login")
    return render(request, "access/accept_admin_invite.html", {"form": form})
