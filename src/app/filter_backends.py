from django_filters import rest_framework as filters

from app import models


class CompanyFilter(filters.FilterSet):
    class Meta:
        model = models.Company
        fields = {
            'code': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
        }
