from django import forms
# from django.forms import ModelForm
# from django.conf import settings
# from django.forms.widgets import Widget
# from django.template.loader import render_to_string
# from django.utils.safestring import mark_safe

from .widgets import MavenFileSelectorWidget, MavenImageSelectorWidget, MavenDirSelectorWidget

class TestWidgetsForm(forms.Form):
    media_file = forms.CharField(widget=MavenFileSelectorWidget(url='Temp'), required=False)
    media_image = forms.CharField(widget=MavenImageSelectorWidget(url='Images/autodoc'), required=False)
    media_dir = forms.CharField(widget=MavenDirSelectorWidget(url=''), required=False)

