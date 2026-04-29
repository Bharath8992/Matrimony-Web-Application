# -*- coding: utf-8 -*-
from django.contrib import admin
from django.apps import apps
from .models import *

class DynamicColumnAdmin(admin.ModelAdmin):
        def __init__(self, *args, **kwargs):
            super(DynamicColumnAdmin, self).__init__(*args, **kwargs)
            field_list = [i.name for i in self.model._meta.fields]
            fields_without_relation = [i.name for i in self.model._meta.fields if not isinstance(i,models.ForeignKey) and not 'invalid_date' in i.error_messages]
            self.search_fields = (fields_without_relation)
            self.list_select_related = ()
            self.list_display = field_list
            self.list_display_links = field_list

my_app = apps.get_app_config('mck_admin_console')

for model in list(my_app.get_models()):
       admin.site.register(model, DynamicColumnAdmin)