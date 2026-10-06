"""
Views do app de contas: login, logout e CRUD de usuarios.

ESTE ARQUIVO E A SUA REFERENCIA. O CRUD que voce vai escrever no app
`academico` e o mesmo padrao, trocando Usuario por Aluno/Disciplina.

Paralelo com a Entrega 1 -- o CRUD nao mudou de natureza, mudou de
camada:

    Entrega 1 (modo texto)              Aqui (web)
    ------------------------------      ----------------------------
    main.py mostra o menu               o template mostra o HTML
    input() coleta os dados             o <form> coleta os dados
    crud_aluno.listar_alunos()          Usuario.objects.all()
    crud_aluno.inserir_aluno(...)       form.save()
    print("Aluno cadastrado!")          messages.success(...)
    cursor.execute + commit             o ORM, dentro da transacao

A regra do item 5 da rubrica continua valendo, so que ao contrario:
la, o CRUD nao podia ter print(); aqui, a view nao monta HTML. Quem
monta HTML e o template.

Leitura: material/05-views-urls-templates.md e material/07-tour-do-app-contas.md
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import somente_coordenacao
from .forms import LoginForm, UsuarioCriarForm, UsuarioEditarForm
from .models import Usuario


# =====================================================================
# AUTENTICACAO
# =====================================================================


class TelaLogin(LoginView):
    """Tela de login.

    Esta e a unica view "de classe" do projeto, e de proposito: o
    Django ja resolve login melhor do que qualquer um de nos faria na
    mao (protecao contra timing attack, invalidacao de sessao, redirect
    seguro). Reaproveitamos a logica e controlamos so a aparencia.

    E o espirito do RAD: escrever codigo e custo, nao virtude. Se o
    framework ja resolveu, use.
    """

    template_name = "contas/login.html"
    authentication_form = LoginForm

    # Se um usuario ja logado abrir /login/, manda para a pagina
    # inicial em vez de mostrar o formulario de novo.
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Chamado quando usuario e senha conferem, logo antes do redirect."""
        messages.success(
            self.request, f"Bem-vindo(a), {form.get_user().get_short_name() or form.get_user()}!"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Chamado quando a autenticacao falha."""
        messages.error(self.request, "Usuario ou senha invalidos.")
        return super().form_invalid(form)


# =====================================================================
# CRUD DE USUARIOS
#
# As cinco operacoes, na mesma ordem do seu crud_aluno.py.
# =====================================================================


@somente_coordenacao
def usuario_lista(request):
    """LISTAR -- equivale a listar_alunos().

    SQL equivalente:
        SELECT * FROM usuario
         WHERE first_name ILIKE %busca% OR username ILIKE %busca%
         ORDER BY first_name
    """
    # .all() devolve um QuerySet, nao uma lista. QuerySet e PREGUICOSO:
    # ele guarda a "receita" da consulta e so vai ao banco quando os
    # dados sao realmente usados (aqui, no {% for %} do template).
    # Por isso da para ir filtrando em etapas sem custo nenhum.
    usuarios = Usuario.objects.all()

    # request.GET sao os dados que vem na URL: /usuarios/?busca=maria
    # O segundo argumento e o padrao quando o parametro nao veio.
    busca = request.GET.get("busca", "").strip()

    if busca:
        # Q() permite combinar condicoes com OR (|) e AND (&).
        # Sem Q, varios filter() encadeados sempre viram AND.
        # __icontains = "contem, ignorando maiusculas" -> ILIKE %valor%
        usuarios = usuarios.filter(
            Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
            | Q(username__icontains=busca)
            | Q(email__icontains=busca)
        )

    # render() junta template + dados e devolve um HttpResponse.
    # O terceiro argumento e o CONTEXTO: o dicionario com as variaveis
    # que o template pode usar.
    return render(
        request,
        "contas/usuario_lista.html",
        {"usuarios": usuarios, "busca": busca},
    )


@somente_coordenacao
def usuario_detalhe(request, pk):
    """BUSCAR POR ID -- equivale a buscar_aluno_por_id().

    get_object_or_404 faz o SELECT ... WHERE id = %s e, se nao achar,
    devolve a pagina 404 automaticamente.

    Compare com a Entrega 1, onde voce precisava tratar o None:

        aluno = buscar_aluno_por_id(id)
        if aluno is None:
            print("Aluno nao encontrado")
            return
    """
    usuario = get_object_or_404(Usuario, pk=pk)
    return render(request, "contas/usuario_detalhe.html", {"usuario_obj": usuario})


@somente_coordenacao
def usuario_novo(request):
    """CRIAR -- equivale a inserir_aluno().

    Aqui aparece o PADRAO DE VIEW COM FORMULARIO, que se repete em toda
    tela de cadastro e de edicao do sistema inteiro. Decore o desenho:

        se a requisicao for POST:          (o usuario enviou o form)
            monta o form com os dados
            se for valido: salva e redireciona
            se nao for:    cai no render la embaixo, com os erros
        se for GET:                        (o usuario so abriu a tela)
            monta um form vazio

        render(...)  -- serve os dois casos

    Por que redirecionar depois de salvar, em vez de so renderizar?
    Por causa do padrao POST/Redirect/GET: sem o redirect, se o usuario
    apertar F5 o navegador reenvia o POST e cadastra o mesmo registro
    duas vezes.
    """
    if request.method == "POST":
        form = UsuarioCriarForm(request.POST)

        # is_valid() dispara TODAS as validacoes: as do modelo, as dos
        # validadores de senha e os seus clean_<campo>. So depois disso
        # existe form.cleaned_data.
        if form.is_valid():
            # save() traduz para INSERT INTO usuario (...) VALUES (...)
            # com os valores PARAMETRIZADOS -- o mesmo cuidado do `?`
            # da Entrega 1, so que automatico. O ORM nunca concatena
            # valor dentro do SQL, entao SQL Injection nao acontece.
            usuario = form.save()

            messages.success(request, f"Usuario '{usuario.username}' cadastrado.")
            return redirect("contas:usuario_lista")

        # Form invalido: nao redireciona. Cai no render de baixo
        # levando o form COM os erros e COM o que o usuario digitou --
        # ninguem precisa preencher tudo de novo.
        messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = UsuarioCriarForm()

    return render(
        request,
        "contas/usuario_form.html",
        {"form": form, "titulo": "Novo usuario", "modo": "criar"},
    )


@somente_coordenacao
def usuario_editar(request, pk):
    """ATUALIZAR -- equivale a atualizar_aluno().

    Uma unica diferenca em relacao ao criar: o `instance=usuario`.

    Sem instance, o form criaria um registro novo.
    Com instance, ele PREENCHE os campos com os valores atuais e o
    save() vira UPDATE ... WHERE id = %s em vez de INSERT.

    Aquele "WHERE obrigatorio em UPDATE" do item 4 da rubrica esta
    garantido de graca: o ORM sempre atualiza pela chave primaria da
    instancia. Nao existe UPDATE sem WHERE por descuido.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, instance=usuario)

        if form.is_valid():
            # Regra de negocio: ninguem desativa a propria conta.
            # Sem isto, a coordenacao poderia se trancar para fora do
            # sistema e nao haveria como voltar pela interface.
            if usuario == request.user and not form.cleaned_data["is_active"]:
                messages.error(request, "Voce nao pode desativar a sua propria conta.")
            else:
                form.save()
                messages.success(request, f"Usuario '{usuario.username}' atualizado.")
                return redirect("contas:usuario_lista")
        else:
            messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = UsuarioEditarForm(instance=usuario)

    return render(
        request,
        "contas/usuario_form.html",
        {
            "form": form,
            "titulo": f"Editar {usuario.username}",
            "modo": "editar",
            "usuario_obj": usuario,
        },
    )


@somente_coordenacao
def usuario_excluir(request, pk):
    """EXCLUIR -- equivale a excluir_aluno(), mas com SOFT DELETE.

    Em vez de apagar a linha, marcamos is_active=False.

    Por que? O enunciado da Entrega 1 pedia essa reflexao no bonus, e a
    resposta vale aqui: num sistema academico o registro tem valor
    historico. Um usuario que lancou notas no semestre passado nao pode
    sumir do banco -- as notas ficariam orfas e o historico, sem autor.
    "Desligar" preserva o passado e bloqueia o futuro.

    Repare ainda em DUAS requisicoes:
      GET  -> mostra a tela de confirmacao
      POST -> executa de fato

    Isso nao e burocracia. GET precisa ser seguro: um link que apaga
    dados seria disparado por qualquer robo, pre-carregador de pagina
    ou histerico do navegador que resolvesse visitar a URL.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        if usuario == request.user:
            messages.error(request, "Voce nao pode desativar a sua propria conta.")
            return redirect("contas:usuario_lista")

        usuario.is_active = False
        # save(update_fields=[...]) grava SO essa coluna:
        #     UPDATE usuario SET is_active = false WHERE id = %s
        # Sem o update_fields, o UPDATE reescreveria todas as colunas.
        usuario.save(update_fields=["is_active"])

        messages.success(request, f"Usuario '{usuario.username}' desativado.")
        return redirect("contas:usuario_lista")

    return render(request, "contas/usuario_confirmar_exclusao.html", {"usuario_obj": usuario})


@somente_coordenacao
def usuario_reativar(request, pk):
    """Desfaz o soft delete.

    O par natural do usuario_excluir. Se desativar fosse o fim da
    linha, seria um DELETE com passos extras.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        usuario.is_active = True
        usuario.save(update_fields=["is_active"])
        messages.success(request, f"Usuario '{usuario.username}' reativado.")

    return redirect("contas:usuario_lista")


@login_required
def painel(request):
    """Pagina inicial de quem esta logado.

    Usa @login_required (do Django) e nao @somente_coordenacao: todo
    usuario autenticado pode ver o painel, independente do perfil.
    """
    return render(request, "contas/painel.html")
