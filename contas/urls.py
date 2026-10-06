"""
Rotas do app de contas.

O arquivo de urls e o "menu" do sistema web -- o equivalente ao
while True / if opcao == "1" do seu main.py na Entrega 1. A diferenca
e que aqui quem escolhe a opcao e a URL que o usuario abre.

Leitura: material/05-views-urls-templates.md
"""

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

# app_name cria um NAMESPACE. Com ele, o nome completo da rota passa a
# ser "contas:usuario_lista".
#
# Por que isso importa: o app academico tambem vai ter uma rota
# chamada "lista". Sem namespace, os nomes colidiriam e o Django
# resolveria para a errada. Com namespace, nao ha ambiguidade.
app_name = "contas"

urlpatterns = [
    # path(rota, view, name)
    #
    # O `name` e o que voce usa no template -- {% url 'contas:login' %}
    # -- e na view -- redirect("contas:login").
    #
    # NUNCA escreva o caminho na mao no template ("/contas/login/").
    # Se um dia a rota mudar, com {% url %} voce altera aqui e o site
    # inteiro acompanha; com o caminho escrito na mao, voce cacaria
    # link quebrado por todo o projeto.
    path("login/", views.TelaLogin.as_view(), name="login"),
    # LogoutView do Django exige POST desde a versao 5 -- logout por
    # link GET permitia que um site malicioso deslogasse o usuario
    # so por embutir uma <img src="...">.
    path("logout/", LogoutView.as_view(), name="logout"),
    path("painel/", views.painel, name="painel"),
    # ----------------------------------------------------------------
    # CRUD de usuarios.
    #
    # <int:pk> captura um trecho da URL e entrega como argumento para
    # a view:  /usuarios/7/editar/  ->  usuario_editar(request, pk=7)
    #
    # O `int:` e um conversor -- garante que so digito passa. Se
    # alguem abrir /usuarios/abc/editar/, o Django devolve 404 antes
    # de a view rodar, e nao um ValueError.
    # ----------------------------------------------------------------
    path("usuarios/", views.usuario_lista, name="usuario_lista"),
    path("usuarios/novo/", views.usuario_novo, name="usuario_novo"),
    path("usuarios/<int:pk>/", views.usuario_detalhe, name="usuario_detalhe"),
    path("usuarios/<int:pk>/editar/", views.usuario_editar, name="usuario_editar"),
    path("usuarios/<int:pk>/excluir/", views.usuario_excluir, name="usuario_excluir"),
    path("usuarios/<int:pk>/reativar/", views.usuario_reativar, name="usuario_reativar"),
]
