from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
import lib.util as util

class SiteSettings(models.Model):
    title = models.CharField(verbose_name='Title')
    icon = models.CharField(verbose_name='Icon')
    banner_bg_color = models.CharField(verbose_name='Banner Background Color')
    banner_fg_color = models.CharField(verbose_name='Banner Foreground Color')
    home_page_content = models.TextField(
        verbose_name='Home Page Content',
        blank=True,
        help_text='Content displayed on the public home page.',
    )

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


class HomePageLink(models.Model):
    class Visibility(models.IntegerChoices):
        EVERYONE = 0, "Everyone"
        STAFF = 1, "Staff"
        ADMIN = 2, "Admin"

    site_settings = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="home_page_links",
    )
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    url = models.CharField(
        max_length=500,
        help_text="Use a root-relative path such as /ocia/participant/ or a full URL.",
    )
    rank = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        db_index=True,
    )
    verbosity = models.PositiveSmallIntegerField(
        choices=Visibility.choices,
        default=Visibility.EVERYONE,
        help_text="Minimum access level required to show this link.",
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("rank", "title", "pk")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(verbosity__gte=0, verbosity__lte=2),
                name="main_homepagelink_valid_verbosity",
            ),
        ]

    def __str__(self):
        return self.title
