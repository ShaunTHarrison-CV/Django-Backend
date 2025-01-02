import pytest
from django.db import IntegrityError
from django.test import TestCase

from app.models import Company, Product


class TestModelProduct(TestCase):

    fixtures = ["unit_test.json"]

    def setUp(self):
        self.company = Company.objects.get(code="ABC001")

    def test_create(self):
        product = Product.objects.create(company=self.company, code="PRD001", name="Product 1", price=123)
        assert product.company == self.company
        assert product.code == "PRD001"
        assert product.name == "Product 1"
        assert product.price == 123

    def test_create_duplicate_code(self):
        # Existing code in different company, allow creation
        Product.objects.create(
            company=Company.objects.get(code="ABC002"),
            code="FXP001",
            name="Product 1",
            price=123,
        )

        # Duplicate code within company, raise error
        with pytest.raises(IntegrityError) as e:
            Product.objects.create(company=self.company, code="FXP001", name="Product 1", price=123)
        assert e.value.args == ("UNIQUE constraint failed: app_product.company_id, app_product.code",)

    def test_str(self):
        assert str(Product.objects.get(code="FXP001")) == "FXP001 - ABC001"
