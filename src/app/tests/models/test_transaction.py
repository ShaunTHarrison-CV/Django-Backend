import datetime

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from freezegun import freeze_time

from app.models import Product, Transaction


class TestModelTransaction(TestCase):

    fixtures = ["unit_test.json"]

    def setUp(self):
        self.user = User.objects.get(username="UserABC001")
        self.product = Product.objects.get(code="FXP001")

    @freeze_time("2025-01-01 18:00:00")
    def test_create(self):
        transaction = Transaction.objects.create(user=self.user, product=self.product, code="REF001", quantity=5)
        assert transaction.user == self.user
        assert transaction.product == self.product
        assert transaction.code == "REF001"
        assert transaction.quantity == 5
        assert transaction.timestamp == datetime.datetime(2025, 1, 1, 18, tzinfo=datetime.timezone.utc)

    def test_create_duplicate_code(self):
        with pytest.raises(IntegrityError) as e:
            Transaction.objects.create(user=self.user, product=self.product, code="FXT001", quantity=5)
        assert e.value.args == ("UNIQUE constraint failed: app_transaction.code",)

    def test_str(self):
        assert str(Transaction.objects.get(code="FXT001")) == "FXT001"
