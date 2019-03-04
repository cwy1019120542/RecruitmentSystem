from django.contrib import admin
from . import models
admin.site.register(models.Applicant)
admin.site.register(models.Company)
admin.site.register(models.ApplicantSearch)
admin.site.register(models.Post)
admin.site.register(models.PostTag)