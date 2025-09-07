from django import forms
from django.conf import settings
from cronos import epoch

TS = epoch(int)
THEME = 'charcoal'
try:THEME = settings.MEDIA_MAVEN['THEME']
except: pass

class MavenStandardMixin(forms.TextInput):
    input_type = 'text'  # Subclasses must define this.
    class Media:
        css = {
            'all': (
                settings.STATIC_URL + 'dialog/dialog.css',
                settings.STATIC_URL + f'maven/maven-{THEME}.css?version={TS}',
            )
        }
        js = (
            settings.STATIC_URL + 'admin/js/vendor/jquery/jquery.js',
            settings.STATIC_URL + 'admin/js/jquery.init.js',
            settings.STATIC_URL + 'fontawesome/all.min.js',
            settings.STATIC_URL + f'dialog/dialog.js?version={TS}',
            settings.STATIC_URL + f'maven/maven-1.3.js?version={TS}',
        )
    def __init__(self, attrs=None, url=''):
        if attrs is not None:
            attrs = attrs.copy()
            self.input_type = attrs.pop('type', self.input_type)
        super().__init__(attrs)
        self.url = url

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        context['widget']['url'] = self.url
        return context

class MavenAdminMixin(forms.TextInput):
    input_type = 'text'  # Subclasses must define this.
    class Media:
        css = {
            'all': (
                settings.STATIC_URL + 'dialog/dialog.css',
                settings.STATIC_URL + f'maven/maven-admin.css?version={TS}',
            )
        }
        js = (
            settings.STATIC_URL + 'fontawesome/all.min.js',
            settings.STATIC_URL + f'dialog/dialog.js?version={TS}',
            settings.STATIC_URL + f'maven/maven-1.3.js?version={TS}',
        )
    def __init__(self, attrs=None, url=''):
        if attrs is not None:
            attrs = attrs.copy()
            self.input_type = attrs.pop('type', self.input_type)
        super().__init__(attrs)
        self.url = url

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['type'] = self.input_type
        context['widget']['url'] = self.url
        return context

class MavenDirSelectorWidget(MavenStandardMixin):
    template_name = 'maven/widget/dir-selector-widget-standard.html'

class MavenFileSelectorWidget(MavenStandardMixin):
    template_name = 'maven/widget/file-selector-widget-standard.html'

class MavenImageSelectorWidget(MavenStandardMixin):
    template_name = 'maven/widget/image-selector-widget-standard.html'

class MavenDirSelectorAdminWidget(MavenAdminMixin):
    template_name = 'maven/widget/dir-selector-widget-admin.html'

class MavenFileSelectorAdminWidget(MavenAdminMixin):
    template_name = 'maven/widget/file-selector-widget-admin.html'

class MavenImageSelectorAdminWidget(MavenAdminMixin):
    template_name = 'maven/widget/image-selector-widget-admin.html'