from django.contrib import admin
from .models import ArrangementMap, DeletedArrangementMap


@admin.register(ArrangementMap)
class ArrangementMapAdmin(admin.ModelAdmin):
    pass


@admin.register(DeletedArrangementMap)
class DeletedArrangementMapAdmin(admin.ModelAdmin):
    pass
