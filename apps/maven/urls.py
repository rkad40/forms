from django.urls import path

from . import views as view

urlpatterns = [
  path('', view.Test, name='maven-test'),
  path('refresh', view.AjaxRefresh, name='maven-refresh'),
  path('explorer', view.ExplorerRoot, name='maven-explorer-root'),
  path('explorer/<path:path>', view.Explorer, name='maven-explorer-path'),
  # path('test/widgets', view.TestWidgets, name='maven-test-widgets'),
]
