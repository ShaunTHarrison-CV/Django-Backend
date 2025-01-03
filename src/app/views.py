from rest_framework import viewsets, mixins

from app import models, serializers, filter_backends


class CreateWithAuthenticatedUserMixin(mixins.CreateModelMixin):
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = models.Company.objects.all().order_by("code")
    serializer_class = serializers.CompanySerializer
    filterset_class = filter_backends.CompanyFilter
    lookup_field = "code"

    def get_serializer_class(self):
        if self.request.user.is_superuser or self.action in ["create", "partial_update", "update"]:
            return serializers.AdminCompanySerializer
        return super().get_serializer_class()
