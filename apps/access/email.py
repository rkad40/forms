def email_backend_for_debug(debug):
    if debug:
        return "django.core.mail.backends.console.EmailBackend"
    return "django.core.mail.backends.smtp.EmailBackend"
