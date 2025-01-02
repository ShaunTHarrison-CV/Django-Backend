import json

from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.test import APITestCase


class TestModelCompany(APITestCase):

    fixtures = ["unit_test.json"]

    def setUp(self):
        self.user = User.objects.get(username="User1")
        self.client.force_login(self.user)

    def test_list_companies(self):
        response = self.client.get("/api/companies/")
        assert response.status_code == 200
        with open("app/tests/views/fixtures/list_companies_user.json") as infile:
            assert response.json() == json.load(infile)

        # Superusers can see ID and admin info
        self.client.force_login(User.objects.get(username="admin"))
        response = self.client.get("/api/companies/")
        assert response.status_code == 200
        with open("app/tests/views/fixtures/list_companies_admin.json") as infile:
            assert response.json() == json.load(infile)

    def test_list_companies_pagination(self):
        call_command("loaddata", "app/fixtures/bulk_companies.json")
        # Page 1, previous is null
        with open("app/tests/views/fixtures/list_companies_page_1.json") as infile:
            assert self.client.get("/api/companies/").json() == json.load(infile)
        # Page 2, previous and next are populated
        with open("app/tests/views/fixtures/list_companies_page_2.json") as infile:
            assert self.client.get("/api/companies/?page=2").json() == json.load(infile)
        # Page 3, next is null
        with open("app/tests/views/fixtures/list_companies_page_2.json") as infile:
            assert self.client.get("/api/companies/?page=2").json() == json.load(infile)
        # Custom page size
        with open("app/tests/views/fixtures/list_companies_page_size.json") as infile:
            assert self.client.get("/api/companies/?pageSize=10").json() == json.load(infile)

    def test_list_companies_filter(self):
        assert False

    def test_retrieve_company(self):
        assert False

    def test_create_company(self):
        assert False

    def test_update_company(self):
        # Test update with valid and invalid user
        assert False

    def test_delete_company(self):
        # Test delete with valid and invalid user
        # Test delete of company that still has products
        assert False
