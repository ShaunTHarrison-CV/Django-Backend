import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from app.models import Company


class TestModelCompany(TestCase):

    fixtures = ["unit_test.json"]

    def setUp(self):
        self.user = User.objects.get(username="test-admin")

    def test_create(self):
        company = Company.objects.create(owner=self.user, code="CP001", name="Company 1")
        assert company.owner == self.user
        assert company.code == "CP001"
        assert company.name == "Company 1"

    def test_create_duplicate_code(self):
        with pytest.raises(IntegrityError) as e:
            Company.objects.create(owner=self.user, code="FXC001", name="Company 1")
        assert e.value.args == ("UNIQUE constraint failed: app_company.code",)

    def test_property_total_product(self):
        assert Company.objects.get(code="FXC001").total_products == 2
        assert Company.objects.get(code="FXC002").total_products == 0

    def test_str(self):
        assert str(Company.objects.get(code="FXC001")) == "FXC001"
