import fs
from django import template
from django.conf import settings
from PIL import Image

from django.core.serializers import serialize
from django.db.models.query import QuerySet

import json

register = template.Library()

DEBUG = False
IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif'}

@register.filter( is_safe=True )
def maven_jsonify(object): return str(object)

r"""
            _                                         _
  __ _  ___| |_    ___ _ __ ___  _ __  _ __   ___  __| |
 / _` |/ _ \ __|  / __| '__/ _ \| '_ \| '_ \ / _ \/ _` |
| (_| |  __/ |_  | (__| | | (_) | |_) | |_) |  __/ (_| |
 \__, |\___|\__|  \___|_|  \___/| .__/| .__/ \___|\__,_|
 |___/                          |_|   |_|
 _
(_)_ __ ___   __ _  __ _  ___
| | '_ ` _ \ / _` |/ _` |/ _ \
| | | | | | | (_| | (_| |  __/
|_|_| |_| |_|\__,_|\__, |\___|
                   |___/
"""
def get_cropped_image(img_file_path, w, h, align_x=0.5, align_y=0.5):
    r"""
    Takes a relative path to a media file.  Return the relative path to a cropped version of that 
    file if possible.  
    
    Example::

        cropped_file = get_cropped_image('Photo/Places/Timbuktu.png', 200, 150)

    The function renders a cropped file 'Photo/Places/.thumb/.Timbuktu__200x150_cropped.png'. 
    
    - If the cropped file does not exist, it is created.
    - If the cropped file exists, but the source is newer, it is updated.
    - If the cropped file exists and the source is older, nothing is done.

    The function returns the cropped file name.  This function is used by the 
    ``media_crop`` template tag::

        {% maven %}
        <img src="{% media_crop 'Photo/Places/Timbuktu.png' '200x150' %}">

    """
    ## Get ext, dir_name and root_name.
    ext = fs.get_ext(img_file_path)
    dir_name = fs.get_dir_name(img_file_path)
    root_name = fs.remove_ext(fs.get_file_name(img_file_path))

    ## From that create the cropped_img_file_path.  
    cropped_img_file_dir = fs.join_names(dir_name, '.thumb')
    if not fs.dir_exists(cropped_img_file_dir): fs.create_dir(cropped_img_file_dir, 0o775)
    cropped_img_file_path = fs.join_names(cropped_img_file_dir, f'.{root_name}__{w}x{h}_cropped.{ext}')
    if DEBUG: print(f'cropped_img_file_path={cropped_img_file_path}')

    ## If the cropped_img_file_path exists and is newer than the original img_file_path, no 
    ## cropping is necessary.  Simply return cropped_img_file_path.
    if fs.file_exists(cropped_img_file_path) and fs.file_exists(img_file_path) and \
        fs.last_modified(cropped_img_file_path) > fs.last_modified(img_file_path):
            if DEBUG: print(f"File '{cropped_img_file_path}' exists.")
            return cropped_img_file_path

    ## If we get here, cropping is necessary.  Get Image object and first crop to aspect ratio w/h.
    img = Image.open(img_file_path)
    if img.width / img.height > w / h:
        newwidth = int(img.height * (w / h))
        newheight = img.height
    else:
        newwidth = img.width
        newheight = int(img.width / (w / h))
    new_img = img.crop((
        align_x * (img.width - newwidth),
        align_y * (img.height - newheight),
        align_x * (img.width - newwidth) + newwidth,
        align_y * (img.height - newheight) + newheight))

    ## Next scale to size.
    new_img.thumbnail((w, h), Image.Resampling.LANCZOS)

    ## Save the cropped image.
    new_img.save(cropped_img_file_path)
    if DEBUG: print(f"File '{cropped_img_file_path}' updated or created.")

    ## Return the relative cropped image file path (suitable for inserting in image src attributes).
    return cropped_img_file_path

r"""
 _                       _       _         _
| |_ ___ _ __ ___  _ __ | | __ _| |_ ___  | |_ __ _  __ _ _
| __/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \ | __/ _` |/ _` (_)
| ||  __/ | | | | | |_) | | (_| | ||  __/ | || (_| | (_| |_
 \__\___|_| |_| |_| .__/|_|\__,_|\__\___|  \__\__,_|\__, (_)
                  |_|                               |___/
                    _ _
 _ __ ___   ___  __| (_) __ _
| '_ ` _ \ / _ \/ _` | |/ _` |
| | | | | |  __/ (_| | | (_| |
|_| |_| |_|\___|\__,_|_|\__,_|

"""
@register.simple_tag
def maven_media(url):
    r"""
    Media tag (similar to static).
    
    Usage::

        {% maven %}
        <img src="{% maven_media 'path/to/file.png' %}">

    Also works with template variables::

        {% maven %}
        {% for img_file_path in img_file_paths %}
            <img src="{% maven_media img_file_path %}">
        {% endfor %}

    """
    img_file_url = f'{settings.MEDIA_URL}{url}'
    return f'{img_file_url}'

r"""
 _                       _       _         _
| |_ ___ _ __ ___  _ __ | | __ _| |_ ___  | |_ __ _  __ _ _
| __/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \ | __/ _` |/ _` (_)
| ||  __/ | | | | | |_) | | (_| | ||  __/ | || (_| | (_| |_
 \__\___|_| |_| |_| .__/|_|\__,_|\__\___|  \__\__,_|\__, (_)
                  |_|                               |___/
                    _ _
 _ __ ___   ___  __| (_) __ _    ___ _ __ ___  _ __
| '_ ` _ \ / _ \/ _` | |/ _` |  / __| '__/ _ \| '_ \
| | | | | |  __/ (_| | | (_| | | (__| | | (_) | |_) |
|_| |_| |_|\___|\__,_|_|\__,_|  \___|_|  \___/| .__/
                                              |_|
"""
@register.simple_tag
def maven_media_crop(url, dim):
    r"""
    Crop and scale a media image file.  
    
    Usage::

        {% maven %}
        <img src="{% maven_media_crop 'path/to/file.png' '150x120' %}">

    Also works with template variables:

        {% maven %}
        {% for img_file_path in img_file_paths %}
            <img src="{% maven_media_crop img_file_path '150x120' %}">
        {% endfor %}

    """
    orig_img_file_url = f'{settings.MEDIA_URL}{url}'
    dim_list = dim.split('x')
    w = int(str(dim_list[0]).strip())
    h = int(str(dim_list[1]).strip())
    orig_img_file_path = fs.fix_path_name(fs.join_names(settings.MEDIA_ROOT, url))
    new_img_file_path = get_cropped_image(orig_img_file_path, w, h)
    new_img_file_url_parts = orig_img_file_url.split('/')
    new_img_file_name = fs.get_file_name(new_img_file_path)
    new_img_file_url_parts.pop()
    new_img_file_url_parts.append('.thumb')
    new_img_file_url_parts.append(new_img_file_name)
    new_img_file_path = '/'.join(new_img_file_url_parts)
    return f'{new_img_file_path}'

r"""
 _                       _       _         _
| |_ ___ _ __ ___  _ __ | | __ _| |_ ___  | |_ __ _  __ _ _
| __/ _ \ '_ ` _ \| '_ \| |/ _` | __/ _ \ | __/ _` |/ _` (_)
| ||  __/ | | | | | |_) | | (_| | ||  __/ | || (_| | (_| |_
 \__\___|_| |_| |_| .__/|_|\__,_|\__\___|  \__\__,_|\__, (_)
                  |_|                               |___/
                    _ _         _   _
 _ __ ___   ___  __| (_) __ _  | |_| |__   ___ _ __ ___   ___    ___ ___ ___
| '_ ` _ \ / _ \/ _` | |/ _` | | __| '_ \ / _ \ '_ ` _ \ / _ \  / __/ __/ __|
| | | | | |  __/ (_| | | (_| | | |_| | | |  __/ | | | | |  __/ | (__\__ \__ \
|_| |_| |_|\___|\__,_|_|\__,_|  \__|_| |_|\___|_| |_| |_|\___|  \___|___/___/

"""

@register.simple_tag
def maven_theme_css():
    r"""
    Return the theme CSS as defined in settings, else maven-charcoal.css.
    """
    theme = 'charcoal'
    try:theme = settings.MEDIA_MAVEN['THEME']
    except: pass
    css_file = settings.STATIC_URL + f'maven/maven-{theme}.css'
    return css_file
