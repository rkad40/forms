from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .forms import AdminPasswordResetForm
from .views import AccessLoginView, accept_admin_invite, actions, send_admin_invite, update_information


urlpatterns = [
    path(
        "login/",
        AccessLoginView.as_view(),
        name="admin_login",
    ),
    path("actions/", actions, name="access_actions"),
    path("actions/information/", update_information, name="access_update_information"),
    path(
        "actions/password/",
        auth_views.PasswordChangeView.as_view(
            template_name="access/password_change.html",
            success_url=reverse_lazy("access_actions"),
        ),
        name="access_password_change",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("admin_login")),
        name="access_logout",
    ),
    path("invite/", send_admin_invite, name="send_admin_invite"),
    path(
        "invite/<uuid:uid>/<str:token>/",
        accept_admin_invite,
        name="admin_invite_accept",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            form_class=AdminPasswordResetForm,
            template_name="access/password_reset_form.html",
            email_template_name="access/password_reset_email.txt",
            subject_template_name="access/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="access/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="access/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="access/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
