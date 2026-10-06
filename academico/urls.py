"""
Rotas do app academico.

ESTE ARQUIVO JA VEM PRONTO -- de proposito.

Ele e o CONTRATO entre as suas views, os templates e os testes: os
nomes de rota daqui aparecem no menu (templates/base.html), nos botoes
dos templates e no academico/tests/. Se voce renomear uma rota, tudo
isso quebra de uma vez.

Voce nao precisa escrever, mas PRECISA saber ler -- o padrao das
rotas cai na arguicao. O exemplo comentado linha a linha esta em
contas/urls.py, e a explicacao completa em
material/05-views-urls-templates.md.
"""

from django.urls import path

from . import views

# Namespace do app: as rotas daqui se chamam "academico:aluno_lista".
# E o que evita colisao com a rota "usuario_lista" do app contas.
app_name = "academico"

urlpatterns = [
    # --- Alunos ------------------------------------------------------
    path("alunos/", views.aluno_lista, name="aluno_lista"),
    path("alunos/novo/", views.aluno_novo, name="aluno_novo"),
    path("alunos/<int:pk>/editar/", views.aluno_editar, name="aluno_editar"),
    path("alunos/<int:pk>/excluir/", views.aluno_excluir, name="aluno_excluir"),

    # --- Disciplinas -------------------------------------------------
    path("disciplinas/", views.disciplina_lista, name="disciplina_lista"),
    path("disciplinas/nova/", views.disciplina_nova, name="disciplina_nova"),
    path("disciplinas/<int:pk>/editar/", views.disciplina_editar, name="disciplina_editar"),
    path("disciplinas/<int:pk>/excluir/", views.disciplina_excluir, name="disciplina_excluir"),

    # --- Inscricoes e notas ------------------------------------------
    path("inscricoes/", views.inscricao_lista, name="inscricao_lista"),
    path("inscricoes/nova/", views.inscricao_nova, name="inscricao_nova"),
    path("inscricoes/<int:pk>/editar/", views.inscricao_editar, name="inscricao_editar"),
    path("inscricoes/<int:pk>/excluir/", views.inscricao_excluir, name="inscricao_excluir"),
]
