import json

from django.contrib.auth.models import User, Group
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
        for term, value in [
            ("code", "ABC001"),
            ("code__icontains", "ABC"),
            ("name", "ABC Company"),
            ("name__icontains", "ABC"),
        ]:
            with open(f"app/tests/views/fixtures/list_companies_filter_{term}.json") as infile:
                assert self.client.get("/api/companies/", query_params={term: value}).json() == json.load(infile)

    def test_retrieve_company(self):
        response = self.client.get("/api/companies/ABC001/")
        assert response.status_code == 200
        assert response.json() == {"code": "ABC001", "name": "ABC Company"}

        self.client.force_login(User.objects.get(username="admin"))
        response = self.client.get("/api/companies/ABC001/")
        assert response.status_code == 200
        assert response.json() == {
            "code": "ABC001",
            "id": 1,
            "name": "ABC Company",
            "owner_groups": [{"name": "company_ABC001"}, {"name": "company_FX_Supergroup"}],
        }

    def test_create_company(self):
        request_body = {
            "code": "UNT",
            "owner_groups": [
                {"name": "company_ABC002"},
            ],
        }

        # Check default serializer behaviour
        response = self.client.post("/api/companies/", data=json.dumps(request_body), content_type="application/json")
        assert response.status_code == 400
        assert response.json() == {"name": ["This field is required."]}

        # User1 is not part of group company_ABC002, so request is rejected
        request_body["name"] = "Unit Test Company"
        response = self.client.post("/api/companies/", data=json.dumps(request_body), content_type="application/json")
        assert response.status_code == 400
        assert response.json() == {"owner_groups": ["You must be in at least one of the specified group."]}

        # Add User1 to appropriate group, so request is approved
        self.user.groups.add(Group.objects.get(name="company_ABC002"))
        response = self.client.post("/api/companies/", data=json.dumps(request_body), content_type="application/json")
        assert response.status_code == 201
        assert response.json() == {
            "code": "UNT",
            "id": 4,
            "name": "Unit Test Company",
            "owner_groups": [{"name": "company_ABC002"}],
        }

        # Superusers can create companies for groups that they're not part of
        request_body["code"] = "UNT002"
        self.client.force_login(User.objects.get(username="admin"))
        response = self.client.post("/api/companies/", data=json.dumps(request_body), content_type="application/json")
        assert response.status_code == 201
        assert response.json() == {
            "code": "UNT002",
            "id": 5,
            "name": "Unit Test Company",
            "owner_groups": [{"name": "company_ABC002"}],
        }

    def test_update_company(self):
        # Test update with valid and invalid user
        assert False

    def test_delete_company(self):
        # Test delete with valid and invalid user
        # Test delete of company that still has products
        assert False
