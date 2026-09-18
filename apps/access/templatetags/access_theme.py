from django import template

from main.models import SiteSettings
from lib import util
from types import SimpleNamespace


register = template.Library()


@register.simple_tag
def access_site_settings():
    site = SiteSettings.objects.first()
    if site is None:
        return SimpleNamespace(
            banner_bg_color="#8b1e2d",
            banner_fg_color="#ffffff",
            primary_bg_color_10="#731925",
        )
    site.primary_bg_color_10 = util.color_variant(site.banner_bg_color, 10)
    return site
