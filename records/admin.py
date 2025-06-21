from django.contrib import admin

# Register your models here.
# records/admin.py

from django.contrib import admin
from .models import Project, Record  # この行を追記

# Register your models here.
admin.site.register(Project)         # この行を追記
admin.site.register(Record)          # この行を追記