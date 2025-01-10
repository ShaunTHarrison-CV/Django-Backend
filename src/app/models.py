import random
import string

from django.contrib.auth.models import User, Group
from django.db import models


class Company(models.Model):
    owner_groups = models.ManyToManyField(Group)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.code

    @property
    def total_products(self):
        return self.product_set.count()

    @staticmethod
    def generate_code():
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if Company.objects.filter(code=code).count() == 0:
                return code


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    price = models.IntegerField()  # Price stored in pence to avoid floating point errors
    active_listing = models.BooleanField(default=True)  # Inactive listing are no longer for sale

    class Meta:
        unique_together = ("company", "code")

    def __str__(self):
        return f"{self.code} - {self.company.code}"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    code = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
