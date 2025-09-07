# Installation



## Dependencies

Media Maven requires the following Python modules be installed:

```python
filelock==3.0.12
PyYAML==5.3.1
```

It also requires the following static assets:

```
📁 static
 ├── 📁 dialog
 |    ├── 📁 img
 |    ├── 📄 dialog.css
 |    ├── 📄 dialog.css.map
 |    └── 📄 dialog.js
 └── 📁 fontawesome
```

Media Maven makes use of the `assets` template tags:

```
📁 templatetags
 ├── 📄 __init__.py
 └── 📄 assets.py
```

## Settings

In `settings.py` add `maven.apps.MavenConfig` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'maven.apps.MavenConfig',
]
```

It is also recommended (though optional) to add the following:

```python
MEDIA_MAVEN = {
    # Set 'THEME' to one of: 'autumn', 'charcoal', 'midnight', or 'ocean' -- or roll your own!!!
    'THEME': 'charcoal',  
}
```

The `MEDIA_MAVEN` settings dictionary allows you to customize Media Maven.

In `urls.py`:

```python
from maven.views import ExplorerAdminRoot

urlpatterns = [   
    path('admin/maven/mediaexplorer/', ExplorerAdminRoot, name='maven-explorer-admin'),
    path('admin/maven/mediaexplorer/add/', ExplorerAdminRoot, name='maven-explorer-admin-add'),
    path('maven/', include('maven.urls')), 
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

```

> **IMPORTANT**: Media Maven URLs need to come *before* admin URLs.  That's because Media Maven adds a Media Explorer to your admin view.  The Media Explorer is associated with a dummy table so that a link to the Media Explorer appears in the admin index.  The "mediaexplorer" URLs defined above must come before the admin URLS so that "Add" and "Change" links on the index are properly rerouted to the Media Explorer view and not the non-existing database model admin view.   

## Adding Admin Widgets to Admin Model Views

The easiest way to add Media Maven widgets to admin model views is to create custom admin forms.  This is actually a fairly easy task.  

Suppose you have an existing model named `ImageLogger`.  You have already define an admin:

```python
from django.contrib import admin

from .models import ImageLogger

@admin.register(ImageLogger)
class ImageLoggerAdmin(admin.ModelAdmin):
    fields = ['title', 'image', 'caption']
    list_display = ['title', 'caption']
```

You want the `image` field defined in the model to use `MavenImageSelectorAdminWidget`.  

First, edit `forms.py` and create a custom `ImageLoggerAdminForm`.  Use the `Meta` class to define the `image` field to use  `MavenImageSelectorAdminWidget`.  Optionally, specify a `url` argument to the media URL where the image selector will open: 

```python
from maven.widgets import MavenFileSelectorAdminWidget, MavenImageSelectorAdminWidget, MavenDirSelectorAdminWidget

class ImageLoggerAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'image': MavenImageSelectorAdminWidget(url='Photos'),
        }
```

Now, go back to `admin.py` and make the following edits (adding 2 lines):

```python
from django.contrib import admin

from .models import ImageLogger
## NEW: Import ImageLoggerAdminForm from forms.
from .forms import ImageLoggerAdminForm

@admin.register(ImageLogger)
class ImageLoggerAdmin(admin.ModelAdmin):
    ## NEW: Use ImageLoggerAdminForm.
    form = ImageLoggerAdminForm
    fields = ['title', 'image', 'caption']
    list_display = ['title', 'caption']
```




