from rest_framework import viewsets, mixins

from app import models, serializers, filter_backends


class MultiTenantedViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        # Superusers bypass multi-tenanting restrictions, allowing site administration
        if self.request.user.is_superuser:
            return super().get_queryset()
        # Filter results so only records related to groups the user is in. If a user attempts to view/change a record
        # that they don't have access to, the API pretends that it doesn't exist in the DB.
        filter_arg = {
            models.Company: "owner_groups__in",
            models.Product: "company__owner_groups__in",
            models.Transaction: "product__company__owner_groups__in",
        }[self.queryset.model]
        return super().get_queryset().filter(**{filter_arg: self.request.user.groups.all()})


class CreateWithAuthenticatedUserMixin(mixins.CreateModelMixin):
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class CompanyViewSet(MultiTenantedViewSet):
    queryset = models.Company.objects.all().order_by("code")
    serializer_class = serializers.CompanySerializer
    filterset_class = filter_backends.CompanyFilter
    lookup_field = "code"
