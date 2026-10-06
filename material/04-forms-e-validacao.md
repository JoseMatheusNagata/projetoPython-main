# 04 — Forms e validação

Leia antes dos **TODO 4, 5 e 6**.

## O que um Form faz

Na Entrega 1, coletar um aluno era assim:

```python
matricula = input("Matrícula: ")
nome = input("Nome: ")
if not nome:
    print("Nome é obrigatório!")
    return
```

Três responsabilidades misturadas: **coletar**, **validar** e **avisar**.
Um `Form` faz as três, separadas:

1. **Desenha** o HTML dos campos
2. **Valida** o que chegou
3. **Converte** os tipos — `"2005-03-14"` (texto do navegador) vira um
   `date` do Python

## `ModelForm` — o atalho que importa

```python
class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ["matricula", "nome", "email", "data_nascimento", "ativo"]
```

Quatro linhas. O Django lê o modelo e deduz o resto: `CharField` vira
`<input type="text">`, `BooleanField` vira checkbox, `DateField` valida
data, `unique=True` vira checagem de duplicidade, `max_length` vira
limite no HTML **e** na validação.

E o melhor: quando você acrescentar um campo ao modelo, basta incluí-lo
no `fields`. Não há HTML para atualizar em três lugares.

> **Nunca use `fields = "__all__"`.** Parece prático e é uma falha de
> segurança: qualquer campo novo passa a ser editável por quem manda o
> formulário, inclusive os que você não queria expor. Liste os campos.

## O ciclo de vida

```python
form = AlunoForm(request.POST)     # 1. recebe os dados crus
if form.is_valid():                # 2. valida TUDO
    aluno = form.save()            # 3. grava
```

`is_valid()` dispara, nesta ordem:

1. A validação de cada campo (tipo, obrigatoriedade, `max_length`)
2. O seu `clean_<campo>()`, se existir
3. O `clean()` geral, se existir
4. As validações do modelo (`unique`, `validators`)

**Só depois de `is_valid()` existe `form.cleaned_data`** — o dicionário
com os valores já convertidos. Antes disso só existe `form.data`, que é
texto cru.

## Criar ou editar: a única diferença

```python
AlunoForm(request.POST)                    # INSERT
AlunoForm(request.POST, instance=aluno)    # UPDATE ... WHERE id = %s
```

Com `instance`, o form nasce preenchido com os valores atuais e o
`save()` atualiza aquele registro em vez de criar outro.

Esqueceu o `instance`? O sintoma é claro: você edita um aluno e aparecem
dois na listagem. (Ou um `IntegrityError` de matrícula duplicada, que é
o banco te salvando.)

**O `instance` é necessário nos dois caminhos** — no `POST` e no `GET`.
Só no POST, o formulário aparece vazio ao abrir a tela de edição.

## Validação própria

### Um campo: `clean_<campo>()`

O Django chama automaticamente todo método com esse nome.

```python
def clean_carga_horaria(self):
    valor = self.cleaned_data["carga_horaria"]
    if valor <= 0:
        raise forms.ValidationError("A carga horária deve ser maior que zero.")
    return valor
```

Duas regras que derrubam gente:

- **Sempre devolva o valor.** Esqueceu o `return`? O campo vira `None` e
  o registro é salvo vazio, sem erro nenhum.
- O método recebe o valor já convertido, então aqui `valor` já é `int`.

Também serve para **normalizar**:

```python
def clean_codigo(self):
    return self.cleaned_data["codigo"].strip().upper()
```

Isso resolve, na entrada, o problema do cenário do trabalho: *"nomes de
disciplina escritos de três formas diferentes"*. `ara0095` e `ARA0095`
passam a ser a mesma coisa — e aí o `unique=True` consegue fazer o
trabalho dele.

### Vários campos juntos: `clean()`

Quando a regra depende de mais de um campo:

```python
def clean(self):
    dados = super().clean()
    if dados.get("nota1") and dados.get("nota2"):
        ...
    return dados
```

O erro levantado aqui não pertence a nenhum campo — aparece no
`{{ form.non_field_errors }}` do template.

## Onde validar: modelo ou formulário?

Nos **dois**, e não é redundância:

| Camada | Como | Vale para |
|---|---|---|
| **Modelo** | `validators=[MinValueValidator(1)]`, `unique=True` | formulário, admin, shell, seed — tudo |
| **Formulário** | `clean_<campo>()` | a mensagem que o usuário lê |

Validar só no formulário deixa a porta dos fundos aberta: o `seed_demo`,
o `/admin/` e o shell continuam gravando lixo. Validar só no modelo
funciona, mas a mensagem fica técnica.

Regra: **integridade no modelo, mensagem no formulário.**

Foi o mesmo raciocínio do `UNIQUE` na Entrega 1 — a restrição no banco é
a garantia, o resto é cortesia.

## Duplicidade: você não precisa escrever nada

Com `unique=True` no modelo, o `ModelForm` já transforma a violação em
mensagem de campo:

> Aluno com este Matricula já existe.

Isso é o item 6 da rubrica da Entrega 1 resolvido de graça — mensagem
clara ao usuário, não traceback.

Para trocar o texto:

```python
class Meta:
    error_messages = {
        "matricula": {"unique": "Já existe um aluno com esta matrícula."},
    }
```

### E a duplicidade composta (`UniqueConstraint`)?

O erro não pertence a um campo, então vai em `non_field_errors`:

```python
class Meta:
    error_messages = {
        forms.models.NON_FIELD_ERRORS: {
            "unique_together": "Este aluno já está inscrito nesta disciplina.",
        }
    }
```

> **Não** substitua a restrição do banco por um `if
> Inscricao.objects.filter(...).exists()`. Entre a sua consulta e o
> `save()` existe uma janela em que outra requisição pode inserir o mesmo
> par. Quem garante é o banco; o formulário só traduz.

## Ajustando o HTML dos campos

```python
class Meta:
    widgets = {
        "data_nascimento": forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
    }
```

`type="date"` faz o navegador mostrar o seletor de calendário nativo.

**O `format` não é decoração.** Sem ele, ao editar um aluno o campo de
data aparece vazio: o navegador só entende `AAAA-MM-DD` e o Django
estaria mandando `dd/mm/aaaa`. É um bug difícil de achar sozinho.

## Limitando as opções de um `<select>`

Para uma FK, o Django lista todos os registros. Para filtrar:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields["aluno"].queryset = Aluno.objects.filter(ativo=True)
```

Filtrar a lista é melhor do que aceitar e depois reclamar — o usuário não
chega nem a ver a opção inválida.

O texto de cada opção vem do `__str__` do modelo. Se o `__str__` não
estiver implementado, o `<select>` mostra `Aluno object (1)` e a tela
fica inutilizável.

## No template

```django
<form method="post" novalidate>
  {% csrf_token %}
  {{ form.non_field_errors }}

  {% for campo in form %}
    <label for="{{ campo.id_for_label }}">{{ campo.label }}</label>
    {{ campo }}
    {% for erro in campo.errors %}<div>{{ erro }}</div>{% endfor %}
  {% endfor %}

  <button type="submit">Salvar</button>
</form>
```

`{% csrf_token %}` é **obrigatório** em todo `<form method="post">`. Sem
ele o Django recusa com 403. Ver o [módulo
06](06-autenticacao-e-permissoes.md).

Os templates do app `academico` já vêm prontos com esse laço — você não
precisa escrever HTML no trabalho.

---

Anterior: [03 — ORM na prática](03-orm-na-pratica.md) ·
Próximo: [05 — Views, URLs e templates](05-views-urls-templates.md)
