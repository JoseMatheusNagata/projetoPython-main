"""
TODO 13 (BONUS) -- Registre os modelos no admin.
================================================

O admin do Django gera um CRUD completo a partir do modelo, sem view
nem template. Serve para INSPECIONAR os dados enquanto voce
desenvolve -- o papel que o DB Browser for SQLite teve na Entrega 1.

Exemplo pronto e comentado: contas/admin.py

O basico e uma linha por modelo:

    admin.site.register(Aluno)

Mas com pouco mais voce ganha busca, filtro e uma listagem util:

    @admin.register(Aluno)
    class AlunoAdmin(admin.ModelAdmin):
        list_display = ("matricula", "nome", "email", "ativo")
        list_filter = ("ativo",)
        search_fields = ("matricula", "nome", "email")

    @admin.register(Disciplina)
    class DisciplinaAdmin(admin.ModelAdmin):
        list_display = ("codigo", "nome", "carga_horaria", "periodo")
        list_filter = ("periodo",)
        search_fields = ("codigo", "nome")

    @admin.register(Inscricao)
    class InscricaoAdmin(admin.ModelAdmin):
        list_display = ("aluno", "disciplina", "nota1", "nota2")
        list_filter = ("disciplina",)
        # select_related evita o problema N+1 na listagem do admin --
        # o mesmo cuidado do TODO 12a.
        list_select_related = ("aluno", "disciplina")

Para entrar em /admin/ use o usuario 'admin' (senha 'escola2024'), que
o `manage.py seed_demo` ja cria como superusuario.

UM AVISO: o admin nao substitui as telas do trabalho. Ele e ferramenta
de desenvolvedor. Entregar so o admin e entregar o CRUD do Django, nao
o seu.
"""

from django.contrib import admin  # noqa: F401

from .models import Aluno, Disciplina, Inscricao  # noqa: F401

# >>> ESCREVA OS REGISTROS AQUI <<<
