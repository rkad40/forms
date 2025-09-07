from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils import timezone

import fs

# class MediaExplorer(models.Model):
    # name = models.CharField(verbose_name="Name", max_length=100, default="")
    # class Meta:
        # # managed = True    
        # verbose_name_plural = "Media explorer" 

class MediaFolderPolicy(models.Model):
    class Meta:
        verbose_name_plural = "Media folder policies (group permissions)"    
    name = models.CharField(verbose_name="Name", max_length=100, null=False)
    contrib_groups = models.ManyToManyField(Group, verbose_name="Contributor Groups", 
        related_name="media_folder_contrib_groups", blank=True)
    editor_groups = models.ManyToManyField(Group, verbose_name="Editor Groups", 
        related_name="media_folder_editor_groups", blank=True)
    admin_groups = models.ManyToManyField(Group, verbose_name="Admin Groups", 
        related_name="media_folder_admin_groups", blank=True)
    visitors_can_view = models.BooleanField(verbose_name="Visitors can view?", default=True)
    # superusers_are_admins = models.BooleanField(verbose_name="Superusers are admins?", default=True)
    notes = models.TextField(verbose_name="Notes", null=False, blank=True, default='')
    def __str__(self): return self.name

class MediaFolder(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100, null=False, blank=True, default="")
    url = models.CharField(verbose_name="URL", max_length=250, null=False, unique=True, blank=True)
    ancestor_folders = models.ManyToManyField("self", symmetrical=False, blank=True,
        related_name="ancestors_backref")
    child_folders = models.ManyToManyField("self", symmetrical=False, blank=True, 
        related_name="children_backref")
    policy = models.ForeignKey('MediaFolderPolicy', verbose_name="Policy", on_delete=models.CASCADE, 
        related_name="policy", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Created by", 
        on_delete=models.CASCADE, related_name="media_folders_created", null=True, blank=True)
    created_on = models.DateTimeField(verbose_name="Created on", null=False, auto_now_add=True)
    is_active = models.BooleanField(verbose_name="Is active?", default=True)
    hint = models.CharField(verbose_name="Hint", max_length=200, null=False, blank=True, default='')
    notes = models.TextField(verbose_name="Notes", null=False, blank=True, default='')
    def __str__(self): return self.url

    def save(self, *args, **kwargs):

        ## Call the standard save() first.  We need an ID to then add ancestor_folders.   
        super(MediaFolder, self).save(*args, **kwargs)

        ## Add parent URLs to self.ancestor_folders.  
        url_parts = self.url.split("/")
        url_parts.pop()
        parent_url = ""
        while url_parts:
            parent_url = "/".join(url_parts)
            inst = MediaFolder.objects.get(url=parent_url)
            self.ancestor_folders.add(inst)
            url_parts.pop()

        ## Add the top level URL (which is "")
        if self.url != "":
            inst = MediaFolder.objects.get(url="")
            self.ancestor_folders.add(inst)

    def get_perm(self):
        pass

    def get_fs_path(self):
        fixed_abs_root = fs.get_abs_path(fs.fix_path_name(settings.MEDIA_ROOT))
        return(fs.fix_path_name(fs.join_names(fixed_abs_root, self.url)))

    @staticmethod
    def fs_path_to_url(path):
        fixed_abs_path = fs.get_abs_path(fs.fix_path_name(path))
        fixed_abs_root = fs.get_abs_path(fs.fix_path_name(settings.MEDIA_ROOT))
        return fs.get_unix_path(fs.get_rel_path(fixed_abs_path, fixed_abs_root))

    @staticmethod
    def url_to_fs_path(url):
        fixed_abs_root = fs.get_abs_path(fs.fix_path_name(settings.MEDIA_ROOT))
        return(fs.fix_path_name(fs.join_names(fixed_abs_root, url)))

class MediaFile(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100, null=False)
    url = models.CharField(verbose_name="URL", max_length=250, null=False, unique=True, blank=False)
    folder = models.ForeignKey('MediaFolder', on_delete=models.CASCADE, related_name="files")
    size = models.IntegerField(verbose_name="Size", null=False, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Created by", 
        on_delete=models.CASCADE, related_name="media_files_created", null=True, blank=True)
    created_on = models.DateTimeField(verbose_name="Created on", null=False, auto_now_add=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Updated by", 
        on_delete=models.CASCADE, related_name="media_files_updated", null=True, blank=True)
    updated_on = models.DateTimeField(verbose_name="Updated on", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="Is active?", default=True)
    notes = models.TextField(verbose_name="Notes", null=False, blank=True, default='')
    def __str__(self): return self.url

    @staticmethod
    def fs_path_to_url(path):
        fixed_abs_path = fs.get_abs_path(fs.fix_path_name(path))
        fixed_abs_root = fs.get_abs_path(fs.fix_path_name(settings.MEDIA_ROOT))
        return fs.get_unix_path(fs.get_rel_path(fixed_abs_path, fixed_abs_root))

    @staticmethod
    def url_to_fs_path(url):
        fixed_abs_root = fs.get_abs_path(fs.fix_path_name(settings.MEDIA_ROOT))
        return(fs.fix_path_name(fs.join_names(fixed_abs_root, url)))

    @staticmethod
    def file_size_kb(size_bytes):
        if size_bytes == 0: return '0 KB'
        if size_bytes < 1024: return '1 KB'
        size_bytes = size_bytes / 1024
        if size_bytes > int(size_bytes): size_bytes += 1
        size_bytes = int(size_bytes)
        return f'{size_bytes:,} KB'    

