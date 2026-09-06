from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core.views import (
    landing,
    KaushalSetuLoginView,
    kaushalsetu_logout,
    dashboard,
    recommendations,
    upload_material,
    take_quiz,
    profile,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing, name="landing"),
    path("login/", KaushalSetuLoginView.as_view(), name="login"),
    path("logout/", kaushalsetu_logout, name="logout"),
    path("profile/", profile, name="profile"),
    path("dashboard/", dashboard, name="dashboard"),
    path("recommendations/", recommendations, name="recommendations"),
    path("upload-material/", upload_material, name="upload_material"),
    path("quiz/<int:quiz_id>/", take_quiz, name="take_quiz"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)