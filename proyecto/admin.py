from django.contrib import admin
from django.contrib.auth.models import Permission

from proyecto.models import Proyecto


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = []


@admin.register(Permission)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
