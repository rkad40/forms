DEBUG = False
HTTP_ROOT = 'https://kadura.net'
ALLOWED_HOSTS = ['kadura.net', 'www.kadura.net']
CSRF_TRUSTED_ORIGINS = ['https://kadura.net', 'https://www.kadura.net']
ADMINS = [
   ('Rodney Kadura', 'rkad40@yahoo.com')
]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
