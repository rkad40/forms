# Media Management

**The Maven database tables model the physical media file system.**

Media folders and files exist in a physical location in the website's media folder.  Information about the media folders and files is maintained in the Maven database tables.  

> **IMPORTANT**: When you are using Maven to navigate the medial file system, you are actually traversing the mirrored file system information in the database.  Avoid adding, moving, renaming and deleting folders or files manually (e.g. doing a `rm my_profile_pic.jpg` from the Linux command line).  This can have serious consequences and very unintended effects.    


**Deleting a file does not remove it from the file system.**

When you delete a file in media folder using the Maven explorer, it is not actually deleted from the file system.  Rather, it is archived by setting its `is_active` field to `False`.  This removes it from the explorer, effectively making it *appear* as if the file has been deleted.  

In reality, the file remains in the physical file system, and in an archived state in the database, because there may still be links that still reference the file.  But it will no longer be visible in the Maven explorer, or selectable using the file and image selector widgets.  

> **NOTE**: A superuser can permanently delete a file from the database and file system.  But care should be taken when doing this.  

