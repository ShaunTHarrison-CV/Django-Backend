from django.contrib import admin

from app import models

admin.site.register(models.Company)
admin.site.register(models.Product)
admin.site.register(models.Transaction)
