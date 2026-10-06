"""
=====================================================================
 VIEWS DO SISTEMA ACADEMICO -- TODO 7 a 12
=====================================================================

Cada funcao aqui embaixo esta marcada com `todo(...)`: uma tela
provisoria que explica o que falta. Conforme voce implementa, substitua
a chamada de `todo(...)` pelo codigo de verdade -- e a tela provisoria
some sozinha.

--- ONDE ESTA O EXEMPLO ----------------------------------------------

  contas/views.py tem as MESMAS cinco operacoes, prontas e comentadas
  linha a linha, para Usuario. Abra os dois arquivos lado a lado: o que
  muda e o nome do modelo, do form, do template e da rota.

  material/05-views-urls-templates.md explica o ciclo da requisicao.
  material/07-tour-do-app-contas.md faz a leitura guiada do exemplo.

--- OS TEMPLATES JA ESTAO PRONTOS ------------------------------------

  Estao em templates/academico/. Voce NAO precisa escrever HTML.
  Mas precisa mandar o contexto com os nomes que eles esperam -- cada
  TODO diz quais sao.

--- A REGRA QUE NAO MUDOU DA ENTREGA 1 -------------------------------

  Item 5 da rubrica: separacao de responsabilidades. La, o CRUD nao
  podia ter print() nem input(). Aqui vale o inverso: a view NAO monta
  HTML. Ela consulta, decide e entrega dados ao template.

=====================================================================
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AlunoForm, DisciplinaForm, InscricaoForm
from .models import Aluno, Disciplina, Inscricao


def todo(request, numero, titulo, arquivo, descricao):
    """Tela provisoria de 'ainda nao implementado'.

    Existe para que o sistema RODE desde o primeiro minuto, mesmo com
    tudo por fazer. Assim voce navega, ve o menu funcionando e
    implementa um TODO de cada vez, com retorno visual imediato.

    Apague a chamada a esta funcao quando implementar a view. Quando
    nao houver mais nenhuma, pode apagar a funcao tambem.
    """
    return render(
        request,
        "academico/nao_implementado.html",
        {
            "numero": numero,
            "titulo": titulo,
            "arquivo": arquivo,
            "descricao": descricao,
        },
    )


# =====================================================================
# ALUNOS -- TODO 7, 8 e 9
# =====================================================================


@login_required
def aluno_lista(request):
    """
    TODO 7 -- Listar alunos, com busca.
    ===================================

    Equivale ao listar_alunos() da Entrega 1.
    Exemplo pronto: contas/views.py, funcao usuario_lista().

    O que fazer:

      1. Comece com todos os alunos:
             alunos = Aluno.objects.all()

      2. Leia o termo de busca da URL (/alunos/?busca=maria):
             busca = request.GET.get("busca", "").strip()

      3. Se veio busca, filtre por nome OU matricula.
         Varios filter() encadeados viram AND; para OR use Q:
             alunos = alunos.filter(
                 Q(nome__icontains=busca) | Q(matricula__icontains=busca)
             )
         `Q` ja esta importado no topo deste arquivo.

      4. Devolva o render com o contexto que o template espera:
             return render(request, "academico/aluno_lista.html",
                           {"alunos": alunos, "busca": busca})

    O template usa as variaveis `alunos` e `busca`. Se errar o nome, a
    tela aparece vazia sem dar erro nenhum -- o template do Django
    ignora variavel inexistente em silencio. Fique atento a isso.

    BONUS (soft delete): mostre apenas os ativos, com
    .filter(ativo=True). Explique a escolha no README -- e a mesma
    pergunta do bonus da Entrega 1.
    """
    alunos = Aluno.objects.all()
    busca = request.GET.get('busca', '').strip()

    #filtro por nome, matricula ou email
    if busca:
        alunos = alunos.filter(
            Q(nome__icontains=busca) |
            Q(matricula__icontains=busca) |
            Q(email__icontains=busca)
        )

    return render(
        request,
        "academico/aluno_lista.html",
        {"alunos": alunos, "busca":busca},
    )



@login_required
def aluno_novo(request):
    """
    TODO 8 -- Cadastrar aluno.
    ==========================

    Equivale ao inserir_aluno().
    Exemplo pronto: contas/views.py, funcao usuario_novo().

    Use o PADRAO DE VIEW COM FORMULARIO -- o mesmo desenho que se
    repete em toda tela de cadastro e edicao:

        if request.method == "POST":
            form = AlunoForm(request.POST)
            if form.is_valid():
                aluno = form.save()
                messages.success(request, f"Aluno '{aluno.nome}' cadastrado.")
                return redirect("academico:aluno_lista")
            messages.error(request, "Corrija os erros do formulario.")
        else:
            form = AlunoForm()

        return render(request, "academico/aluno_form.html",
                      {"form": form, "titulo": "Novo aluno"})

    POR QUE redirecionar depois de salvar, em vez de renderizar?
    Padrao POST/Redirect/GET. Sem o redirect, um F5 reenvia o POST e
    cadastra o mesmo aluno de novo -- e ai a matricula duplicada que o
    UNIQUE barra vira uma tela de erro para o usuario.

    O template espera: `form` e `titulo`.
    """
    return todo(
        request, 8, "Cadastrar aluno", "academico/views.py :: aluno_novo",
        "Padrao POST/Redirect/GET com AlunoForm, renderizando aluno_form.html.",
    )


@login_required
def aluno_editar(request, pk):
    """
    TODO 9a -- Editar aluno.
    ========================

    Equivale ao atualizar_aluno().
    Exemplo pronto: contas/views.py, funcao usuario_editar().

    E igual ao TODO 8, com DUAS diferencas:

      1. Busque o registro antes:
             aluno = get_object_or_404(Aluno, pk=pk)
         Isto faz o SELECT ... WHERE id = %s e devolve 404 se nao
         achar -- substitui aquele `if aluno is None: print(...)` que
         voce escrevia na Entrega 1.

      2. Passe instance=aluno ao montar o form, NOS DOIS CAMINHOS:
             AlunoForm(request.POST, instance=aluno)   # no POST
             AlunoForm(instance=aluno)                 # no GET

    Sem o instance, o save() faz INSERT e voce cria um aluno novo em
    vez de alterar o existente. Com instance, vira
    UPDATE ... WHERE id = %s -- o "WHERE obrigatorio em UPDATE" do
    item 4 da rubrica, garantido pelo ORM.

    O template espera: `form` e `titulo`.
    """
    return todo(
        request, 9, "Editar aluno", "academico/views.py :: aluno_editar",
        "get_object_or_404 + AlunoForm(instance=aluno), renderizando aluno_form.html.",
    )


@login_required
def aluno_excluir(request, pk):
    """
    TODO 9b -- Excluir (ou desativar) aluno.
    ========================================

    Equivale ao excluir_aluno().
    Exemplo pronto: contas/views.py, funcao usuario_excluir().

    O desenho tem DUAS requisicoes:

        aluno = get_object_or_404(Aluno, pk=pk)

        if request.method == "POST":
            ...faz a exclusao...
            messages.success(request, "...")
            return redirect("academico:aluno_lista")

        return render(request, "academico/aluno_confirmar_exclusao.html",
                      {"aluno": aluno})

    GET mostra a confirmacao; POST executa. Nunca apague dados num GET:
    um link que apaga e disparado por robo de busca, pre-carregador do
    navegador ou qualquer um que abra a URL sem querer.

    --- A DECISAO DE PROJETO -----------------------------------------

    Voce pode fazer de duas formas:

      DELETE de verdade:    aluno.delete()
      SOFT DELETE (bonus):  aluno.ativo = False
                            aluno.save(update_fields=["ativo"])

    Se o TODO 3 usou on_delete=PROTECT, tentar apagar um aluno que ja
    tem inscricao levanta ProtectedError -- e o banco impedindo a
    perda de historico academico. Trate e explique:

        from django.db.models import ProtectedError
        try:
            aluno.delete()
        except ProtectedError:
            messages.error(request, "Este aluno tem inscricoes e nao pode ser excluido.")

    Qual das duas e a certa para um sistema academico? Essa e a
    pergunta do bonus, e a resposta vai no README.

    O template espera: `aluno`.
    """
    return todo(
        request, 9, "Excluir aluno", "academico/views.py :: aluno_excluir",
        "GET mostra a confirmacao, POST executa a exclusao ou o soft delete.",
    )


# =====================================================================
# DISCIPLINAS -- TODO 10 e 11
#
# A partir daqui o roteiro e o mesmo. Se os TODOs 7 a 9 ficaram bons,
# estes dois sao traducao quase mecanica -- e essa repeticao e
# proposital: e ela que mostra que voce entendeu o padrao, e nao
# decorou um caso.
# =====================================================================


@login_required
def disciplina_lista(request):
    """
    TODO 10 -- Listar disciplinas, com busca por codigo ou nome.
    Espelhe o TODO 7. O template espera: `disciplinas` e `busca`.
    """
    return todo(
        request, 10, "Listar disciplinas", "academico/views.py :: disciplina_lista",
        "Mesmo padrao do TODO 7, agora com Disciplina.",
    )


@login_required
def disciplina_nova(request):
    """
    TODO 11a -- Cadastrar disciplina. Espelhe o TODO 8.
    O template espera: `form` e `titulo`.
    """
    return todo(
        request, 11, "Cadastrar disciplina", "academico/views.py :: disciplina_nova",
        "Mesmo padrao do TODO 8, agora com DisciplinaForm.",
    )


@login_required
def disciplina_editar(request, pk):
    """
    TODO 11b -- Editar disciplina. Espelhe o TODO 9a.
    O template espera: `form` e `titulo`.
    """
    return todo(
        request, 11, "Editar disciplina", "academico/views.py :: disciplina_editar",
        "Mesmo padrao do TODO 9a, agora com Disciplina.",
    )


@login_required
def disciplina_excluir(request, pk):
    """
    TODO 11c -- Excluir disciplina. Espelhe o TODO 9b.
    O template espera: `disciplina`.
    """
    return todo(
        request, 11, "Excluir disciplina", "academico/views.py :: disciplina_excluir",
        "Mesmo padrao do TODO 9b, agora com Disciplina.",
    )


# =====================================================================
# INSCRICOES E NOTAS -- TODO 12
#
# Esta e a parte que o CRUD simples nao ensina: trabalhar com o
# relacionamento N:N.
# =====================================================================


@login_required
def inscricao_lista(request):
    """
    TODO 12a -- Listar inscricoes com o aluno e a disciplina.
    =========================================================

    A listagem mostra o nome do aluno e o nome da disciplina -- dados
    que estao em OUTRAS tabelas. Em SQL voce escreveria:

        SELECT * FROM inscricao
          JOIN aluno      ON aluno.id      = inscricao.aluno_id
          JOIN disciplina ON disciplina.id = inscricao.disciplina_id

    No ORM basta escrever `inscricao.aluno.nome` no template e o
    Django busca sozinho. O problema e que ele busca UMA CONSULTA POR
    LINHA: 50 inscricoes viram 101 consultas ao banco. Isso se chama
    problema N+1 e e a causa numero 1 de lentidao em sistemas Django.

    A solucao e avisar antes o que voce vai usar:

        inscricoes = Inscricao.objects.select_related("aluno", "disciplina")

    select_related faz o JOIN e traz tudo em UMA consulta.

    Este e o assunto da Entrega 2. Veja material/03-orm-na-pratica.md
    -- inclusive como espiar o SQL gerado com `print(qs.query)`.

    O template espera: `inscricoes`.
    """
    return todo(
        request, 12, "Listar inscricoes", "academico/views.py :: inscricao_lista",
        "Inscricao.objects.select_related('aluno', 'disciplina') -- o JOIN sem escrever JOIN.",
    )


@login_required
def inscricao_nova(request):
    """
    TODO 12b -- Inscrever aluno em disciplina. Espelhe o TODO 8, com
    InscricaoForm. O template espera: `form` e `titulo`.

    Cuidado com a inscricao duplicada: a UniqueConstraint do TODO 3
    barra no banco e o form exibe o erro. Se voce NAO declarou a
    constraint, o sistema aceita a duplicata calado -- e o item 1 da
    rubrica vai embora junto.
    """
    return todo(
        request, 12, "Nova inscricao", "academico/views.py :: inscricao_nova",
        "Mesmo padrao do TODO 8, agora com InscricaoForm.",
    )


@login_required
def inscricao_editar(request, pk):
    """
    TODO 12c -- Lancar ou corrigir as notas. Espelhe o TODO 9a.
    O template espera: `form` e `titulo`.
    """
    return todo(
        request, 12, "Lancar notas", "academico/views.py :: inscricao_editar",
        "Mesmo padrao do TODO 9a, agora com Inscricao.",
    )


@login_required
def inscricao_excluir(request, pk):
    """
    TODO 12d -- Cancelar inscricao. Espelhe o TODO 9b.
    O template espera: `inscricao`.
    """
    return todo(
        request, 12, "Cancelar inscricao", "academico/views.py :: inscricao_excluir",
        "Mesmo padrao do TODO 9b, agora com Inscricao.",
    )
