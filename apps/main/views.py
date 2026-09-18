from django.shortcuts import render
from main.models import SiteSettings

def home(request):
    site = SiteSettings.fetch()
    visibility = 0
    if request.user.is_authenticated and request.user.is_staff:
        visibility = 2 if request.user.is_superuser else 1
    context = dict(
        site=site,
        home_page_links=site.home_page_links.filter(
            active=True,
            verbosity__lte=visibility,
        ),
    )
    return render(request, template_name='main/home.html', context=context)
