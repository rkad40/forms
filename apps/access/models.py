import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class AdminInvite(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField()
    token_hash = models.CharField(max_length=64)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="admin_invites_sent",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.email

    def is_usable(self):
        return self.is_valid and self.used_at is None and self.expires_at > timezone.now()
