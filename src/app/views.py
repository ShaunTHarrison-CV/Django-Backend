from rest_framework import viewsets, mixins

from app import models, serializers


class CreateWithAuthenticatedUserMixin(mixins.CreateModelMixin):
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = models.Company.objects.all().order_by("code")
    serializer_class = serializers.CompanySerializer

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return serializers.AdminCompanySerializer
        return super().get_serializer_class()
