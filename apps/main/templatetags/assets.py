import fs
from django import template
from django.conf import settings
from cronos import epoch
from django.template.defaultfilters import stringfilter
from cronos import Time, epoch
from django.forms.widgets import CheckboxInput

import typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    class SettingsFake:
        HTTP_ROOT = ''
        STATIC_URL = ''
        MEDIA_URL = ''
        DEBUG = True
    settings = SettingsFake

register = template.Library()

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)

@register.simple_tag
def site_debug():
    return 'true' if settings.DEBUG else 'false'

@register.simple_tag
def http_base_url():
    return f'{settings.HTTP_ROOT}'

@register.simple_tag
def http_static_url():
    return f'{settings.HTTP_ROOT}{settings.STATIC_URL}'

@register.simple_tag
def static(url):
    new_url = f'{settings.STATIC_URL}{url}'
    return new_url  

@register.simple_tag
def static_reload(url):
    new_url = f'{settings.STATIC_URL}{url}'
    if settings.DEBUG: new_url += f'?id={epoch(int)}'
    return new_url  

@register.simple_tag
def http_media_url():
    return f'{settings.HTTP_ROOT}{settings.MEDIA_URL}'

@register.simple_tag
def media(url):
    new_url = f'{settings.MEDIA_URL}{url}'
    if settings.DEBUG: new_url += f'?id={epoch(int)}'
    return new_url  

@register.simple_tag
def media_reload(url):
    new_url = f'{settings.MEDIA_URL}{url}'
    if settings.DEBUG: new_url += f'?id={epoch(int)}'
    return new_url  

MESSAGE = {
        'success': dict(label='SUCCESS', type='success',   glyph=f'<i class="fas fa-check-circle"></i>'),
        'error':   dict(label='ERROR',   type='danger',    glyph=f'<i class="fas fa-exclamation-circle"></i>'),
        'warning': dict(label='WARNING', type='warning',   glyph=f'<i class="fas fa-exclamation-triangle"></i>'),
        'info':    dict(label='NOTE',    type='info',      glyph=f'<i class="fas fa-info-circle"></i>'),
        'debug':   dict(label='NOTE',    type='secondary', glyph=f'<i class="fas fa-bug"></i>'),
    }

@register.filter(name='alert')
@stringfilter
def alert(value, arg):
    r'''
    ## Description
    Defines an `alert` filter for use with template tags.  This filter is used convert message.tags into a label, 
    Bootstrap alert type and image.  Using the template syntax `{% for message in messages %}...{% endfor %}`, 
    `message.tags` will be one of "success", "error", "warning", "info" or "debug".  For example, if `message.tags` is
    "error":

    - `{{ message.tags|alert:'label' }}` = "ERROR" 
    - `{{ message.tags|alert:'type' }}` = "danger"
    - `{{ message.tags|alert:'img' }}` = "main/img/misc/error.png"
    
    Here is an example of how to use it:

    ```html
    {% load static %}
    {% load main_tags %}
    {% get_static_prefix as STATIC_PREFIX %}

    {% if messages %}
    <div class="flash messages" style="padding: 0;">
        {% for message in messages %}
        <div class="flash messages" style="padding: 0; margin: 0;">
            <div class="alert alert-{{ message.tags|alert:'type' }} alert-dismissible fade show" style="width: 100%; margin: 0 0 5px 0;" role="alert">
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
                <img src="{{ STATIC_PREFIX }}{{ message.tags|alert:'img' }}" style="position: relative; left: -3px; top: -1px;}">
                <strong>{{ message.tags|alert:'label' }}</strong>: {{ message }}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}	
    ```
    '''
    if value not in MESSAGE: value = 'info'
    return MESSAGE[value][arg]

@register.filter(name='json')
def json(obj):
    import json
    txt = json.dumps(obj, indent=None)
    return txt

@register.filter(name='sortkeys')
def sortkeys(obj):
    keys = sorted(obj)
    for key in keys:
     yield (key, obj[key])

@register.filter(name='plusminus')
def plusminus(val):
    return f'+{val}' if val >= 0 else f'{val}'

@register.filter(name='fetch')
def fetch(data, *args):
    print(args)
    for arg in args:
        if arg not in data: return ''
        data = data[arg]
    return data
