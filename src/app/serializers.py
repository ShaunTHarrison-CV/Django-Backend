from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app import models


class CompanyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]

    # Override so serializer doesn't complain about existing group names, as that is allowed here
    name = serializers.CharField()


class AdminCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = "__all__"

    owner_groups = CompanyGroupSerializer(many=True, min_length=1)
    total_products = serializers.IntegerField(read_only=True)

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=raise_exception)
        request_user = self.context["request"].user
        if request_user.is_superuser:
            return True  # Superusers bypass group checks

        # User must be in at least one of the groups defined in the request,
        # and one group defined on the instance being updated
        request_groups = [i["name"] for i in self.validated_data.get("owner_groups", [])]
        user_groups = [i.name for i in request_user.groups.all()]
        instance_groups = [i.name for i in self.instance.owner_groups.all()] if self.instance else []
        request_groups_invalid = len(set(request_groups).intersection(user_groups)) == 0
        instance_groups_invalid = len(instance_groups) > 0 and len(set(instance_groups).intersection(user_groups)) == 0

        if raise_exception and any([request_groups_invalid, instance_groups_invalid]):
            raise ValidationError(
                {
                    "owner_groups": [
                        "You must be in at least one of the specified groups when creating or updating Company records."
                    ]
                }
            )
        return not any([request_groups_invalid, instance_groups_invalid])

    def create(self, validated_data):
        """Create a Company object, then get or create Group objects and associate them with the company"""
        owner_groups = [i["name"] for i in validated_data.pop("owner_groups", [])]
        instance = super().create(validated_data)
        for group_name in owner_groups:
            instance.owner_groups.add(Group.objects.get_or_create(name=group_name)[0])
        return instance

    def update(self, instance, validated_data):
        """
        Update a Company object, then get or create Group objects and associate them with the company,
        removing any old groups that were not included in the request
        """
        owner_groups = [i["name"] for i in validated_data.pop("owner_groups", [])]
        instance = super().update(instance, validated_data)
        # If groups were specified in the request (they may not be in PATCH requests), update the groups
        if owner_groups:
            for group_name in owner_groups:
                instance.owner_groups.add(Group.objects.get_or_create(name=group_name)[0])
            for group in instance.owner_groups.all():
                if group.name not in owner_groups:
                    instance.owner_groups.remove(group)
        return instance


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        exclude = ["id", "owner_groups"]
    total_products = serializers.IntegerField(read_only=True)
