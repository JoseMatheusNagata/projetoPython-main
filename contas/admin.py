"""
Registro do modelo Usuario no painel administrativo.

O admin do Django gera um CRUD completo a partir do modelo, sem voce
escrever view nem template. Use como FERRAMENTA DE INSPECAO durante o
desenvolvimento -- o papel que o DB Browser for SQLite teve na Entrega
1 -- e nao como substituto das telas do sistema.

Acesse em /admin/ com o usuario 'admin' (senha 'escola2024'), criado
pelo comando `manage.py seed_demo`.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Herda de UserAdmin para preservar o tratamento correto de senha.

    Se registrassemos com o admin.ModelAdmin comum, o campo de senha
    apareceria como um texto editavel e gravaria o valor CRU no banco
    -- destruindo o hash e quebrando o login do usuario.
    """

    list_display = ("username", "first_name", "last_name", "email", "perfil", "is_active")
    list_filter = ("perfil", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("first_name", "username")

    # fieldsets controla o formulario de EDICAO. Copiamos os do
    # UserAdmin e acrescentamos o nosso campo `perfil`.
    fieldsets = UserAdmin.fieldsets + (
        ("Dados academicos", {"fields": ("perfil",)}),
    )

    # add_fieldsets controla o formulario de CRIACAO, que e diferente
    # (tem os dois campos de senha).
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Dados academicos", {"fields": ("first_name", "last_name", "email", "perfil")}),
    )
