from django.contrib import admin

from proyecto.models import Proyecto, Cliente

# Register your models here.

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = []

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'ruc', 'nombre']
