from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import RolAdministrativo,RolProyecto, Proyecto
from proyecto.models import Proyecto

admin.site.register(RolAdministrativo)
admin.site.register(RolProyecto)


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = []


@admin.register(Permission)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

