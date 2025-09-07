from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'banner_bg_color', 'banner_fg_color')

    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not SiteSettings.objects.exists()

    def changelist_view(self, request, extra_context=None):
        # Redirect to edit view if instance exists
        obj = SiteSettings.objects.first()
        if obj:
            return HttpResponseRedirect(reverse('admin:main_sitesettings_change', args=[obj.id]))
        return super().changelist_view(request, extra_context)