from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Email backend is configured via EMAIL_BACKEND in .env / base settings
# (defaults to SMTP so OTP emails are actually sent during development).
