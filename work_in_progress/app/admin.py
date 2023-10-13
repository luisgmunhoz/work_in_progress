from django.contrib import admin

from work_in_progress.app.models import Company, Contato, SystemUser

# Register your models here.
admin.site.site_header = "Work in progress"
admin.site.site_title = "Work in progress"
admin.site.register(SystemUser)
admin.site.register(Contato)
admin.site.register(Company)
