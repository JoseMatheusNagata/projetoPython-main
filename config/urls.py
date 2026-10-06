"""
Rotas do PROJETO -- o ponto de entrada de toda URL.

O Django le esta lista de cima para baixo e para na primeira que casar.
include() delega um prefixo inteiro para o urls.py de um app: tudo que
comeca com "academico/" e problema do academico/urls.py.

Isso mantem cada app independente -- voce pode copiar o app academico
para outro projeto e as rotas vao junto.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # O painel administrativo do Django.
    #
    # Pense nele como o DB Browser for SQLite da Entrega 1: uma
    # ferramenta para INSPECIONAR os dados enquanto voce desenvolve.
    # Ele nao e a entrega -- as telas que voce constroi e que sao.
    path("admin/", admin.site.urls),

    path("contas/", include("contas.urls")),
    path("academico/", include("academico.urls")),

    # A raiz do site manda para o painel. Quem nao estiver logado sera
    # redirecionado ao login pelo @login_required.
    path("", RedirectView.as_view(pattern_name="contas:painel"), name="inicio"),
]
