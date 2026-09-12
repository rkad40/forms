from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.db.models import Q


class AdminAuthenticationForm(AuthenticationForm):
    """Only allow active staff members into the administration site."""

    username = forms.EmailField(
        label="Email", max_length=150, widget=forms.EmailInput()
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise self.get_invalid_login_error()


class AdminPasswordResetForm(PasswordResetForm):
    """Send reset links only for active staff accounts."""

    def get_users(self, email):
        return (user for user in super().get_users(email) if user.is_staff)


class UserInformationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        username_max_length = get_user_model()._meta.get_field("username").max_length
        if len(email) > username_max_length:
            raise forms.ValidationError(
                f"Email addresses must be {username_max_length} characters or fewer."
            )
        users = get_user_model().objects.exclude(pk=self.instance.pk)
        if users.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
            raise forms.ValidationError("An account already uses this email address.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


class AdminInviteForm(forms.Form):
    email = forms.EmailField(label="New administrator email", max_length=150)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).exists():
            raise forms.ValidationError("An account already uses this email address.")
        return email


class NewAdminForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(disabled=True)
    password1 = forms.CharField(
        label="Password", strip=False, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirm password", strip=False, widget=forms.PasswordInput
    )

    def __init__(self, *args, invited_email, **kwargs):
        super().__init__(*args, **kwargs)
        self.invited_email = invited_email
        self.fields["email"].initial = invited_email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "The two passwords do not match.")
        if password1:
            candidate = get_user_model()(
                username=self.invited_email,
                email=self.invited_email,
                first_name=cleaned_data.get("first_name", ""),
                last_name=cleaned_data.get("last_name", ""),
            )
            password_validation.validate_password(password1, candidate)
        return cleaned_data
