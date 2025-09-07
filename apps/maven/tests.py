import json

import fs
import yaml
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.http import HttpRequest
from django.test import TestCase, override_settings
from django.utils import timezone

settings.TESTING = True

import maven.views as view
from maven.models import MediaFile, MediaFolder, MediaFolderPolicy
from maven.util import (MavenMedia, get_folders_recurse,
                   initialize_media_folders_in_database)

DEBUG = False

# Create your tests here.

class TestUser:
    admin = None
    user1 = None
    user2 = None

class TestGroup:
    admin = None
    team1 = None

class TestPolicy:
    admin = None
    team1 = None
    team2 = None

class TestFolder:
    top = None
    dir0 = None
    dir1 = None

SOURCE_DIR = fs.join(fs.dname(fs.abs(__file__)), 'testing', 'source', 'media')
TARGET_DIR = fs.join(fs.dname(fs.abs(__file__)), 'testing', 'target', 'media')
USERS = []

class MavenTest(TestCase):

    @override_settings(TESTING=True)
    @override_settings(MEDIA_ROOT=TARGET_DIR)
    def setUp(self):
        TestUser.admin = get_user_model().objects.create(username='admin', email='user0@fake.com', password='abcd1234', is_staff=True, is_superuser=True)
        TestUser.user1 = get_user_model().objects.create(username='user1', email='user1@fake.com', password='abcd1234', is_staff=True, is_superuser=False)
        TestUser.user2 = get_user_model().objects.create(username='user2', email='user2@fake.com', password='abcd1234', is_staff=False, is_superuser=False)
        
        self.users = list(get_user_model().objects.all())
        self.users.append(AnonymousUser)

        TestGroup.admin = Group.objects.create(name='admin')
        TestGroup.team1 = Group.objects.create(name='team1')

        TestUser.user1.groups.add(TestGroup.team1)
        TestUser.user1.save()

        TestPolicy.admin = MediaFolderPolicy.objects.create()
        TestPolicy.admin.admin_groups.add(TestGroup.admin)
        TestPolicy.admin.editor_groups.add(TestGroup.admin)
        TestPolicy.admin.contrib_groups.add(TestGroup.admin)
        TestPolicy.admin.visitors_can_view = False 
        TestPolicy.admin.save()

        TestPolicy.team1 = MediaFolderPolicy.objects.create()
        # TestPolicy.team1.admin_groups.add(TestGroup.team1)
        TestPolicy.team1.editor_groups.add(TestGroup.team1)
        TestPolicy.team1.contrib_groups.add(TestGroup.team1)
        TestPolicy.team1.save()

        TestPolicy.team2 = MediaFolderPolicy.objects.create()
        TestPolicy.team2.visitors_can_view = False 
        TestPolicy.team2.save()

        if fs.exists(TARGET_DIR): fs.delete_dir(TARGET_DIR)
        fs.copy_dir_if_changed(SOURCE_DIR, TARGET_DIR)
        initialize_media_folders_in_database()

        TestFolder.top = MediaFolder.objects.get(url='')

        TestFolder.dir0 = MediaFolder.objects.get(url='dir0')
        TestFolder.dir0.policy = TestPolicy.team1
        TestFolder.dir0.save()

        TestFolder.dir1 = MediaFolder.objects.get(url='dir1')
        TestFolder.dir1.policy = TestPolicy.admin
        TestFolder.dir1.save()

    @override_settings(TESTING=True)
    @override_settings(MEDIA_ROOT=TARGET_DIR)
    def test_001_media_root_dir_access(self):

        cnt = 0

        r"""
         ____  _           _                           _____         _
        |  _ \(_)_ __     / \   ___ ___ ___  ___ ___  |_   _|__  ___| |_ ___
        | | | | | '__|   / _ \ / __/ __/ _ \/ __/ __|   | |/ _ \/ __| __/ __|
        | |_| | | |     / ___ \ (_| (_|  __/\__ \__ \   | |  __/\__ \ |_\__ \
        |____/|_|_|    /_/   \_\___\___\___||___/___/   |_|\___||___/\__|___/
        
        """

        if DEBUG: print("** Dir access tests **")

        # Test base access with no policy.
        for url in ['']:
            media = MavenMedia()
            expect = [4, 1, 1, 1]
            for user in self.users:
                username = str(user) if user is not AnonymousUser else "anonymous"
                media.path(url, user=user)
                value = expect.pop(0)
                msg = f'User {username} access level {media.access} to URL "{url}" must equal {value}'
                if DEBUG: print(msg + ' ...')
                self.assertEqual(media.access, value, msg)
                cnt += 1
        
        # Test restricted directory (and subdirectory) access where visitors cannot browse.
        for url in ['dir1', 'dir1/dir10']:
            media = MavenMedia()
            expect = [4, 1, 1, 0]
            for user in self.users:
                username = str(user) if user is not AnonymousUser else "anonymous"
                media.path(url, user=user)
                value = expect.pop(0)
                msg = f'User {username} access level {media.access} to URL "{url}" must equal {value}'
                if DEBUG: print(msg + ' ...')
                self.assertEqual(media.access, value, msg)
                cnt += 1
        
        # Test restricted directory (and subdirectories) access where team1 members can edit.
        for url in ['dir0', 'dir0/dir00', 'dir0/dir01/dir010']:
            media = MavenMedia() 
            expect = [4, 3, 1, 1]
            for user in self.users:
                username = str(user) if user is not AnonymousUser else "anonymous"
                media.path(url, user=user)
                value = expect.pop(0)
                msg = f'User {username} access level {media.access} to URL "{url}" must equal {value}'
                if DEBUG: print(msg + ' ...')
                self.assertEqual(media.access, value, msg)
                cnt += 1
        
        r"""
         __  __                  _____ _ _        _____         _
        |  \/  | _____   _____  |  ___(_) | ___  |_   _|__  ___| |_
        | |\/| |/ _ \ \ / / _ \ | |_  | | |/ _ \   | |/ _ \/ __| __|  _____
        | |  | | (_) \ V /  __/ |  _| | | |  __/   | |  __/\__ \ |_  |_____|
        |_|  |_|\___/ \_/ \___| |_|   |_|_|\___|   |_|\___||___/\__|

        __     __    _ _     _   _   _
        \ \   / /_ _| (_) __| | | | | |___  ___ _ __
         \ \ / / _` | | |/ _` | | | | / __|/ _ \ '__|
          \ V / (_| | | | (_| | | |_| \__ \  __/ |
           \_/ \__,_|_|_|\__,_|  \___/|___/\___|_|

        """

        if DEBUG: print("** Move file tests: valid user **")

        # Create request
        filename = 'file010a.txt'
        source_dir = 'dir0/dir01/dir010'
        target_dir = 'dir1/dir10'

        request = HttpRequest()
        request.user = TestUser.admin
        request.method = 'POST'
        data = request.POST.copy()
        request.POST['id'] = 'maven-123456789'
        request.POST['action'] = 'file-move'
        request.POST['source'] = source_dir
        request.POST['target'] = target_dir
        request.POST['type'] = 'file'
        request.POST['files'] = json.dumps([dict(index=0, filename=filename, canEdit=True)])

        # Get source and target paths and URLs.
        source_file_path = fs.fix(fs.join(settings.MEDIA_ROOT, request.POST['source'], filename))
        source_file_url = request.POST['source'] + '/' + filename
        target_file_path = fs.fix(fs.join(settings.MEDIA_ROOT, request.POST['target'], filename))
        target_file_url = request.POST['target'] + '/' + filename
        
        # Test source MediaFile before move operation.  
        time_before = timezone.now()
        msg = f'Source MediaFile object for URL "{source_file_url}" must exist'
        if DEBUG: print(msg + ' ...')
        try: 
            source_file_inst = MediaFile.objects.get(url=source_file_url)
            self.assertTrue(True, msg)
            cnt += 1
        except:
            self.assertTrue(False, msg)
        msg = f'Source MediaFile object for URL "{source_file_url}" must be active'
        if DEBUG: print(msg + ' ...')
        self.assertTrue(source_file_inst.is_active, msg)
        cnt += 1

        # Test target MediaFile before move operation.
        msg = f'Target MediaFile object for URL "{target_file_url}" must not yet exist'
        if DEBUG: print(msg + ' ...')
        try: 
            target_file_inst = MediaFile.objects.get(url=target_file_url)
            self.assertTrue(False, msg)
        except:
            self.assertTrue(True, msg)
            cnt += 1

        # Call AjaxRefresh() for move file operation.  Get data response.
        responce = view.AjaxRefresh(request)
        data = json.loads(responce.content)
        time_after = timezone.now()

        # Test target MediaFile object.
        msg = f'Target MediaFile object for URL "{target_file_url}" must exist'
        if DEBUG: print(msg + ' ...')
        try: 
            target_file_inst = MediaFile.objects.get(url=target_file_url)
            self.assertTrue(True, msg)
            cnt += 1
        except: 
            self.assertTrue(False, msg)
        msg = f'Target MediaFile object for URL "{target_file_url}" must be active'
        if DEBUG: print(msg + ' ...')
        self.assertTrue(target_file_inst.is_active, msg)
        cnt += 1
        msg = f'Target MediaFile object for URL "{target_file_url}" must have been created by {TestUser.admin}'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(TestUser.admin, target_file_inst.created_by, msg)
        cnt += 1
        msg = f'Target MediaFile object for URL "{target_file_url}" must have been updated by {TestUser.admin}'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(TestUser.admin, target_file_inst.updated_by, msg)
        cnt += 1
        if DEBUG: print(f'Target MediaFile object for URL "{target_file_url}" created on {target_file_inst.created_on}.')
        msg = f'Target MediaFile object for URL "{target_file_url}" must have been created after {time_before}'
        if DEBUG: print(msg + ' ...')
        self.assertLessEqual(time_before, target_file_inst.created_on, msg)
        cnt += 1
        msg = f'Target MediaFile object for URL "{target_file_url}" must have been created before {time_after}'
        if DEBUG: print(msg + ' ...')
        self.assertLessEqual(target_file_inst.created_on, time_after, msg)
        cnt += 1

        # Test target file.
        msg = f'Target file "{target_file_path}" must now exist'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(fs.exists(target_file_path), True, msg)
        cnt += 1

        # Test source MediaFile after move (should exist but be deactivated).
        msg = f'Source file "{source_file_path}" should still exist'
        if DEBUG: print(msg + ' ...')
        self.assertTrue(fs.exists(source_file_path), msg)
        cnt += 1
        msg = f'Source MediaFile object for URL "{source_file_url}" should still exist'
        if DEBUG: print(msg + ' ...')
        try: 
            source_file_inst = MediaFile.objects.get(url=source_file_url)
            self.assertTrue(True, msg)
            cnt += 1
        except:
            self.assertTrue(False, msg)
        msg = f'Source MediaFile object for URL "{source_file_url}" must no longer be active'
        if DEBUG: print(msg + ' ...')
        self.assertFalse(source_file_inst.is_active, msg)
        cnt += 1
        files_moved = json.loads(data["files-moved"])
        move_cnt = len(files_moved)
        msg = f'Files moved list count {move_cnt} should be 1: {files_moved}'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(move_cnt, 1, msg)
        cnt += 1
        msg = f'File moved should be "{filename}"'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(filename, files_moved[0], msg)
        cnt += 1
        msg = f'File move count {data["file-move-count"]} should be 1'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(data["file-move-count"], 1, msg)
        cnt += 1
        msg = f'File move error should not be defined'
        if DEBUG: print(msg + ' ...')
        self.assertFalse('error' in data, msg)
        cnt += 1
        
        r"""
         __  __                  _____ _ _        _____         _
        |  \/  | _____   _____  |  ___(_) | ___  |_   _|__  ___| |_
        | |\/| |/ _ \ \ / / _ \ | |_  | | |/ _ \   | |/ _ \/ __| __|  _____
        | |  | | (_) \ V /  __/ |  _| | | |  __/   | |  __/\__ \ |_  |_____|
        |_|  |_|\___/ \_/ \___| |_|   |_|_|\___|   |_|\___||___/\__|

         ___                 _ _     _   _   _
        |_ _|_ ____   ____ _| (_) __| | | | | |___  ___ _ __
         | || '_ \ \ / / _` | | |/ _` | | | | / __|/ _ \ '__|
         | || | | \ V / (_| | | | (_| | | |_| \__ \  __/ |
        |___|_| |_|\_/ \__,_|_|_|\__,_|  \___/|___/\___|_|

        """

        if DEBUG: print("** Move file tests: invalid user **")

        filename = 'file0a.txt'
        source_dir = 'dir0'
        target_dir = 'dir1/dir10'

        request = HttpRequest()
        request.user = TestUser.user2
        request.method = 'POST'
        data = request.POST.copy()
        request.POST['id'] = 'maven-123456789'
        request.POST['action'] = 'file-move'
        request.POST['source'] = source_dir
        request.POST['target'] = target_dir
        request.POST['type'] = 'file'
        request.POST['files'] = json.dumps([dict(index=0, filename=filename, canEdit=True)])

        # Get source and target paths and URLs.
        source_file_path = fs.fix(fs.join(settings.MEDIA_ROOT, request.POST['source'], filename))
        source_file_url = request.POST['source'] + '/' + filename
        target_file_path = fs.fix(fs.join(settings.MEDIA_ROOT, request.POST['target'], filename))
        target_file_url = request.POST['target'] + '/' + filename

        # Test source MediaFile before move operation.  
        time_before = timezone.now()
        msg = f'Source MediaFile object for URL "{source_file_url}" must exist'
        if DEBUG: print(msg + ' ...')
        try: 
            source_file_inst = MediaFile.objects.get(url=source_file_url)
            self.assertTrue(True, msg)
            cnt += 1
        except:
            self.assertTrue(False, msg)
        msg = f'Source MediaFile object for URL "{source_file_url}" must be active'
        if DEBUG: print(msg + ' ...')
        self.assertTrue(source_file_inst.is_active, msg)
        cnt += 1

        # Test target MediaFile before move operation.
        msg = f'Target MediaFile object for URL "{target_file_url}" must not yet exist'
        if DEBUG: print(msg + ' ...')
        try: 
            target_file_inst = MediaFile.objects.get(url=target_file_url)
            self.assertTrue(False, msg)
        except:
            self.assertTrue(True, msg)
            cnt += 1

        # Call AjaxRefresh() for move file operation.  Get data response.
        responce = view.AjaxRefresh(request)
        data = json.loads(responce.content)
        time_after = timezone.now()

        # Test target MediaFile object.
        msg = f'Target MediaFile object for URL "{target_file_url}" should not exist'
        if DEBUG: print(msg + ' ...')
        try: 
            target_file_inst = MediaFile.objects.get(url=target_file_url)
            self.assertTrue(False, msg)
            cnt += 1
        except: 
            self.assertTrue(True, msg)

        # Test target file.
        msg = f'Target file "{target_file_path}" should still not exist'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(fs.exists(target_file_path), False, msg)
        cnt += 1

        # Test source MediaFile after failed move should not be deactivated.
        msg = f'Source file "{source_file_path}" should still exist'
        if DEBUG: print(msg + ' ...')
        self.assertTrue(fs.exists(source_file_path), msg)
        cnt += 1
        msg = f'Source MediaFile object for URL "{source_file_url}" should still exist'
        if DEBUG: print(msg + ' ...')
        try: 
            source_file_inst = MediaFile.objects.get(url=source_file_url)
            self.assertTrue(True, msg)
            cnt += 1
        except:
            self.assertTrue(False, msg)
        msg = f'Source MediaFile object for URL "{source_file_url}" should not be deactivated'
        if DEBUG: print(msg + ' ...')
        self.assertTrue(source_file_inst.is_active, msg)
        files_moved = json.loads(data["files-moved"])
        move_cnt = len(files_moved)
        msg = f'Files moved list count {move_cnt} should be 0: {files_moved}'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(move_cnt, 0, msg)
        cnt += 1
        msg = f'File move count {data["file-move-count"]} should be 0'
        if DEBUG: print(msg + ' ...')
        self.assertEqual(data["file-move-count"], 0, msg)
        cnt += 1
        msg = f'File move error should be defined'
        if DEBUG: print(msg + ' ...')
        self.assertTrue('error' in data, msg)
        cnt += 1

        r"""
         ____                       _     _____         _
        |  _ \ ___ _ __   ___  _ __| |_  |_   _|__  ___| |_
        | |_) / _ \ '_ \ / _ \| '__| __|   | |/ _ \/ __| __|
        |  _ <  __/ |_) | (_) | |  | |_    | |  __/\__ \ |_
        |_| \_\___| .__/ \___/|_|   \__|   |_|\___||___/\__|
                  |_|
         ____                 _ _
        |  _ \ ___  ___ _   _| | |_ ___
        | |_) / _ \/ __| | | | | __/ __|
        |  _ <  __/\__ \ |_| | | |_\__ \
        |_| \_\___||___/\__,_|_|\__|___/
        
        """

        if DEBUG: print(f'Passed {cnt} test assertions!')
        fs.delete_dir(fs.dname(TARGET_DIR))


