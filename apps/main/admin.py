from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django_summernote.admin import SummernoteModelAdmin
from .models import HomePageLink, SiteSettings


class HomePageLinkInline(admin.TabularInline):
    model = HomePageLink
    extra = 1
    fields = ('rank', 'title', 'description', 'url', 'verbosity', 'active')

@admin.register(SiteSettings)
class SiteSettingsAdmin(SummernoteModelAdmin):
    list_display = ('title', 'icon', 'banner_bg_color', 'banner_fg_color')
    summernote_fields = ('home_page_content',)
    inlines = (HomePageLinkInline,)

    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not SiteSettings.objects.exists()

    def changelist_view(self, request, extra_context=None):
        # Redirect to edit view if instance exists
        obj = SiteSettings.objects.first()
        if obj:
            return HttpResponseRedirect(reverse('admin:main_sitesettings_change', args=[obj.id]))
        return super().changelist_view(request, extra_context)
