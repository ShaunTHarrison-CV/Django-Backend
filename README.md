# Django-API
This is a simple REST API to showcase how I build applications. The data model and API endpoints are trivial, as the purpose of this repo is to show
how I use the django-rest-framework to build, test and deploy a functional API, not to build a useful API. 

## Data Model
Company - A Company is a representation of someone who has something to sell.
Product - A Product is a representation of something to be sold.
Transaction - A Transaction is a representation of a person buying one or many instances of a Product.

## Endpoints
GET   /api/companies/ - List all companies.
POST  /api/companies/ - Create a company. Only possible by superusers.
GET   /api/companies/<code>/ - Get details of specific company. 
GET   /api/companies/<code>/products/ - List all products owned by a specific company.
POST  /api/companies/<code>/products/ - Create a new product under a specific company.
GET   /api/companies/<code>/products/<code>/ - Get details of specific product.
PATCH /api/companies/<code>/products/<code>/ - Modify details of existing product.
GET   /api/companies/<code>/products/<code>/transactions/ - List all transactions of a specific product.
GET   /api/companies/<code>/products/<code>/transactions/<reference>/ - Get details of a specific transaction.

GET  /api/products/ - List all products across all companies.
GET  /api/user/transactions/ - List all transactions for the logged in user.
POST /api/user/transactions/ - Create a transaction for the logged in user.
GET  /api/user/transactions/<reference>/ - Get details of a specific transaction.

The /api/companies/... endpoints are demonstrating a multi-tenanted system. Users can only CRUD objects that they are
in the correct Django user group for. Listing objects will filter out any objects that the user doesn't have access to. Attempting
to directly retrieve/modify these will return a 404 response, as if the records didn't exist. This prevents malicious users
iterating through records to get a list of object IDs. Django superusers bypass this check, allowing them to access all records.


## Test Data Setup
The fixture `unit_test.json` contains a small set of user, company and product data for testing. These can be loaded into a running version of
the application using the loaddata command `python manage.py loaddata app/fixtures/unit_test.json`. The created users will be
- User "admin" - A superuser that is not in any groups, for testing the superuser logic
- User "UserABC001" - A user that can only maintain company ABC001.
- User "UserABCSuper" - A user that can maintain ABC001 and ABC002 due to them being in the superuser group for ABC.
- User "UserABCFXC1" - A user that can maintain ABC001 and FXC001 due to being in separate groups for each.
- User "UserFXC002" - A user in the group "company_FXC002", which is not associated with any companies.

The password for all users is "admin". These are test users, and should never be loaded into a production environment as
the password hashes have been committed to this repo. These are insecure credentials.


## Security Design
Companies are associated with a Django user group. Creating or modifying Companies or Products under a company requires the user
to be in one of the user groups associated with the company. Multiple groups were chosen over users for several reasons:
- Allow multiple users to administer a company, in case of employee absence.
- Allow a group to be given to a specific company and users, to limit a group to one company.
- Allow "umbrella" groups to be created and assigned to multiple companies, allowing administration of an enterprise.

Users must be logged in to access any API endpoints apart from the swagger docs. 
Users can only modify Companies/Products that they have permission to. Attempting to modify a Company/Product for a different user will return a 403.
Transactions can only be viewed by the user that made it, or the company that owns the Product within. Listing Transactions will filter out any records
outside of that. Attempting to retrieve a Transaction outside of that will return a 404, even if it exists. 
This is to prevent iterative attacks being used to identify lists of valid transaction reference numbers.

Users who are django superusers bypass the group / ownership requirements.
