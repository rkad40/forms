from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import MediaFile, MediaFolder, MediaFolderPolicy #, MediaExplorer

# @admin.register(MediaExplorer)
# class MediaExplorerAdmin(admin.ModelAdmin):
    # list_display_links = None

class MediaExplorerProxy(MediaFolder):  # Or any model from your app
    class Meta:
        proxy = True
        verbose_name = "Media Explorer"
        verbose_name_plural = "Media Explorer"

    
class MediaExplorerAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False  # This hides the "Add" button

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.redirect_view))
        ]
        return custom_urls + urls

    def redirect_view(self, request):
        return redirect('maven-explorer-root')  # Your custom view
        # return redirect('/admin/maven/mediaexplorer/')  # Your custom view

admin.site.register(MediaExplorerProxy, MediaExplorerAdmin)
    
@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'created_on', 'created_by', 'is_active']
    list_display_links = ['id', 'url']
    ordering = ['url']
    fields = ['name', 'url', 'created_by', 'updated_by', 'updated_on', 'is_active', 'notes']
    readonly_fields = ['name', 'url']

@admin.register(MediaFolder)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'created_on', 'created_by', 'is_active']
    list_display_links = ['id', 'url']
    ordering = ['url']
    fields = ['name', 'url', 'hint', 'policy', 'created_by', 'is_active', 'notes']
    readonly_fields = ['name', 'url', 'ancestor_folders', 'child_folders']

@admin.register(MediaFolderPolicy)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']
    ordering = ['name']