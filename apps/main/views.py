from django.shortcuts import render
from main.models import SiteSettings

def home(request):
    site = SiteSettings.fetch()
    context = dict(
        site=site,
    )
    return render(request, template_name='main/home.html', context=context)
