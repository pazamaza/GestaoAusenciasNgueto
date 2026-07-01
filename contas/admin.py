from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Campos que aparecerão na lista de utilizadores no painel de controlo
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']
    
    # Customização dos campos ao editar um utilizador existente
    fieldsets = UserAdmin.fieldsets + (
        ('Controlo de Acesso Escolar', {'fields': ('role', 'telefone')}),
    )
    
    # Customização dos campos ao criar um novo utilizador
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Controlo de Acesso Escolar', {
            'classes': ('collapse',),
            'fields': ('role', 'telefone', 'first_name', 'last_name', 'email'),
        }),
    )
