from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .forms import AdminAuthenticationForm, AdminPasswordResetForm


urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=AdminAuthenticationForm,
            template_name="access/login.html",
            next_page=reverse_lazy("admin:index"),
        ),
        name="admin_login",
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
