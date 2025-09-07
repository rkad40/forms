# admin.py
from django.urls import reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from .models import (
    OCIAParticipantSettings,
    OCIAParticipant, OCIAParticipantMarriage, OCIAParticipantParent,
    OCIAParticipantEngagement, OCIAParticipantQuestions, OCIAParticipantReligion
)

@admin.register(OCIAParticipantSettings)
class OCIAPartipantSiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('liturgical_year', 'access_code', 'enable_editing')

    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not OCIAParticipantSettings.objects.exists()

    def changelist_view(self, request, extra_context=None):
        # Redirect to edit view if instance exists
        obj = OCIAParticipantSettings.objects.first()
        if obj:
            return HttpResponseRedirect(reverse('admin:ocia_participant_ociaparticipantsettings_change', args=[obj.id]))
        return super().changelist_view(request, extra_context)

class MarriageInline(admin.StackedInline):
    model = OCIAParticipantMarriage
    extra = 0

class ParentInline(admin.StackedInline):
    model = OCIAParticipantParent
    max_num = 2
    extra = 0

class EngagementInline(admin.StackedInline):
    model = OCIAParticipantEngagement
    max_num = 1
    extra = 0

class QuestionsInline(admin.StackedInline):
    model = OCIAParticipantQuestions
    max_num = 1

class ReligionInline(admin.StackedInline):
    model = OCIAParticipantReligion
    max_num = 1

@admin.register(OCIAParticipant)
class OCIAParticipantAdmin(admin.ModelAdmin):
    inlines = [ReligionInline, MarriageInline, EngagementInline, ParentInline, QuestionsInline]
    list_display = ['full_name', 'first_name', 'last_name', 'liturgical_year', 'age', 'email', 'phone', 'can_text']
    list_filter = ['liturgical_year']
    search_fields = ['first_name', 'last_name', 'email']
    list_display_links = ['full_name']
    ordering = ['-liturgical_year', 'last_name', 'first_name']