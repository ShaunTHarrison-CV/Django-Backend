from rest_framework import serializers

from app import models


class AdminCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        exclude = ["id", "owner_groups"]



