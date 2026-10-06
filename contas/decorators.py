"""
Decorator de controle de acesso por perfil.

Um DECORATOR e uma funcao que embrulha outra funcao para acrescentar
comportamento sem alterar o corpo dela. Voce ja usou um sem perceber:

    @login_required
    def minha_view(request):
        ...

O @login_required checa "esta logado?" ANTES da view rodar. Se nao
estiver, redireciona para o login e a view nem chega a executar.

Aqui escrevemos o nosso, que checa o PERFIL. Poderiamos usar o
@permission_required do Django, mas escrever este na mao mostra o
mecanismo -- e voce vai reaproveita-lo no app academico.

Leitura: material/06-autenticacao-e-permissoes.md
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def somente_coordenacao(view):
    """Libera a view apenas para usuarios de coordenacao.

    Fluxo de decisao, nesta ordem:

      1. Visitante nao logado  -> manda para a tela de login, guardando
         para onde ele queria ir (volta para la depois de logar).
      2. Logado, mas sem perfil de coordenacao -> 403 Acesso negado.
      3. Coordenacao -> executa a view normalmente.

    Por que 403 e nao redirecionar para o login no caso 2?
    Porque sao problemas diferentes. 401/login significa "nao sei quem
    voce e"; 403 significa "sei quem voce e, e voce nao pode". Mandar
    para o login alguem que JA esta logado produz aquele loop de tela
    de login que nao adianta preencher.

    Uso:

        @somente_coordenacao
        def usuario_lista(request):
            ...
    """

    @wraps(view)  # preserva __name__ e docstring da view original;
                  # sem isto, toda view passaria a se chamar "wrapper"
                  # e o debug viraria advinhacao.
    def wrapper(request, *args, **kwargs):
        # request.user existe gracas ao AuthenticationMiddleware.
        # Para um visitante, ele e um AnonymousUser -- um objeto falso
        # cujo is_authenticated e sempre False.
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if not request.user.eh_coordenacao:
            messages.error(
                request,
                "Seu perfil nao tem permissao para acessar a gestao de usuarios.",
            )
            # Levantar PermissionDenied faz o Django devolver 403 e
            # renderizar o template 403.html, se existir.
            raise PermissionDenied("Acesso restrito a coordenacao.")

        return view(request, *args, **kwargs)

    return wrapper
