import json
from unittest.mock import patch

from django.contrib.auth.models import User, Group
from django.core.management import call_command
from rest_framework.test import APITestCase

from app.models import Company


class TestViewCompany(APITestCase):
    fixtures = ["unit_test.json"]

    def test_unauthenticated_request(self):
        for method, url in [
            (self.client.get, "/api/companies/"),
            (self.client.post, "/api/companies/"),
            (self.client.put, "/api/companies/ABC001/"),
            (self.client.patch, "/api/companies/ABC001/"),
        ]:
            response = method(url)
            assert response.status_code == 403

    def test_list_companies(self):
        """Test that the appropriate companies are returned, based on the groups the users are in"""
        for username in ["admin", "UserABC001", "UserABCSuper", "UserABCFXC1", "UserFXC002"]:
            self.client.force_login(User.objects.get(username=username))
            response = self.client.get("/api/companies/")
            assert response.status_code == 200
            with open(f"app/tests/views/fixtures/list_companies_{username}.json") as infile:
                assert response.json() == json.load(infile)

    def test_list_companies_pagination(self):
        """Test that responses are correctly paginated and the next/previous values are populated correctly"""
        self.client.force_login(User.objects.get(username="admin"))
        call_command("loaddata", "app/fixtures/bulk_companies.json")
        # Page 1, previous is null
        with open("app/tests/views/fixtures/list_companies_page_1.json") as infile:
            assert self.client.get("/api/companies/").json() == json.load(infile)
        # Page 2, previous and next are populated
        with open("app/tests/views/fixtures/list_companies_page_2.json") as infile:
            assert self.client.get("/api/companies/?page=2").json() == json.load(infile)
        # Page 3, next is null
        with open("app/tests/views/fixtures/list_companies_page_3.json") as infile:
            assert self.client.get("/api/companies/?page=3").json() == json.load(infile)
        # Custom page size
        with open("app/tests/views/fixtures/list_companies_page_size.json") as infile:
            assert self.client.get("/api/companies/?pageSize=10").json() == json.load(infile)

    def test_list_companies_filter(self):
        """Test each supported querystring filter filters correctly"""
        self.client.force_login(User.objects.get(username="admin"))
        # Check each single filter
        for term, value in [
            ("code", "ABC001"),
            ("code__icontains", "ABC"),
            ("name", "ABC Company"),
            ("name__icontains", "ABC"),
        ]:
            with open(f"app/tests/views/fixtures/list_companies_filter_{term}.json") as infile:
                assert self.client.get("/api/companies/", query_params={term: value}).json() == json.load(infile)
        # Check dual filters
        with open("app/tests/views/fixtures/list_companies_filter_combined.json") as infile:
            query = {"name__icontains": "ABC", "code__icontains": "002"}
            assert self.client.get("/api/companies/", query_params=query).json() == json.load(infile)

    def test_retrieve_company(self):
        response_200 = {
            "code": "FXC001",
            "name": "Fixture Company 1",
            "owner_groups": [{"name": "company_FXC001"}],
            "total_products": 0,
        }
        response_404 = {"detail": "No Company matches the given query."}

        for username, expected_status, expected_response in [
            ("admin", 200, response_200),
            ("UserABC001", 404, response_404),
            ("UserABCSuper", 404, response_404),
            ("UserABCFXC1", 200, response_200),
            ("UserFXC002", 404, response_404),
        ]:
            self.client.force_login(User.objects.get(username=username))
            response = self.client.get("/api/companies/FXC001/")
            assert response.status_code == expected_status
            assert response.json() == expected_response

        # Record that actually doesn't exist, should behave the same as existing but not allowed
        response = self.client.get("/api/companies/FXC002/")
        assert response.status_code == 404
        assert response.json() == response_404

    @patch("app.serializers.models.Company.generate_code", return_value="UNT001")
    def test_create_company(self, *patches):
        user = User.objects.get(username="UserABC001")
        request_body = {
            "name": "Unit Test Company",
            "owner_groups": [
                {"name": "company_ABC002"},
                {"name": "company_UnitTest"},
            ],
        }

        # Check default serializer behaviour
        self.client.force_login(user)
        response = self.client.post("/api/companies/", data=json.dumps({}), content_type="application/json")
        assert response.status_code == 400
        assert response.json() == {
            "name": ["This field is required."],
            "owner_groups": ["This field is required."],
        }
        response = self.client.post(
            "/api/companies/", data=json.dumps({"owner_groups": []}), content_type="application/json"
        )
        assert response.status_code == 400
        assert response.json() == {
            "name": ["This field is required."],
            "owner_groups": {"non_field_errors": ["Ensure this field has at least 1 elements."]},
        }

        # UserABC001 is not part of group company_ABC002, so request is rejected
        request_body["name"] = "Unit Test Company"
        response = self.client.post("/api/companies/", data=json.dumps(request_body), content_type="application/json")
        assert response.status_code == 400
        assert response.json() == {
            "owner_groups": [
                "You must be in at least one of the specified groups when creating or updating Company records."
            ]
        }

        # Add UserABC001 to appropriate group, so request is approved
        # Code is auto-generated by the backend, not by user request
        user.groups.add(Group.objects.get(name="company_ABC002"))
        response = self.client.post("/api/companies/", data=json.dumps(request_body), content_type="application/json")
        assert response.status_code == 201
        assert response.json() == {
            "code": "UNT001",
            "name": "Unit Test Company",
            "total_products": 0,
            "owner_groups": [{"name": "company_ABC002"}, {"name": "company_UnitTest"}],
        }

        # Superusers can create companies for groups that they're not part of and define codes directly
        self.client.force_login(User.objects.get(username="admin"))
        request_body["code"] = "UNT002"
        response = self.client.post("/api/companies/", data=json.dumps(request_body), content_type="application/json")
        assert response.status_code == 201
        assert response.json() == {
            "code": "UNT002",
            "name": "Unit Test Company",
            "total_products": 0,
            "owner_groups": [{"name": "company_ABC002"}, {"name": "company_UnitTest"}],
        }

    def test_partial_update_company(self):
        user_001 = User.objects.get(username="UserABC001")
        user_super = User.objects.get(username="UserABCSuper")
        user_admin = User.objects.get(username="admin")

        # User1 is not part of company_ABC002 group, which the company is currently set to
        # API responds as if company does not exist
        self.client.force_login(user_001)
        request_body = {"name": "Updated Company"}
        response = self.client.patch(
            "/api/companies/ABC002/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "No Company matches the given query."}

        # User2 is part of ABC002 (allowing update of this company), but not part of the target company_ABC001
        self.client.force_login(user_super)
        request_body = {"name": "Updated Company", "owner_groups": [{"name": "company_ABC001"}]}
        response = self.client.patch(
            "/api/companies/ABC002/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 400
        assert response.json() == {
            "owner_groups": [
                "You must be in at least one of the specified groups when creating or updating Company records."
            ]
        }

        # Add User2 to ABC001 group, allow changing of groups and name
        # Code is ignored as it's not modifiable by non-superusers
        user_super.groups.add(Group.objects.get(name="company_ABC001"))
        request_body = {"name": "Updated Company", "code": "NewCode", "owner_groups": [{"name": "company_ABC001"}]}
        response = self.client.patch(
            "/api/companies/ABC002/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {
            "code": "ABC002",
            "name": "Updated Company",
            "total_products": 1,
            "owner_groups": [{"name": "company_ABC001"}],
        }
        company = Company.objects.get(id=2)
        assert company.name == "Updated Company"
        assert company.code == "ABC002"
        assert list(company.owner_groups.all()) == [Group.objects.get(name="company_ABC001")]

        # Superuser doesn't need to be in groups, and can modify code
        self.client.force_login(user_admin)
        request_body = {"code": "NewCode", "owner_groups": [{"name": "company_Admin"}]}
        response = self.client.patch(
            "/api/companies/ABC001/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {
            "code": "NewCode",
            "name": "ABC Company",
            "total_products": 1,
            "owner_groups": [{"name": "company_Admin"}],
        }
        company = Company.objects.get(id=1)
        assert list(company.owner_groups.all()) == [Group.objects.get(name="company_Admin")]

    def test_update_company(self):
        user_001 = User.objects.get(username="UserABC001")
        user_super = User.objects.get(username="UserABCSuper")
        user_admin = User.objects.get(username="admin")
        request_body = {"name": "Updated Company", "code": "Updated Code", "owner_groups": [{"name": "company_ABC001"}]}

        # Check default serializer behaves like create serializer
        self.client.force_login(user_001)
        response = self.client.put("/api/companies/ABC001/", data=json.dumps({}), content_type="application/json")
        assert response.status_code == 400
        assert response.json() == {
            "name": ["This field is required."],
            "owner_groups": ["This field is required."],
        }

        # User1 is not part of company_ABC002 group, which the company is currently set to
        self.client.force_login(user_001)
        response = self.client.put(
            "/api/companies/ABC002/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 404
        assert response.json() == {"detail": "No Company matches the given query."}

        # User2 is part of ABC002 (allowing update of this company), but not part of the target company_ABC001
        self.client.force_login(user_super)
        response = self.client.put(
            "/api/companies/ABC002/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 400
        assert response.json() == {
            "owner_groups": [
                "You must be in at least one of the specified groups when creating or updating Company records."
            ]
        }

        # Add User2 to ABC001 group, allow changing of Company. Code cannot be changed by non-superuser, so is ignored
        user_super.groups.add(Group.objects.get(name="company_ABC001"))
        response = self.client.put(
            "/api/companies/ABC002/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {
            "code": "ABC002",
            "name": "Updated Company",
            "total_products": 1,
            "owner_groups": [{"name": "company_ABC001"}],
        }
        company = Company.objects.get(id=2)
        assert company.name == "Updated Company"
        assert company.code == "ABC002"
        assert list(company.owner_groups.all()) == [Group.objects.get(name="company_ABC001")]

        # Superuser doesn't need to be in groups and can updated code
        self.client.force_login(user_admin)
        request_body["owner_groups"] = [{"name": "company_Admin"}]
        response = self.client.put(
            "/api/companies/ABC001/", data=json.dumps(request_body), content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {
            "code": "Updated Code",
            "name": "Updated Company",
            "total_products": 1,
            "owner_groups": [{"name": "company_Admin"}],
        }
        company = Company.objects.get(id=1)
        assert company.name == "Updated Company"
        assert company.code == "Updated Code"
        assert list(company.owner_groups.all()) == [Group.objects.get(name="company_Admin")]
