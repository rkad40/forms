import json
import pprint

import fs
from cronos import Time
from dateutil import tz
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import escape_uri_path
from rex import Rex

from maven.models import MediaFile, MediaFolder, MediaFolderPolicy

DEBUG = False

IMAGE_EXT = ['bmp', 'gif', 'ico', 'jpeg', 'jpg', 'png', 'tif', 'tiff']

FILE_EXT = {
    'aif': 'audio', 'cda': 'audio', 'mid': 'audio', 'mp3': 'audio', 'mpa': 'audio', 'ogg': 'audio', 'wav': 'audio', 
    'wma': 'audio', 'wpl': 'audio', '7z': 'zip', 'arj': 'zip', 'deb': 'zip', 'pkg': 'package', 'rar': 'zip', 
    'rpm': 'zip', 'gz': 'zip', 'z': 'zip', 'zip': 'zip', 'csv': 'csv', 'dat': 'data', 'db': 'database', 
    'db3': 'database', 'log': 'text', 'mdb': 'database', 'sav': 'data', 'sql': 'database', 'sqlite': 'database', 
    'tar': 'package', 'xml': 'xml', 'yml': 'yml', 'json': 'json', 'email': 'mail', 'eml': 'mail', 'emlx': 'mail', 
    'msg': 'outlook', 'oft': 'outlook', 'ost': 'outlook', 'pst': 'mail', 'vcf': 'mail', 'apk': 'package', 'bat': 'exe', 
    'bin': 'exe', 'cgi': 'perl', 'pl': 'perl', 'pm': 'perl', 'rb': 'ruby', 'com': 'exe', 'exe': 'exe', 'gadget': 'misc', 
    'jar': 'java', 'msi': 'install', 'py': 'python', 'wsf': 'exe', 'fnt': 'font', 'fon': 'font', 'otf': 'font', 'ttf': 
    'font', 'ai': 'image', 'bmp': 'image', 'gif': 'image', 'ico': 'image', 'jpeg': 'image', 'jpg': 'image', 
    'png': 'image', 'ps': 'image', 'psd': 'image', 'svg': 'image', 'tif': 'image', 'tiff': 'image', 'asp': 'web', 
    'aspx': 'web', 'cer': 'certificate', 'cfm': 'web', 'css': 'css', 'htm': 'html', 'html': 'html', 'js': 'javascript', 
    'jsp': 'web', 'part': 'web', 'php': 'web', 'rss': 'rss', 'xhtml': 'web', 'key': 'presentation', 
    'odp': 'presentation', 'pps': 'powerpoint', 'ppt': 'powerpoint', 'pptx': 'powerpoint', 'c': 'c', 'class': 'java', 
    'cpp': 'c', 'cs': 'c', 'h': 'c', 'java': 'java', 'php': 'text', 'sh': 'exe', 'swift': 'text', 'vba': 'vba', 
    'vb': 'vb', 'ods': 'spreadsheet', 'xls': 'excel', 'xlsm': 'excel', 'xlsx': 'excel', 'xla': 'xla', 'bak': 'bak', 
    'cab': 'misc', 'cfg': 'config', 'cpl': 'config', 'cur': 'misc', 'dll': 'lib', 'dmp': 'data', 'icns': 'image', 
    'ico': 'image', 'ini': 'config', 'lnk': 'link', 'msi': 'install', 'sys': 'prompt', 'tmp': 'misc', '3g2': 
    'video', '3gp': 'video', 'avi': 'video', 'flv': 'video', 'h264': 'video', 'm4v': 'video', 'mkv': 'video', 
    'mov': 'video', 'mp4': 'video', 'mpg': 'video', 'rm': 'video', 'swf': 'video', 'vob': 'video', 'wmv': 'video', 
    'doc': 'word', 'docx': 'word', 'odt': 'document', 'pdf': 'pdf', 'rtf': 'misc', 'txt': 'text', 'wpd': 'document', 
    'misc': 'misc', 'igxl': 'igxl'
}

def file_size_kb(size_bytes):
    if size_bytes == 0: return '0 KB'
    if size_bytes < 1024: return '1 KB'
    size_bytes = size_bytes / 1024
    if size_bytes > int(size_bytes): size_bytes += 1
    size_bytes = int(size_bytes)
    return f'{size_bytes:,} KB'

def get_user_access(user, folder):
    r"""
    Get access level:

    0. Restricted - no access; can see folder tree but not files
    1. Visitor - can browse files
    2. Contributor - can create files and edit them
    3. Editor - can edit files created by any user
    4. Admin - can do anything
    """
    # If user is superuser, policy access level is 4 (highest access level).
    if user is not None and user.is_superuser: return 4
    # Find the folder policy.  If the current folder does not have a policy, search ancestors 
    # beginning with the most recent.  When a folder policy is found, terminate search and use it.
    policy = folder.policy 
    if policy is None:
        for ancestor_folder in folder.ancestor_folders.all().order_by('-url'):
            # if DEBUG: print(ancestor_folder.url)
            policy = ancestor_folder.policy
            if policy is not None: break
    # If no policy is found, superusers have level 4 access and all other users have level 1 
    # access, even visitors.
    if policy is None:
        if user is None or user.is_anonymous: return 1
        if user.is_superuser: return 4
        return 1
    # You can only get here if a folder policy was found.  If user is None, user level is 1 if 
    # the policy allows visitors to view, 0 otherwise.
    if settings.DEBUG: 
        if DEBUG: print(f'User: {user}')
        if DEBUG: print(f'Folder policy: {policy.name}')
    if user is None or user.is_anonymous:
        if policy.visitors_can_view: return 1
        else: return 0
    # Compare user groups agains folder policy admin, editor and contrib groups returning the first
    # level match if one is made.
    if any(group in policy.admin_groups.all() for group in user.groups.all()): return 4
    if any(group in policy.editor_groups.all() for group in user.groups.all()): return 3
    if any(group in policy.contrib_groups.all() for group in user.groups.all()): return 2
    # If no user group matches an admin, editor or contrib group, level is 1.
    return 1

# from datetime import datetime
# import time

# def datetime_from_utc_to_local(utc_datetime):
#     now_timestamp = time.time()
#     offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
#     return utc_datetime + offset    

def get_folders_recurse(top_folder_path, folder_fs_info_lookup=None):
    folders = fs.get_dirs(top_folder_path)
    media_root = fs.fix_path_name(settings.MEDIA_ROOT)
    if folder_fs_info_lookup is None: 
        folder_fs_info_lookup = {}
        folder_fs_info_lookup[''] = {'name': '', 'path': fs.fix_path_name(top_folder_path), 'url': '', 'parent': None}
    for folder in folders:
        if fs.get_file_name(folder).startswith('.'): continue
        folder = fs.fix_path_name(folder)
        name = fs.get_file_name(folder)
        parent = fs.get_unix_path(fs.get_rel_path(fs.get_dir_name(folder), media_root))
        if parent == ".": parent = ""
        url = fs.get_unix_path(fs.get_rel_path(folder, media_root))
        folder_fs_info_lookup[url] = {'name': name, 'path': folder, 'url': url, 'parent': parent}
        get_folders_recurse(folder, folder_fs_info_lookup)
    return folder_fs_info_lookup

def initialize_media_folders_in_database():
    
    folder_fs_info_lookup = get_folders_recurse(settings.MEDIA_ROOT)
    folder_model_inst = {}

    class count():
        folders_already_in_database = 0
        files_already_in_database = 0
        folders_created = 0
        files_created = 0
        child_folders_linked = 0
        parent_folders_linked = 0

    # Get MediaFolder instances.
    for folder_inst in MediaFolder.objects.all():
        folder_model_inst[folder_inst.url] = folder_inst
        count.folders_already_in_database += 1

    count.files_already_in_database = MediaFile.objects.count()
    
    # Get all media file system folders.  If there is not already a mirror MediaFolder object, 
    # create one.
    for folder_key in sorted(folder_fs_info_lookup.keys()):
        folder_fs_info = folder_fs_info_lookup[folder_key]
        if folder_key in folder_model_inst: continue
        url = folder_fs_info['url']
        if DEBUG: print(f'Creating MediaFolder object for "{url}" ...')
        folder_model_inst[url] = MediaFolder()
        folder_model_inst[url].name = folder_fs_info['name']
        folder_model_inst[url].url = folder_fs_info['url']
        folder_model_inst[url].save()
        count.folders_created += 1

    for parent_folder_inst in MediaFolder.objects.all():
        url = parent_folder_inst.url
        parent_folder_fs_path = parent_folder_inst.get_fs_path()
        child_fs_paths = fs.get_dirs(parent_folder_fs_path)
        for child_fs_path in child_fs_paths:
            name = fs.get_file_name(child_fs_path)
            if name.startswith('.'): continue
            child_url = MediaFolder.fs_path_to_url(child_fs_path)
            child_folder_inst = folder_model_inst[child_url]
            if not child_folder_inst in parent_folder_inst.child_folders.all():
                if DEBUG: print(f'Adding folder "{child_folder_inst.url}" to folder "{parent_folder_inst.url}" ...')
                parent_folder_inst.child_folders.add(child_folder_inst)
                count.child_folders_linked += 1
        file_fs_paths = fs.get_files(parent_folder_fs_path, rec=False)
        for file_fs_path in file_fs_paths:
            name = fs.get_file_name(file_fs_path)
            if name.startswith('.'): continue
            file_url = MediaFile.fs_path_to_url(file_fs_path)
            file_inst = MediaFile.objects.filter(url=file_url).first()
            if file_inst is None:
                if DEBUG: print(f'Creating MavenFile object for "{file_url}" ...')
                file_inst = MediaFile()
                file_inst.url = file_url
                file_inst.name = name
                file_inst.folder = parent_folder_inst
                # modified = fs.last_modified(file_fs_path)
                # modified = timezone.datetime.fromtimestamp(modified)
                file_inst.size = fs.get_size(file_fs_path)
                file_inst.save()
                # Save second time to set the created_on field to the actual file modification time, not the field 
                # default.  
                # file_inst.created_on(modified)
                # file_inst.save()
                count.files_created += 1
            if file_inst.folder is None:
                file_inst.folder = parent_folder_inst
                file_inst.save()
                count.parent_folders_linked += 1
    
    if DEBUG: print('Summary:')
    if DEBUG: print(f'Folders already in database    : {count.folders_already_in_database}')
    if DEBUG: print(f'Files already in database      : {count.files_already_in_database}')
    if DEBUG: print(f'Folders created                : {count.folders_created}')
    if DEBUG: print(f'Files created                  : {count.files_created}')
    if DEBUG: print(f'Child folders linked to parent : {count.child_folders_linked}')

class MavenMedia():

    def __init__(self, offline=False):
        if offline:
            self.settings_media_root = r'C:\Work\TestRequirementsWebProj2\proj\media'
            self.settings_media_url = '/media/'
        else:
            self.settings_media_root = settings.MEDIA_ROOT
            self.settings_media_url = settings.MEDIA_URL
        self.settings_media_root = fs.fix_path_name(self.settings_media_root)
        self.settings_media_url = fs.get_unix_path(self.settings_media_url)

    def __str__(self):
        return f'<MavenMedia "{self.root_url}">'

    def path(self, url, file_type='file', user=None):
        rex = Rex()

        unix_root_url = fs.get_unix_path(url).lstrip('/')
        sys_root_url = fs.fix_path_name(unix_root_url)

        ## Delcare (and define) instance variables.
        self.sys_abs_path = fs.fix_path_name(fs.join_names(self.settings_media_root, sys_root_url))
        self.root_url = unix_root_url
        self.media_url = self.settings_media_url + self.root_url
        self.parent_url = None
        self.exists = fs.file_exists(self.sys_abs_path)
        self.type = 'file' if fs.is_file(self.sys_abs_path) else 'dir'
        self.access = 0
        self.crumbs = []
        self.dirs = []
        self.files = []
        self.error = None

        ## Query the folder object from the database.
        folder = None
        try:      
            # folder = MediaFolder.objects.select_related('').get(url=url)
            folder = MediaFolder.objects.get(url=url)
        except:
            self.error = f'Directory "{self.root_url}" does not exist.'
            return

        self.access = get_user_access(user, folder)
        if DEBUG: print(f'Access level: {self.access}')

        ## Indicate error if the url does not exist.
        if not self.exists:
            self.error = f'Directory "{self.root_url}" does not exist.'
        
        ## Create self.crumbs list.
        parts = []
        self.has_parent = False
        if len(self.root_url) > 0:
            parts = self.root_url.split('/') 
            self.has_parent = True
        if self.type == 'file': parts.pop()
        dynamic_parts = []
        # if len(parts) > 1:
        for part in parts:
            dynamic_parts.append(part)
            self.crumbs.append(dict(name=part, url='/'.join(dynamic_parts)))
        self.parent_url = ''
        if len(dynamic_parts) > 0: 
            dynamic_parts.pop()
            if len(dynamic_parts) > 0:
                self.parent_url = '/'.join(dynamic_parts)

        ## If url is a directory, process subdirectories and top level files.  
        if self.type == 'dir':
            ## Get dirs ...
            # dirs = list(fs.get_dirs(self.sys_abs_path))

            ## ... and files.
            # files = list(fs.get_files(self.sys_abs_path, rec=False))

            ## Process subdirectories.  Create self.dirs list.
            for child_folder in folder.child_folders.all().order_by('name'):
                if not child_folder.is_active: continue
                obj = {}
                # obj['name'] = fs.get_file_name(dir)
                # if obj['name'].startswith('.'): continue
                # obj['url'] = self.root_url + '/' + obj['name']
                obj['name'] = child_folder.name
                obj['url'] = child_folder.url
                self.dirs.append(obj)

            ## Process files. Create self.files list.
            self.files = []
            # for file in files:
            for folder_file in folder.files.all().order_by('name'):
                if self.access == 0: break
                if not folder_file.is_active: continue

                if file_type == 'image':
                    ext = fs.get_ext(folder_file.name)
                    if ext not in IMAGE_EXT: continue

                obj = {}
                obj['name'] = folder_file.name
                obj['size'] = folder_file.size
                obj['size_str'] = file_size_kb(obj['size'])

                obj['can_edit'] = False
                if self.access >= 3: obj['can_edit'] = True
                if self.access == 2 and user == folder_file.created_by: obj['can_edit'] = True
                
                from_zone = tz.gettz('UTC')
                to_zone = tz.gettz(settings.TIME_ZONE)
                mod_suffix = ''
                if folder_file.updated_on:
                    mod_prefix = "Updated "
                    if folder_file.updated_by: mod_suffix = " by " + str(folder_file.updated_by)
                    utc = folder_file.updated_on
                else:
                    mod_prefix = "Created "
                    if folder_file.created_by: mod_suffix = " by " + str(folder_file.created_by)
                    utc = folder_file.created_on
                utc = utc.replace(tzinfo=from_zone)
                localtime = utc.astimezone(to_zone)
                modified = localtime.strftime("%Y-%m-%d %I:%M %p")
                try:
                    obj['modified'] = Time(modified, fmt="%Y-%m-%d %I:%M %p").to_epoch(int)
                    obj['modified_str'] = mod_prefix + modified + mod_suffix
                except:
                    obj['modified'] = 0
                    obj['modified_str'] = mod_prefix + str(modified) + mod_suffix + ' <i class="fas fa-exclamation-triangle">'

                # utc_time = folder_file.created_on
                # local_time = datetime_from_utc_to_local(utc_time)
                # modified = local_time.strftime("%Y-%m-%d %H:%M:%S")

                # obj['modified'] = folder_file.created_on.strftime("%Y-%m-%d %H:%M:%S")
                # t = Time(obj['modified'], fmt=r"%m/%d/%Y %I:%M %p")
                # obj['modified_str'] = str(t)
                # obj['modified_str'] = str(obj['modified'])
                ext = obj['ext'] = fs.get_ext(folder_file.name)
                obj['selected'] = False
                obj['url'] = folder_file.url
                obj['type'] = 'file'
                if ext in IMAGE_EXT:
                    obj['icon'] = obj['url']
                    obj['type'] = 'image'
                elif ext in FILE_EXT:
                    obj['icon'] = f'maven/img/icon/{FILE_EXT[ext]}.png'
                else:
                    obj['icon'] = f'maven/img/icon/{FILE_EXT["misc"]}.png'
                self.files.append(obj)

if __name__ == "__main__":
    paths = [
        'MTR',
        'MTR/dir with spaces/Test.html'
    ]
    media = MavenMedia(offline=True)
    for path in paths:
        media.path(path)
        if DEBUG: print(json.dumps(media.__dict__, indent="  "))
