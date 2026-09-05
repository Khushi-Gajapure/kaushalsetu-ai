from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core.views import dashboard, recommendations, upload_material, take_quiz

urlpatterns = [

    path("admin/", admin.site.urls),

    path(
        "",
        dashboard,
        name="dashboard"
    ),

    path(
        "recommendations/",
        recommendations,
        name="recommendations"
    ),

    path(
        "upload-material/",
        upload_material,
        name="upload_material"
    ),
    path(
    "quiz/<int:quiz_id>/",
    take_quiz,
    name="take_quiz"
    ),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )