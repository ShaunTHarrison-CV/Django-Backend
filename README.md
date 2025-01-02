# Django-API
This is a simple REST API to showcase how I build applications. The data model and API endpoints are trivial, as the purpose of this repo is to show
how I use the django-rest-framework to build, test and deploy a functional API, not to build a useful API.

## Data Model
Company - A Company is a representation of someone who has something to sell. Mapped to a Django user.
Product - A Product is a representation of something to be sold. Mapped to a Django user.
Transaction - A Transaction is a representation of a person buying one or many instances of a Product.

## Endpoints
GET   /api/companies/ - List all companies.
GET   /api/companies/<code>/ - Get details of specific company. 
GET   /api/companies/<code>/products/ - List all products owned by a specific company.
POST  /api/companies/<code>/products/ - Create a new product under a specific company.
GET   /api/companies/<code>/products/<code>/ - Get details of specific product.
PATCH /api/companies/<code>/products/<code>/ - Modify details of existing product.
GET   /api/companies/<code>/products/<code>/transactions/ - List all transactions of a specific product.
POST  /api/companies/<code>/products/<code>/transactions/ - Create a transaction for the logged in user.
GET   /api/companies/<code>/products/<code>/transactions/<reference>/ - Get details of a specific transaction.

GET  /api/products/ - List all products across all companies.
GET  /api/transactions/ - List all transactions for the logged in user.
GET  /api/transactions/<reference>/ - Get details of a specific transaction.


## Security Design
Companies are associated with a Django user group. Modifying the company or creating a product under a company requires the logged in user to be

Users must be logged in to access any API endpoints apart from the swagger docs. 
Users can only modify Companies/Products that they have permission to. Attempting to modify a Company/Product for a different user will return a 403.
Users can only see Transactions that they own. Listing Transactions will show only that user's transactions. Attempting to retrieve a 

When accessing a list endpoint the backend will
filter for only resources that are owned by the logged in user. If the user requests a resource that exists but they are not allowed to
see, a 404 response will be given. This is to prevent attackers from iterating through codes to build a list of valid codes.

Users who are django admins can access all resources.
