from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings
from cronos import Time, epoch

register = template.Library()



