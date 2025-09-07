from django.shortcuts import render
from django.http import HttpResponse
from main.models import SiteSettings

def home(request):
    config = SiteSettings.fetch()
    context = dict(
        title='Sacred Heart Forms',
        page='base',
        config=config,
    )
    return render(request, template_name='main/base.html', context=context)