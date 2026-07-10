from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.urls import include, path

urlpatterns = [
    
    path("", include("django_prometheus.urls")),
    
    path("admin/", admin.site.urls),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",          
    ),

    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    
    path(
        "api/payments/",
        include("apps.payments.urls"),
    ),
]