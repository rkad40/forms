from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm


class AdminAuthenticationForm(AuthenticationForm):
    """Only allow active staff members into the administration site."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise self.get_invalid_login_error()


class AdminPasswordResetForm(PasswordResetForm):
    """Send reset links only for active staff accounts."""

    def get_users(self, email):
        return (user for user in super().get_users(email) if user.is_staff)
