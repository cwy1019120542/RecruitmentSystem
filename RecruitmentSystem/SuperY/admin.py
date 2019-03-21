from django.contrib import admin
from . import models
admin.site.register(models.Applicant)
admin.site.register(models.Company)
admin.site.register(models.ApplicantSearch)
admin.site.register(models.Post)
admin.site.register(models.Tag)
admin.site.register(models.WorkExperience)
admin.site.register(models.ProjectExperience)
admin.site.register(models.EducateExperience)
admin.site.register(models.Skill)