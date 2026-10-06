"""GABARITO -- academico/views.py resolvido."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AlunoForm, DisciplinaForm, InscricaoForm
from .models import Aluno, Disciplina, Inscricao

# =====================================================================
# ALUNOS
# =====================================================================


@login_required
def aluno_lista(request):
    alunos = Aluno.objects.all()
    busca = request.GET.get("busca", "").strip()

    if busca:
        alunos = alunos.filter(
            Q(nome__icontains=busca) | Q(matricula__icontains=busca)
        )

    return render(
        request, "academico/aluno_lista.html", {"alunos": alunos, "busca": busca}
    )


@login_required
def aluno_novo(request):
    if request.method == "POST":
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save()
            messages.success(request, f"Aluno '{aluno.nome}' cadastrado.")
            return redirect("academico:aluno_lista")
        messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = AlunoForm()

    return render(
        request, "academico/aluno_form.html", {"form": form, "titulo": "Novo aluno"}
    )


@login_required
def aluno_editar(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == "POST":
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, f"Aluno '{aluno.nome}' atualizado.")
            return redirect("academico:aluno_lista")
        messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = AlunoForm(instance=aluno)

    return render(
        request,
        "academico/aluno_form.html",
        {"form": form, "titulo": f"Editar {aluno.nome}"},
    )


@login_required
def aluno_excluir(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == "POST":
        # Soft delete: o historico academico e preservado.
        aluno.ativo = False
        aluno.save(update_fields=["ativo"])
        messages.success(request, f"Aluno '{aluno.nome}' desativado.")
        return redirect("academico:aluno_lista")

    return render(request, "academico/aluno_confirmar_exclusao.html", {"aluno": aluno})


# =====================================================================
# DISCIPLINAS
# =====================================================================


@login_required
def disciplina_lista(request):
    disciplinas = Disciplina.objects.all()
    busca = request.GET.get("busca", "").strip()

    if busca:
        disciplinas = disciplinas.filter(
            Q(nome__icontains=busca) | Q(codigo__icontains=busca)
        )

    return render(
        request,
        "academico/disciplina_lista.html",
        {"disciplinas": disciplinas, "busca": busca},
    )


@login_required
def disciplina_nova(request):
    if request.method == "POST":
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save()
            messages.success(request, f"Disciplina '{disciplina.nome}' cadastrada.")
            return redirect("academico:disciplina_lista")
        messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = DisciplinaForm()

    return render(
        request,
        "academico/disciplina_form.html",
        {"form": form, "titulo": "Nova disciplina"},
    )


@login_required
def disciplina_editar(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)

    if request.method == "POST":
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            messages.success(request, f"Disciplina '{disciplina.nome}' atualizada.")
            return redirect("academico:disciplina_lista")
        messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = DisciplinaForm(instance=disciplina)

    return render(
        request,
        "academico/disciplina_form.html",
        {"form": form, "titulo": f"Editar {disciplina.codigo}"},
    )


@login_required
def disciplina_excluir(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)

    if request.method == "POST":
        try:
            disciplina.delete()
            messages.success(request, f"Disciplina '{disciplina.nome}' excluida.")
        except ProtectedError:
            # on_delete=PROTECT: o banco recusa e preserva o historico.
            messages.error(
                request,
                f"A disciplina '{disciplina.nome}' tem alunos inscritos e nao "
                "pode ser excluida.",
            )
        return redirect("academico:disciplina_lista")

    return render(
        request,
        "academico/disciplina_confirmar_exclusao.html",
        {"disciplina": disciplina},
    )


# =====================================================================
# INSCRICOES E NOTAS
# =====================================================================


@login_required
def inscricao_lista(request):
    # select_related faz o JOIN e evita o problema N+1.
    inscricoes = Inscricao.objects.select_related("aluno", "disciplina")

    return render(
        request, "academico/inscricao_lista.html", {"inscricoes": inscricoes}
    )


@login_required
def inscricao_nova(request):
    if request.method == "POST":
        form = InscricaoForm(request.POST)
        if form.is_valid():
            inscricao = form.save()
            messages.success(
                request,
                f"{inscricao.aluno.nome} inscrito em {inscricao.disciplina.nome}.",
            )
            return redirect("academico:inscricao_lista")
        messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = InscricaoForm()

    return render(
        request,
        "academico/inscricao_form.html",
        {"form": form, "titulo": "Nova inscricao"},
    )


@login_required
def inscricao_editar(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)

    if request.method == "POST":
        form = InscricaoForm(request.POST, instance=inscricao)
        if form.is_valid():
            form.save()
            messages.success(request, "Notas lancadas.")
            return redirect("academico:inscricao_lista")
        messages.error(request, "Corrija os erros destacados no formulario.")
    else:
        form = InscricaoForm(instance=inscricao)

    return render(
        request,
        "academico/inscricao_form.html",
        {"form": form, "titulo": f"Notas de {inscricao.aluno.nome}"},
    )


@login_required
def inscricao_excluir(request, pk):
    inscricao = get_object_or_404(Inscricao, pk=pk)

    if request.method == "POST":
        inscricao.delete()
        messages.success(request, "Inscricao cancelada.")
        return redirect("academico:inscricao_lista")

    return render(
        request,
        "academico/inscricao_confirmar_exclusao.html",
        {"inscricao": inscricao},
    )
