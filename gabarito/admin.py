"""GABARITO -- academico/admin.py resolvido."""

from django.contrib import admin

from .models import Aluno, Disciplina, Inscricao


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("matricula", "nome", "email", "data_nascimento", "ativo")
    list_filter = ("ativo",)
    search_fields = ("matricula", "nome", "email")


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "carga_horaria", "periodo")
    list_filter = ("periodo",)
    search_fields = ("codigo", "nome")


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "disciplina", "nota1", "nota2", "media")
    list_filter = ("disciplina",)
    list_select_related = ("aluno", "disciplina")
    search_fields = ("aluno__nome", "aluno__matricula", "disciplina__codigo")

    @admin.display(description="media")
    def media(self, obj):
        return obj.media
