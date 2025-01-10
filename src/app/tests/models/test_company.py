from unittest.mock import patch, call

import pytest
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.test import TestCase

from app.models import Company


class TestModelCompany(TestCase):

    fixtures = ["unit_test.json"]

    def setUp(self):
        self.group = Group.objects.get(name="company_ABC001")

    def test_create(self):
        company = Company.objects.create(code="CP001", name="Company 1")
        company.owner_groups.add(self.group)
        assert company.code == "CP001"
        assert company.name == "Company 1"
        assert company.owner_groups.all()[0] == self.group

    def test_create_duplicate_code(self):
        with pytest.raises(IntegrityError) as e:
            Company.objects.create(code="ABC001", name="Company 1")
        assert e.value.args == ("UNIQUE constraint failed: app_company.code",)

    def test_property_total_product(self):
        assert Company.objects.get(code="ABC001").total_products == 1
        assert Company.objects.get(code="ABC002").total_products == 1
        assert Company.objects.get(code="FXC001").total_products == 0

    def test_str(self):
        assert str(Company.objects.get(code="ABC001")) == "ABC001"

    @patch("app.models.random.choices", side_effect=["code_1", "duplicate_code", "code_2"])
    def test_generate_code(self, patched_choices):
        """Generate a code. First call is valid. Second generates a collision, forcing a loop"""
        Company.objects.create(name="UnitTest", code="duplicate_code")
        assert Company.generate_code() == "code_1"
        assert Company.generate_code() == "code_2"
        assert patched_choices.call_count == 3
        patched_choices.assert_has_calls(
            [
                call("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8),
                call("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8),
                call("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8),
            ]
        )
