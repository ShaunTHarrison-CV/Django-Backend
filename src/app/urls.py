from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions

from app import views

router = routers.DefaultRouter()
router.register("companies", views.CompanyViewSet)

swagger_view = get_schema_view(
    openapi.Info(
        title="Shaun Harrison CV API",
        default_version='v1',
        description="Example API",
        contact=openapi.Contact(email="shaun.harrison@live.co.uk"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', swagger_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger<format>/', swagger_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', swagger_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("api/", include(router.urls)),
]
