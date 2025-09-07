import json

import fs
import ru
import yaml
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.http import HttpRequest
from django.utils import timezone
from menu.simple import select_one

from maven.models import MediaFile, MediaFolder, MediaFolderPolicy
from maven.util import get_user_access, initialize_media_folders_in_database
from maven.views import AjaxRefresh

print(r"""
 __  __          _ _         __  __
|  \/  | ___  __| (_) __ _  |  \/  | __ ___   _____ _ __
| |\/| |/ _ \/ _` | |/ _` | | |\/| |/ _` \ \ / / _ \ '_ \
| |  | |  __/ (_| | | (_| | | |  | | (_| |\ V /  __/ | | |
|_|  |_|\___|\__,_|_|\__,_| |_|  |_|\__,_| \_/ \___|_| |_|

""")


VALID_ACTIONS = ['init', 'rm', 'ls', 'debug']

class Command(BaseCommand):
    help = 'Initialize Maven media'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, help="Action to perform: " + ', '.join(VALID_ACTIONS))
        
    def handle(self, *args, **options):

        if options['action'] == 'init': 
            self.init()
        elif options['action'] == 'rm':
            self.rm()
        elif options['action'] == 'ls':
            self.ls()
        elif options['action'] == 'debug':
            self.debug()
        else:
            raise Exception(f"""Invalid Maven action "{options['action']}".  Must be one of: {', '.join(VALID_ACTIONS)}.""")

    def debug(self):
        request = HttpRequest()
        request.user = get_user_model().objects.get(id=1)
        request.method = 'POST'
        data = request.POST.copy()
        request.POST['id'] = 'maven-123456789'
        request.POST['action'] = 'file-move'
        request.POST['arg'] = 'Temp'
        request.POST['cwd'] = 'Temp'
        request.POST['target'] = 'Archive'
        request.POST['type'] = 'file'
        request.POST['selectedFiles'] = [
            dict(index=2, filename='origen.rb', canEdit=True),
            dict(index=3, filename='pdf.png', canEdit=True),
        ]
        responce = AjaxRefresh(request)
        data = json.loads(responce.content)
        print(data)

    def debug2(self):
        # folder = MediaFolder.objects.get(url='Devices/LX2160/dev')
        folder = MediaFolder.objects.get(url='Devices/LS1088')
        users = get_user_model().objects.all()
        for user in users:
            access = get_user_access(user, folder)
            print(f'username="{user.username}", access={access}')
        access = get_user_access(None, folder)
        print(f'username=None, access={access}')
                
    def debug1(self):
        file = r"C:\Work\TestRequirementsWebProj2\proj\maven\urls.py"
        modified = fs.last_modified(file)
        print(modified)
        t = timezone.datetime.fromtimestamp(modified)
        print(t)
        print(t.strftime("%m/%d/%Y %I:%M %p"))

    def ls(self):
        data = {}
        folders = MediaFolder.objects.all()
        for folder in folders:
            data[folder.url] = {
                'Ancestor Folders': [],
                'Child Folders': [],
                'Files': [],
            }
            for ancestor in folder.ancestor_folders.all().order_by('-id'):
                data[folder.url]['Ancestor Folders'].append(ancestor.url)
            for child in folder.child_folders.all().order_by('name'):
                data[folder.url]['Child Folders'].append(child.url)
            for file in folder.files.all().order_by('id'):
                data[folder.url]['Files'].append(file.url)
        print(json.dumps(data, indent="  "))

    def rm(self):
        if (select_one("This action will purge Maven records in the database.  Continue?", ['Yes', 'No'], default='No') == 'No'): return
        print("Deleting all Maven records ...")
        MediaFile.objects.all().delete()
        MediaFolder.objects.all().delete()
        MediaFolderPolicy.objects.all().delete()
        print("Done.")
    
    def init(self):
        if (select_one("This action will initialize or update Maven records in the database.  Continue?", ['Yes', 'No'], default='No') == 'No'): return
        initialize_media_folders_in_database()




            

