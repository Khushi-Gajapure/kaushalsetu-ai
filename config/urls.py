from django.contrib import admin
from django.urls import path
from core.views import dashboard, recommendations


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
   path(
    "recommendations/",
    recommendations,
    name="recommendations"
),
    
]