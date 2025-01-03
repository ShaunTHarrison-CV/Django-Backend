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

    owner_groups = CompanyGroupSerializer(many=True)

    def is_valid(self, *, raise_exception=False):
        # Verify request body is valid
        super().is_valid(raise_exception=raise_exception)

        # Verify user making the request is a superuser, or is in at least one of the groups belonging to the Company
        request_user = self.context["request"].user
        request_groups = [i["name"] for i in self.validated_data.get("owner_groups", [])]
        user_groups = [i.name for i in request_user.groups.all()]
        groups_invalid = len(set(request_groups).intersection(user_groups)) == 0 and request_user.is_superuser is False

        if raise_exception and groups_invalid:
            raise ValidationError({"owner_groups": ["You must be in at least one of the specified group."]})
        return not groups_invalid

    def create(self, validated_data):
        # Create Company object, then associate groups, creating them if they don't exist
        owner_groups = validated_data.pop("owner_groups")
        instance = super().create(validated_data)
        for group_name in owner_groups:
            instance.owner_groups.add(Group.objects.get_or_create(name=group_name["name"])[0])
        return instance


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        exclude = ["id", "owner_groups"]
