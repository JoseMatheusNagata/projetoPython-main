# 10 — Glossário e Class-Based Views

## Glossário

**App** — um módulo do projeto, com models, views e templates próprios.
Este projeto tem dois: `contas` e `academico`. Um app bem feito pode ser
copiado para outro projeto.

**Projeto** — o conjunto: a pasta `config/` (settings e urls) mais os
apps.

**ORM** (*Object-Relational Mapper*) — a camada que traduz classes Python
em tabelas e métodos em SQL.

**Model** — classe que descreve uma tabela.

**Migration** — arquivo versionado que descreve uma alteração no banco.
Gerado por `makemigrations`, aplicado por `migrate`.

**QuerySet** — a "receita" de uma consulta. Preguiçoso: só vai ao banco
quando os dados são usados.

**Lookup** — o sufixo depois de `__` que define a comparação:
`nome__icontains`, `carga_horaria__gt`.

**`Q`** — objeto que permite combinar condições com `OR` (`|`) e `AND`
(`&`).

**N+1** — problema de desempenho em que uma listagem dispara uma consulta
extra por linha. Resolve-se com `select_related` / `prefetch_related`.

**View** — função que recebe um `request` e devolve um `HttpResponse`.

**Template** — arquivo HTML com marcações `{{ }}` e `{% %}`.

**Contexto** — o dicionário de variáveis que a view entrega ao template.

**Context processor** — função que injeta variáveis em **todos** os
templates. É o que faz `{{ user }}` existir em qualquer lugar.

**Form / ModelForm** — coleta, valida e converte dados de entrada. O
`ModelForm` deduz os campos a partir do modelo.

**`cleaned_data`** — dicionário com os valores já validados e
convertidos. Só existe depois de `is_valid()`.

**Widget** — o controle HTML de um campo (`<input>`, `<select>`,
checkbox).

**Middleware** — camada por onde toda requisição passa na ida e toda
resposta na volta. A ordem importa.

**Decorator** — função que embrulha outra para acrescentar
comportamento: `@login_required`.

**CSRF** — ataque em que outro site envia um POST em nome do seu usuário
logado. O `{% csrf_token %}` impede.

**Hash de senha** — transformação de mão única. Dá para conferir se uma
senha bate; não dá para recuperar a original.

**Sessão** — registro no servidor que lembra quem está logado. O cookie
guarda só o id dela.

**Soft delete** — marcar como inativo em vez de apagar, preservando o
histórico.

**POST/Redirect/GET** — redirecionar depois de gravar, para que o F5 não
duplique o registro.

**`slug`, `pk`** — `pk` é a chave primária (o `id`).

**Namespace** — o prefixo de rota (`academico:`) que evita colisão de
nomes entre apps.

**Fixture / seed** — carga de dados de exemplo. Aqui, o comando
`seed_demo`.

**`manage.py`** — o utilitário de linha de comando do projeto. Ele
inicializa o Django antes de rodar qualquer coisa — por isso um script
solto não consegue importar models.

---

## Bônus: o mesmo CRUD em Class-Based Views

O projeto usa views em **função** de propósito: cada linha é explícita e
defensável na arguição. Mas o Django oferece um atalho que vale conhecer
— principalmente porque é o que você vai encontrar em código de mercado.

### Lado a lado

**Listar** — em função:

```python
@login_required
def aluno_lista(request):
    alunos = Aluno.objects.all()
    busca = request.GET.get("busca", "").strip()
    if busca:
        alunos = alunos.filter(
            Q(nome__icontains=busca) | Q(matricula__icontains=busca)
        )
    return render(request, "academico/aluno_lista.html",
                  {"alunos": alunos, "busca": busca})
```

Em classe:

```python
class AlunoListView(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = "academico/aluno_lista.html"
    context_object_name = "alunos"

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get("busca", "").strip()
        if busca:
            qs = qs.filter(
                Q(nome__icontains=busca) | Q(matricula__icontains=busca)
            )
        return qs
```

**Criar** — em função, são 12 linhas. Em classe:

```python
class AlunoCreateView(LoginRequiredMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = "academico/aluno_form.html"
    success_url = reverse_lazy("academico:aluno_lista")
```

**Quatro linhas.** O `CreateView` já faz: GET monta o form, POST valida,
salva, redireciona.

**Editar** é idêntico, trocando `CreateView` por `UpdateView` — a classe
descobre sozinha que precisa carregar a instância pela `pk` da URL.

**Excluir**:

```python
class AlunoDeleteView(LoginRequiredMixin, DeleteView):
    model = Aluno
    template_name = "academico/aluno_confirmar_exclusao.html"
    success_url = reverse_lazy("academico:aluno_lista")
```

Ele já implementa o "GET confirma, POST executa".

Nas URLs, a chamada muda:

```python
path("alunos/", views.AlunoListView.as_view(), name="aluno_lista"),
```

### O que você ganha e o que você perde

| | Função | Classe |
|---|---|---|
| Linhas de código | mais | muito menos |
| Fluxo visível | todo | escondido na hierarquia |
| Customizar o incomum | fácil | precisa saber qual método sobrescrever |
| Explicar na arguição | direto | exige conhecer o framework |

O ganho é real: o `CreateView` em quatro linhas é o espírito do
Desenvolvimento Rápido de Aplicações. O custo também: quando você precisa
de algo fora do padrão, tem que descobrir se o gancho é
`get_queryset`, `get_context_data`, `form_valid`, `get_form_kwargs` ou
`get_success_url`.

**A ordem em que você aprendeu não é acidente.** Quem escreveu o CRUD na
mão sabe o que o `CreateView` faz — e por isso consegue sobrescrever o
método certo. Quem começou pelo atalho fica preso quando o atalho não
serve.

Vale o mesmo que foi dito sobre SQL e ORM no [módulo
01](01-de-sqlite-cru-para-django.md): você aprende a fazer na mão para
entender o que a máquina faz por você.

### Quer tentar?

Converter uma das views para CBV, mantendo `python verificar.py` verde, é
um bom exercício de bônus — e mostra que os testes não dependem de
*como* você implementou, só do comportamento.

Se for fazer, registre no README o que mudou e por quê.

---

Anterior: [09 — Erros comuns](09-erros-comuns.md) ·
Volta ao [índice](README.md)
