from django.contrib import admin
from django.urls import path

from work_in_progress.app.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
