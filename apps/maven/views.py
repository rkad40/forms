import json
import pprint

import os
import fs
import ru
from cronos import epoch
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from filelock import FileLock
from rex import Rex

from .forms import TestWidgetsForm
from .models import MediaFile, MediaFolder, MediaFolderPolicy
from .util import MavenMedia, get_user_access

r"""
__     ___                 _   _      _
\ \   / (_) _____      __ | | | | ___| |_ __   ___ _ __
 \ \ / /| |/ _ \ \ /\ / / | |_| |/ _ \ | '_ \ / _ \ '__|
  \ V / | |  __/\ V  V /  |  _  |  __/ | |_) |  __/ |
   \_/  |_|\___| \_/\_/   |_| |_|\___|_| .__/ \___|_|
                                       |_|
 _____                 _   _
|  ___|   _ _ __   ___| |_(_) ___  _ __  ___
| |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|
|  _|| |_| | | | | (__| |_| | (_) | | | \__ \
|_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

 _____ _____ _____ _____ _____ _____ _____ _____ _____ _____ _____ _____ _____
|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|_____|

"""

r"""
 _                     _ _         __ _ _
| |__   __ _ _ __   __| | | ___   / _(_) | ___
| '_ \ / _` | '_ \ / _` | |/ _ \ | |_| | |/ _ \
| | | | (_| | | | | (_| | |  __/ |  _| | |  __/
|_| |_|\__,_|_| |_|\__,_|_|\___| |_| |_|_|\___|

             _                 _
 _   _ _ __ | | ___   __ _  __| |
| | | | '_ \| |/ _ \ / _` |/ _` |
| |_| | |_) | | (_) | (_| | (_| |
 \__,_| .__/|_|\___/ \__,_|\__,_|
      |_|

"""

def handle_file_upload(file, target_folder_inst, request):
    """
    Upload client file object to the target folder.  
    """
    ## Get and process the file name.
    rex = Rex()
    file_name = file.name
    file_name = rex.s(file_name, '^\W+', '', '=')
    file_name = rex.s(file_name, r'[^\w\.\-]', r'', 'g=')
    file_ext = fs.get_ext(file_name)
    file_name = fs.remove_ext(file_name)
    file_name = file_name + '.' + file_ext.lower()
    ## Generate file URL and absolute file system path.
    file_url = target_folder_inst.url + '/' + file_name
    out_file_path = fs.fix_path_name(fs.join_names(settings.MEDIA_ROOT, file_url))
    if settings.DEBUG: print(f'Saving file "{out_file_path}" ...')
    ## Upload file in chunks.
    with open(out_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    os.chmod(out_file_path, 0o775)
    ## Get or create the corresponding MedialFile object.  
    created_object = False
    file_inst = MediaFile.objects.filter(url=file_url).first()
    if file_inst is None:
        created_object = True
        file_inst = MediaFile()
    file_inst.url = file_url
    file_inst.name = file_name
    file_inst.folder = target_folder_inst
    if created_object:
        if request.user is not None: file_inst.created_by = request.user
        file_inst.created_on = timezone.now()
    else:
        if request.user is not None: file_inst.updated_by = request.user
        file_inst.updated_on = timezone.now()
    file_inst.size = fs.get_size(out_file_path)
    file_inst.is_active = True
    ## Save the file instance.
    file_inst.save()

r"""
                 _       _                         _
 _   _ _ __   __| | __ _| |_ ___    _____  ___ __ | | ___  _ __ ___ _ __
| | | | '_ \ / _` |/ _` | __/ _ \  / _ \ \/ / '_ \| |/ _ \| '__/ _ \ '__|
| |_| | |_) | (_| | (_| | ||  __/ |  __/>  <| |_) | | (_) | | |  __/ |
 \__,_| .__/ \__,_|\__,_|\__\___|  \___/_/\_\ .__/|_|\___/|_|  \___|_|
      |_|                                   |_|
                 _             _
  ___ ___  _ __ | |_ ___ _ __ | |_
 / __/ _ \| '_ \| __/ _ \ '_ \| __|
| (_| (_) | | | | ||  __/ | | | |_
 \___\___/|_| |_|\__\___|_| |_|\__|

"""

def update_explorer_content(data, target_url, user=None):
    """
    Update the Explorer content (cwd, crumbs, dir-list and file-list HTML elements).  
    """
    ## Get the MedusiaMedia object for the target URL.
    media = MavenMedia()
    file_type = data['type'] if 'type' in data else None
    media.path(target_url, file_type, user)
    ## Check for errors ...
    if media.error:
        data['error'] = media.error
    ## .. if no error, render the cwd, crumbs, dir-list and file-list HTML elements.
    else:
        data['ajax'] = {
            'cwd': media.root_url,
            'dir-access': media.access,
            'crumbs': render_to_string(template_name='maven/component/crumbs.html', context=dict(id=data['id'], maven=media)),
            'dir-list': render_to_string(template_name='maven/component/dir-list.html', context=dict(id=data['id'], maven=media)),
            'file-list': render_to_string(template_name='maven/component/file-list.html', context=dict(id=data['id'], maven=media)),
        }
    ## Set data['valid'] to True, even if there is an error.  data['valid'] just indicates that 
    data['valid'] = True

r"""
 _____         _
|_   _|__  ___| |_
  | |/ _ \/ __| __|
  | |  __/\__ \ |_
  |_|\___||___/\__|

"""

def Test(request):
    return render(request, template_name='maven/debug.html')  

def TestWidgets(request):
    if request.method == 'POST':
        form = TestWidgetsForm(request.POST)
    else:
        form = TestWidgetsForm()
    return render(request, 'maven/test-widgets.html', {'form': form})

r"""
 _____            _                     ____             _
| ____|_  ___ __ | | ___  _ __ ___ _ __|  _ \ ___   ___ | |_
|  _| \ \/ / '_ \| |/ _ \| '__/ _ \ '__| |_) / _ \ / _ \| __|
| |___ >  <| |_) | | (_) | | |  __/ |  |  _ < (_) | (_) | |_
|_____/_/\_\ .__/|_|\___/|_|  \___|_|  |_| \_\___/ \___/ \__|
           |_|
"""

def ExplorerRoot(request):
    """
    Call explorer view without target URL.  This loads the top level media folder.  
    """
    return Explorer(request, '')

r"""
 _____            _                      _       _           _
| ____|_  ___ __ | | ___  _ __ ___ _ __ / \   __| |_ __ ___ (_)_ __
|  _| \ \/ / '_ \| |/ _ \| '__/ _ \ '__/ _ \ / _` | '_ ` _ \| | '_ \
| |___ >  <| |_) | | (_) | | |  __/ | / ___ \ (_| | | | | | | | | | |
|_____/_/\_\ .__/|_|\___/|_|  \___|_|/_/   \_\__,_|_| |_| |_|_|_| |_|
           |_|
 ____             _
|  _ \ ___   ___ | |_
| |_) / _ \ / _ \| __|
|  _ < (_) | (_) | |_
|_| \_\___/ \___/ \__|

"""

@login_required
def ExplorerAdminRoot(request):
    """
    Call explorer view without target URL.  This loads the top level media folder.  
    """
    return ExplorerAdmin(request, '')

r"""
 _____            _
| ____|_  ___ __ | | ___  _ __ ___ _ __
|  _| \ \/ / '_ \| |/ _ \| '__/ _ \ '__|
| |___ >  <| |_) | | (_) | | |  __/ |
|_____/_/\_\ .__/|_|\___/|_|  \___|_|
           |_|
"""

def Explorer(request, path):
    """
    Call explorer view for target URL path.  
    """
    media = MavenMedia()
    media.path(path)
    id = f'maven-{epoch(int)}'
    return render(request, template_name='maven/explorer.html', context=dict(id=id, maven=media))

r"""
 _____            _                      _       _           _
| ____|_  ___ __ | | ___  _ __ ___ _ __ / \   __| |_ __ ___ (_)_ __
|  _| \ \/ / '_ \| |/ _ \| '__/ _ \ '__/ _ \ / _` | '_ ` _ \| | '_ \
| |___ >  <| |_) | | (_) | | |  __/ | / ___ \ (_| | | | | | | | | | |
|_____/_/\_\ .__/|_|\___/|_|  \___|_|/_/   \_\__,_|_| |_| |_|_|_| |_|
           |_|
"""

@login_required
def ExplorerAdmin(request, path):
    """
    Call explorer view for target URL path.  
    """
    media = MavenMedia()
    media.path(path)
    id = f'maven-{epoch(int)}'
    return render(request, template_name='maven/explorer-admin.html', context=dict(id=id, maven=media))

r"""
    _     _            ____       __               _
   / \   (_) __ ___  _|  _ \ ___ / _|_ __ ___  ___| |__
  / _ \  | |/ _` \ \/ / |_) / _ \ |_| '__/ _ \/ __| '_ \
 / ___ \ | | (_| |>  <|  _ <  __/  _| | |  __/\__ \ | | |
/_/   \_\/ |\__,_/_/\_\_| \_\___|_| |_|  \___||___/_| |_|
       |__/
"""

def AjaxRefresh(request):

    ## All Ajax requests must be of type POST.  If not, go scorched earth.
    if request.method != 'POST':
        data = dict(valid=False, error='Invalid request.')
        return JsonResponse(data)

    ## Get POST data 
    data = request.POST.dict()
    if settings.DEBUG: print("===\nAJAX DATA\n---\n", str(data), "\n===")
    action = data['action']

    ## Action is "dir-select":
    if action == 'dir-select':
        target_url = data['arg']
        update_explorer_content(data, target_url, user=request.user)
        return JsonResponse(data)

    ## Action is "file-move":
    if action == 'file-move':
        # Get files, source_dir_url and target_dir_url from data.
        files = json.loads(data['files'])
        source_dir_url = data['source']
        target_dir_url = data['target']
        # Get source and target MediaFolder objects.
        source_folder = MediaFolder.objects.get(url=source_dir_url)
        target_folder = MediaFolder.objects.get(url=target_dir_url)
        # Get source and target access levels.
        source_access = get_user_access(request.user, source_folder)
        target_access = get_user_access(request.user, target_folder)
        # Initialize arrays.
        files_moved = []
        error_messages = []

        data['files-moved'] = []
        data['file-move-count'] = 0

        # Make sure source and target directories are different.
        if source_dir_url == target_dir_url:
            error_messages.append('Source and target directories are the same.')
        # Render error if user does not have target access ...
        elif target_access < 2: 
            error_messages.append('You do not have write access to the destination folder.  No files moved.')
        # ... otherwise:
        else:
            # Cycle through all files.
            for file in files:
                try:
                    # Get name.
                    name = file['filename']
                    # Get source and target file URLs.
                    source_file_url = source_dir_url + '/' + name
                    target_file_url = target_dir_url + '/' + name
                    # Get source, target and lock file paths.
                    source_file_path = fs.fix_path_name(fs.join_names(settings.MEDIA_ROOT, source_file_url))
                    target_file_path = fs.fix_path_name(fs.join_names(settings.MEDIA_ROOT, target_file_url))
                    target_file_lock = target_file_path + '.lock'
                    source_file_dir = fs.dname(source_file_path)
                    target_file_dir = fs.dname(source_file_path)
                    if not fs.exists(source_file_dir): raise Exception('Source folder "{source_file_dir}" does not exist.')
                    if not fs.exists(source_file_path): raise Exception('Source file "{source_file_path}" does not exist.')
                    if not fs.exists(target_file_dir): raise Exception('Target folder "{target_file_dir}" does not exist.')
                    # Use file locking to copy source file to target file location.  NOTE: We do not 
                    # delete the source file, only archive it by setting is_active attribute to False.
                    with FileLock(target_file_lock, timeout=1):
                        fs.copy_file(source_file_path, target_file_path)
                    os.chmod(target_file_path, 0o775)
                    # Get source's MediaFile object and set its is_active attribute to False.  Save it. 
                    source_file_inst = MediaFile.objects.get(url=source_file_url)
                    if source_access == 2 and request.user != source_file_inst.created_by:
                        raise Exception(f'Cannot move file "{source_file_inst.name}".  You are not the owner.')
                    if source_access < 2:
                        raise Exception(f'Cannot move file "{source_file_inst.name}".  You do not have access.')
                    source_file_inst.is_active = False
                    source_file_inst.save()
                    # Get or create the target's MediaFile object.  
                    try:
                        target_file_inst = MediaFile.objects.get(url=target_file_url)
                    except MediaFile.DoesNotExist:
                        target_file_inst = MediaFile()
                        target_file_inst.url = target_file_url
                    # Set instance attributes.
                    target_file_inst.name = name
                    target_file_inst.created_by = request.user
                    target_file_inst.created_on = timezone.now()
                    target_file_inst.updated_by = request.user
                    target_file_inst.updated_on = timezone.now()
                    target_file_inst.folder = target_folder
                    target_file_inst.is_active = True
                    target_file_inst.size = fs.get_size(target_file_path)
                    # Save the target file.
                    target_file_inst.save()
                    files_moved.append(source_file_inst.name)
                except Exception as err:
                    error_messages.append(f'''File "{name}" not moved.  {err}''')
        error_count = len(error_messages)
        success_count = len(files_moved)
        data['files-moved'] = json.dumps(files_moved)
        data['file-move-count'] = success_count
        if error_count > 0:
            if error_count == 1:
                data['error'] = error_messages[0]
            else:
                data['error'] = f'A total of {error_count} errors detected:<ul>'
                for msg in error_messages:
                    data['error'] += f'<li>{msg}</li>'
                data['error'] += '</ul>'
            data['error'] += f'<p>A total of {success_count} file{"s" if success_count != 1 else ""} moved.'
        else:
            data['message'] = f'A total of {success_count} file{"s were" if success_count != 1 else " was"} successfully moved.'
        update_explorer_content(data, target_dir_url, user=request.user)
        return JsonResponse(data)

    ## Action is "file-delete":
    if action == 'file-delete':
        data['valid'] = True
        files = json.loads(data['arg'])
        cwd = data['cwd']
        try:
            for file in files:
                url = cwd + '/' + file['filename']
                file_inst = MediaFile.objects.get(url=url)
                file_inst.is_active = False
                file_inst.save()
        except Exception as err:
            data['error'] = 'Error deleting file: ' + str(err)
        update_explorer_content(data, cwd, user=request.user)
        return JsonResponse(data)

    ## Action is "directory-create":
    if action == 'directory-create':
        data['valid'] = True
        # The value data['arg'] is a JSON string that, when parsed, is a list whose first element is 
        # the parent URL and whose second element is the new folder URL.  Get parent_url and 
        # dir_url.
        urls = json.loads(data['arg'])
        parent_url = urls[0]
        dir_url = urls[1]
        # Construct dir_path and parent_path from dir_url and parent_url respectively.
        dir_path = fs.fix_path_name(fs.join_names(settings.MEDIA_ROOT, dir_url))
        parent_path = fs.fix_path_name(fs.join_names(settings.MEDIA_ROOT, parent_url))
        # Get the dir root name.
        name = fs.get_file_name(dir_path)

        try:
            # Get the parent MediaFolder object.
            parent_folder = MediaFolder.objects.get(url=parent_url)
            # Check access.
            if request.user.is_anonymous:
                raise Exception('You do not have access.')
            if get_user_access(request.user, parent_folder) < 3:
                raise Exception('You do not have access.')
            # Create the new dir path (soon to be a child of parent_folder).
            fs.create_dir(dir_path)
            os.chmod(dir_path, 0o775)
            # Check to make sure the new folder does not already have an entry in the database.  
            # This can happen if the the folder was previously created, then "deleted".  A 
            # "deleted" folder is one where the is_active attribute has been set to False.  This 
            # "deleted" folder is not actually removed in the event that there are still website 
            # assets trying to access it.   
            folder = MediaFolder.objects.filter(url=dir_url).first()
            # If the folder already exists, just reactive it ... 
            if folder is not None:
                folder.is_active = True
                folder.save()
                data['message'] = f"""Folder "{dir_url}" already existed but was previously archived.  It has been restored to active status."""
            # ... if not, create it.
            else:
                # Create the new folder and set its attributes.
                folder = MediaFolder()
                folder.name = name
                folder.url = dir_url
                if request.user is not None: folder.created_by = request.user
                folder.created_on = timezone.now()
                folder.is_active = True
                # Save the folder.
                folder.save()
                # For the folder's ancestor_folders attributes, add all ancestors of the 
                # parent_folder and the parent_folder itself.
                for ancestor in parent_folder.ancestor_folders.all().order_by('-url'):
                    folder.ancestor_folders.add(ancestor)
                folder.ancestor_folders.add(parent_folder)
                # FIX: Is it necessary to re-save?  I don't think it is.  I think add() does so 
                # automatically.  
                folder.save()
                # Add the folder to the parent_folder.child_folders attribute.  
                parent_folder.child_folders.add(folder)
                # FIX: Is it necessary to save?  I don't think it is.  I think add() does so 
                # automatically.  
                parent_folder.save()
        except Exception as err:
            data['error'] = f'An error occurred trying to create folder "{dir_url}": ' + str(err)
            return JsonResponse(data)
        # Update explorer content.
        update_explorer_content(data, dir_url, user=request.user)
        return JsonResponse(data)

    ## Action is "get-file-upload-form"
    if action == 'get-file-upload-form':
        data['ajax'] = {}
        data['ajax']['upload-form'] = render_to_string(template_name='maven/component/file-upload-form.html', context=dict(id=data['id']))
        data['valid'] = True
        return JsonResponse(data)

    ## Action is "get-file-select-html"
    if action == 'get-file-select-html':
        data['ajax'] = {}
        update_explorer_content(data, data['cwd'], user=request.user)
        data['ajax']['file-select-html'] = render_to_string(template_name='maven/component/file-selector.html', context=dict(id=data['id']))
        data['valid'] = True
        return JsonResponse(data)

    ## Action is "get-dir-select-html"
    if action == 'get-dir-select-html':
        data['ajax'] = {}
        update_explorer_content(data, data['cwd'], user=request.user)
        data['ajax']['dir-select-html'] = render_to_string(template_name='maven/component/dir-selector.html', context=dict(id=data['id']))
        data['valid'] = True
        return JsonResponse(data)

    ## Action is 'file-upload'.
    if action == 'file-upload':
        # Assume the best (be and optimist)!
        data['valid'] = True
        # Get the target MediaFolder instance.
        target_url = data['arg']
        target_folder_inst = MediaFolder.objects.get(url=target_url)
        uploaded_files = 0
        # Cycle through and upload all request.FILES entries.
        try:
            for key in request.FILES:
                files = request.FILES.getlist(key)
                if len(files) == 0:
                    data['error'] = 'No files selected for upload.'
                    return JsonResponse(data)
                for file in files:
                    handle_file_upload(file, target_folder_inst, request)
                    uploaded_files += 1
        except Exception as err:
            data['error'] = 'An error occurred during upload: ' + str(err)
            return JsonResponse(data)
        # If no files were uploaded, report an error.
        if uploaded_files == 0:
            data['error'] = 'No files selected for upload.'
            return JsonResponse(data)
        # Update explorer content.
        update_explorer_content(data, target_url, user=request.user)
        # Create response message for success dialog.
        data['message'] = f'A total of {uploaded_files} file{"" if uploaded_files == 0 else "s"} successfully uploaded.'
        return JsonResponse(data)

    data = dict(valid=False, error='Invalid request.')
    return JsonResponse(data)

# def AjaxGetFileUploadForm(request):
#     form_html = render_to_string(template_name='maven/component/crumbs.html', context=dict(id=data['id'], maven=media)),
