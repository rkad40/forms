from django.db import models
from django.core.exceptions import ValidationError
import lib.util as util

class SiteSettings(models.Model):
    title = models.CharField(verbose_name='Title')
    icon = models.CharField(verbose_name='Icon')
    banner_bg_color = models.CharField(verbose_name='Banner Background Color')
    banner_fg_color = models.CharField(verbose_name='Banner Foreground Color')

    def clean(self):
        if SiteSettings.objects.exclude(id=self.id).exists():
            raise ValidationError("Only one SiteSettings instance is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Enforce singleton validation
        super().save(*args, **kwargs)

    @classmethod
    def fetch(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        setattr(obj, 'primary_bg_color', obj.banner_bg_color)
        setattr(obj, 'primary_bg_color_10', util.color_variant(obj.banner_bg_color, 10))
        setattr(obj, 'primary_bg_color_20', util.color_variant(obj.banner_bg_color, 20))
        setattr(obj, 'primary_fg_color', obj.banner_fg_color)
        return obj
        
    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
