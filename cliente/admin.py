from django.contrib import admin

from proyecto.models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'ruc', 'nombre']
