from django.urls import path
import ocia_participant.views as view
from django.views.generic import TemplateView

urlpatterns = [
    path("participant", view.OCIAParticipantStartView, name="OCIAParticipantStartView"), 
    path("test", view.OCIAParticipantTestView, name="OCIAParticipantTestView"), 
    path("delete/<str:category>/<int:id>", view.OCIAParticipantDeleteRecordView, name="OCIAParticipantDeleteRecordView"), 
    path("delete", view.OCIAParticipantDeleteRecordNoArgView, name="OCIAParticipantDeleteRecordNoArgView"), 
    path("login", view.OCIAParticipantLoginView, name="OCIAParticipantLoginView"), 
    path("access/notification/existing", view.OCIAParticipantEmailAccessExistingView, name="OCIAParticipantEmailAccessExistingView"), 
    path("access/notification/new", view.OCIAParticipantEmailAccessNewView, name="OCIAParticipantEmailAccessNewView"), 
    path("access/confirmation/existing/<str:code>", view.OCIAParticipantAccessConfirmationExistingView, name="OCIAParticipantAccessConfirmationExistingView"), 
    path("access/confirmation/new/<str:code>", view.OCIAParticipantAccessConfirmationNewView, name="OCIAParticipantAccessConfirmationNewView"), 
    path("logout", view.OCIAParticipantLogoutView, name="OCIAParticipantLogoutView"), 
    path("create", view.OCIAParticipantCreateView, name="OCIAParticipantCreateView"), 
    path("update", view.OCIAParticipantUpdateView, name="OCIAParticipantUpdateView"),
    path("religion/create", view.OCIAParticipantReligionCreateView, name="OCIAParticipantReligionCreateView"), 
    path("religion/update", view.OCIAParticipantReligionUpdateView, name="OCIAParticipantReligionUpdateView"),
    path("engagement/create", view.OCIAParticipantEngagementCreateView, name="OCIAParticipantEngagementCreateView"), 
    path("engagement/update", view.OCIAParticipantEngagementUpdateView, name="OCIAParticipantEngagementUpdateView"),
    path("engagement/add", view.OCIAParticipantEngagementAddView, name="OCIAParticipantEngagementAddView"),
    path("marriage/create", view.OCIAParticipantMarriageCreateView, name="OCIAParticipantMarriageCreateView"),
    path("marriage/add", view.OCIAParticipantMarriageAddView, name="OCIAParticipantMarriageAddView"),
    path("marriage/update/<int:pk>", view.OCIAParticipantMarriageUpdateView, name="OCIAParticipantMarriageUpdateView"),
    path("parent/create", view.OCIAParticipantParentCreateView, name="OCIAParticipantParentCreateView"),
    path("parent/add", view.OCIAParticipantParentAddView, name="OCIAParticipantParentAddView"),
    path("parent/update/<int:pk>", view.OCIAParticipantParentUpdateView, name="OCIAParticipantParentUpdateView"),
    path("questions/create", view.OCIAParticipantQuestionsCreateView, name="OCIAParticipantQuestionsCreateView"),
    path("questions/update", view.OCIAParticipantQuestionsUpdateView, name="OCIAParticipantQuestionsUpdateView"),
    path("error", view.OCIAParticipantErrorView, name="OCIAParticipantErrorView"),
    path("navigation", view.OCIAParticipantNavigationView, name="OCIAParticipantNavigationView"), 
]