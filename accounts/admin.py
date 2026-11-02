from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'perfil', 'telefone', 'is_active')
    list_filter = ('perfil', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cpf')
    date_hierarchy = 'date_joined'
    fieldsets = UserAdmin.fieldsets + (
        ('Dados da academia', {'fields': ('perfil', 'cpf', 'telefone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados da academia', {'fields': ('perfil', 'cpf', 'telefone', 'first_name', 'last_name', 'email')}),
    )
