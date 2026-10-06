# 05 — Views, URLs e templates

Leia antes dos **TODO 7 a 12**.

## O ciclo da requisição

```
  navegador                     Django                      banco
      |                            |                          |
      |  GET /academico/alunos/    |                          |
      |--------------------------->|                          |
      |                    config/urls.py                     |
      |                            |                          |
      |                    academico/urls.py                  |
      |                            |                          |
      |                    views.aluno_lista(request)         |
      |                            |     Aluno.objects.all()  |
      |                            |------------------------->|
      |                            |<-------------------------|
      |                            |                          |
      |                    render("aluno_lista.html", {...})  |
      |                            |                          |
      |<---------------------------|                          |
      |         HTML pronto        |                          |
```

Compare com a Entrega 1: o `while True` do `main.py` virou o `urls.py`, o
`if opcao == "1"` virou a rota, e o `print()` virou o template.

## URLs

```python
# academico/urls.py
app_name = "academico"

urlpatterns = [
    path("alunos/", views.aluno_lista, name="aluno_lista"),
    path("alunos/<int:pk>/editar/", views.aluno_editar, name="aluno_editar"),
]
```

`<int:pk>` captura um trecho da URL e entrega como argumento:

```
/academico/alunos/7/editar/   ->   aluno_editar(request, pk=7)
```

O `int:` é um conversor. Se alguém abrir `/alunos/abc/editar/`, o Django
devolve 404 **antes** de a view rodar — não um `ValueError`.

### Sempre use o `name`

No template e na view, refira-se à rota pelo nome:

```django
<a href="{% url 'academico:aluno_editar' aluno.pk %}">Editar</a>
```

```python
return redirect("academico:aluno_lista")
```

**Nunca escreva o caminho na mão** (`/academico/alunos/`). Com `{% url
%}`, se um dia a rota mudar, você altera em `urls.py` e o site inteiro
acompanha. Com o caminho escrito na mão, você caça link quebrado pelo
projeto todo.

O `app_name` cria o namespace (`academico:`). Sem ele, a rota
`aluno_lista` do app acadêmico colidiria com nomes de outros apps.

## Views

Uma view é uma função que **recebe** um `request` e **devolve** um
`HttpResponse`. Só isso.

```python
def aluno_lista(request):
    alunos = Aluno.objects.all()
    return render(request, "academico/aluno_lista.html", {"alunos": alunos})
```

`render(request, template, contexto)` junta template com dados e devolve
o HTML.

O **contexto** é o dicionário de variáveis que o template pode usar. Se
você mandar `{"alunos": ...}`, o template escreve `{% for aluno in alunos %}`.

> Errou o nome da variável no contexto? A tela aparece **vazia, sem erro
> nenhum** — o template do Django ignora variável inexistente em
> silêncio. É a causa mais comum de "minha lista não aparece e não dá
> erro". Cada TODO diz exatamente quais nomes o template espera.

### O padrão de view com formulário

Decore este desenho. Ele se repete em toda tela de cadastro e edição:

```python
def aluno_novo(request):
    if request.method == "POST":            # o usuário ENVIOU o form
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save()
            messages.success(request, f"Aluno '{aluno.nome}' cadastrado.")
            return redirect("academico:aluno_lista")
        messages.error(request, "Corrija os erros do formulário.")
    else:                                   # o usuário só ABRIU a tela
        form = AlunoForm()

    return render(request, "academico/aluno_form.html",
                  {"form": form, "titulo": "Novo aluno"})
```

Repare que o `render` final atende dois casos: o GET (form vazio) e o
POST inválido (form com os erros e com o que o usuário digitou). É por
isso que ele fica fora do `if`.

### Por que redirecionar depois de salvar

Chama-se **POST/Redirect/GET**. Sem o redirect, o usuário aperta F5, o
navegador reenvia o POST e o registro é cadastrado de novo.

Regra geral: **depois de alterar dados, sempre redirecione.**

### GET lê, POST altera

```python
def aluno_excluir(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == "POST":
        aluno.delete()
        return redirect("academico:aluno_lista")

    return render(request, "academico/aluno_confirmar_exclusao.html",
                  {"aluno": aluno})
```

GET mostra a confirmação, POST executa.

Isso **não** é burocracia. GET precisa ser seguro porque um link é
disparado por robô de busca, por pré-carregador do navegador e por
qualquer um que abra a URL sem querer. Um link que apaga dados é uma
bomba-relógio.

### `get_object_or_404`

```python
aluno = get_object_or_404(Aluno, pk=pk)
```

Faz o `SELECT ... WHERE id = %s` e, se não achar, responde 404. Substitui
aquele bloco da Entrega 1:

```python
aluno = buscar_aluno_por_id(id)
if aluno is None:
    print("Aluno não encontrado")
    return
```

## Mensagens

```python
messages.success(request, "Aluno cadastrado.")
messages.error(request, "Corrija os erros.")
```

É o `print("Aluno cadastrado!")` do seu menu — só que na camada certa. A
view **dispara** a mensagem; o `base.html` **exibe**, em qualquer tela,
sem a view precisar se preocupar.

A mensagem sobrevive ao redirect: ela fica guardada na sessão e aparece
na página seguinte.

## Templates

### Herança

```django
{% extends "base.html" %}

{% block conteudo %}
  <h1>Alunos</h1>
{% endblock %}
```

O `base.html` tem a navbar, o CSS e a área de mensagens. Cada página
preenche só os blocos. Mudou a navbar? Mudou em todas as telas.

**`{% extends %}` tem que ser a primeira tag do arquivo.** Nem um
comentário pode vir antes.

### Sintaxe

| Escreve | Faz |
|---|---|
| `{{ variavel }}` | imprime |
| `{{ objeto.campo }}` | atributo — e atravessa FK: `{{ inscricao.aluno.nome }}` |
| `{% if %}` `{% else %}` `{% endif %}` | condição |
| `{% for x in lista %}` `{% empty %}` `{% endfor %}` | laço (com caso vazio) |
| `{% url 'app:rota' arg %}` | monta um link |
| `{% include "outro.html" %}` | insere outro template |
| `{# comentário de uma linha #}` | comentário |
| `{% comment %}...{% endcomment %}` | comentário de várias linhas |

> `{#  #}` **não funciona em várias linhas.** Se o seu comentário tem
> mais de uma linha, use `{% comment %}` — senão o texto aparece na tela.

### Filtros

```django
{{ aluno.data_nascimento|date:"d/m/Y" }}
{{ inscricao.media|floatformat:1 }}
{{ aluno.email|default:"--" }}
{{ inscricao.nota1|default_if_none:"--" }}
```

> **`default` e `default_if_none` são diferentes.** `default` troca
> qualquer valor *falso* — e **nota 0 é falsa**. O aluno que tirou zero
> apareceria com "--", como se a nota não tivesse sido lançada. Use
> `default_if_none` para números.

### O que o template NÃO faz

O template não consulta o banco, não decide regra de negócio, não chama
função com argumento. Ele exibe.

É o mesmo item 5 da rubrica da Entrega 1, do outro lado: lá o CRUD não
podia ter `print()`; aqui a view não monta HTML e o template não faz
consulta.

É isso que vai permitir, na Entrega 3, mudar a aparência sem tocar na
lógica.

---

Anterior: [04 — Forms e validação](04-forms-e-validacao.md) ·
Próximo: [06 — Autenticação e permissões](06-autenticacao-e-permissoes.md)
