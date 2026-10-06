# 03 — ORM na prática

Leia antes dos **TODO 7 e 12**. Este é também o módulo que prepara a
**Entrega 2**.

## QuerySet: a receita, não o resultado

```python
alunos = Aluno.objects.all()
```

Isso **não** foi ao banco. Um QuerySet é *preguiçoso*: ele guarda a
receita da consulta e só executa quando alguém precisa dos dados de fato.

```python
alunos = Aluno.objects.all()          # nada aconteceu
alunos = alunos.filter(ativo=True)    # nada aconteceu
alunos = alunos.order_by("nome")      # nada aconteceu

for aluno in alunos:                  # AGORA vai ao banco, uma vez
    print(aluno.nome)
```

Por isso você pode montar a consulta em etapas, com `if`, sem custo
nenhum — é exatamente o que a view de listagem faz ao aplicar a busca.

O QuerySet vai ao banco quando você: itera com `for`, chama `list()`,
`len()`, `count()`, `exists()`, ou usa índice/fatia.

### O cache

Depois de avaliado, o QuerySet guarda o resultado. Iterar de novo **não**
consulta outra vez. Se você quiser forçar uma nova consulta, use `.all()`
para pegar um clone limpo.

## A tabela de tradução

| SQL | ORM |
|---|---|
| `SELECT * FROM aluno` | `Aluno.objects.all()` |
| `WHERE ativo = 1` | `.filter(ativo=True)` |
| `WHERE ativo <> 1` | `.exclude(ativo=True)` |
| `WHERE id = 5` | `.get(pk=5)` |
| `WHERE nome LIKE '%ana%'` | `.filter(nome__icontains="ana")` |
| `WHERE carga_horaria > 60` | `.filter(carga_horaria__gt=60)` |
| `WHERE periodo IN (1,2)` | `.filter(periodo__in=[1, 2])` |
| `WHERE email IS NULL` | `.filter(email__isnull=True)` |
| `ORDER BY nome` | `.order_by("nome")` |
| `ORDER BY nome DESC` | `.order_by("-nome")` |
| `LIMIT 10` | `[:10]` |
| `COUNT(*)` | `.count()` |
| `SELECT DISTINCT` | `.distinct()` |

### Os *lookups*

O `__` (dois sublinhados) separa o campo do tipo de comparação:

| Lookup | Significa |
|---|---|
| `__exact` | igual (é o padrão, pode omitir) |
| `__iexact` | igual, ignorando maiúsculas |
| `__contains` | contém |
| `__icontains` | contém, ignorando maiúsculas |
| `__startswith` / `__endswith` | começa / termina com |
| `__gt` / `__gte` | maior / maior ou igual |
| `__lt` / `__lte` | menor / menor ou igual |
| `__in` | está na lista |
| `__isnull` | é `NULL` |
| `__year` / `__month` | parte de uma data |

## `AND` e `OR`

Vários `filter` encadeados viram `AND`:

```python
Aluno.objects.filter(ativo=True).filter(nome__icontains="ana")
# WHERE ativo = 1 AND nome LIKE '%ana%'
```

Para `OR`, use `Q`:

```python
from django.db.models import Q

Aluno.objects.filter(
    Q(nome__icontains=busca) | Q(matricula__icontains=busca)
)
# WHERE nome LIKE %busca% OR matricula LIKE %busca%
```

`|` é OR, `&` é AND, `~` é NOT. É a ferramenta da busca do TODO 7.

## `get()` versus `filter()`

```python
aluno = Aluno.objects.get(pk=5)       # UM objeto, ou explode
alunos = Aluno.objects.filter(pk=5)   # um QuerySet (com 0 ou 1 item)
```

`get()` levanta `DoesNotExist` se não achar e `MultipleObjectsReturned`
se achar mais de um. Numa view, quase sempre você quer:

```python
from django.shortcuts import get_object_or_404
aluno = get_object_or_404(Aluno, pk=pk)
```

que devolve o objeto ou responde 404 — substituindo o `if aluno is None`
da Entrega 1.

## Atravessando relacionamentos — o `JOIN`

O `__` também atravessa chaves estrangeiras:

```python
# Inscrições da disciplina cujo código é ARA0095
Inscricao.objects.filter(disciplina__codigo="ARA0095")

# Alunos que têm ao menos uma inscrição em ARA0095
Aluno.objects.filter(inscricoes__disciplina__codigo="ARA0095").distinct()
```

O `.distinct()` na segunda importa: o JOIN repete o aluno uma vez por
inscrição que casar.

E no sentido de volta, via `related_name`:

```python
aluno.inscricoes.all()                       # inscrições de um aluno
disciplina.inscricoes.count()                # quantos alunos na disciplina
```

## O problema N+1 — leia com atenção

Este é o erro de desempenho mais comum em Django, e ele é silencioso: o
sistema funciona, só fica lento.

```python
inscricoes = Inscricao.objects.all()

for i in inscricoes:
    print(i.aluno.nome)        # <- uma consulta EXTRA, a cada volta
    print(i.disciplina.nome)   # <- outra
```

Com 50 inscrições: 1 consulta para a lista + 100 consultas para os dados
relacionados = **101 consultas**. Com 500, mais de mil.

A solução é avisar antes o que você vai usar:

```python
inscricoes = Inscricao.objects.select_related("aluno", "disciplina")
```

`select_related` faz o `JOIN` e traz tudo em **uma** consulta.

| Método | Para que serve |
|---|---|
| `select_related` | `ForeignKey` (o "muitos para um") — faz `JOIN` |
| `prefetch_related` | `ManyToMany` e o inverso da FK — faz 2 consultas e junta no Python |

Regra prática: se o template acessa `objeto.outro_objeto.campo`, use
`select_related("outro_objeto")`.

## Agregações — a Entrega 2 começa aqui

```python
from django.db.models import Avg, Count, Max, Min, Sum
```

**Sobre a tabela toda** (`.aggregate` devolve um dicionário):

```python
Inscricao.objects.aggregate(Avg("nota1"))
# {'nota1__avg': 7.2}

Aluno.objects.filter(ativo=True).aggregate(total=Count("id"))
# {'total': 8}
```

**Por linha** (`.annotate` acrescenta uma coluna calculada a cada
objeto):

```python
disciplinas = Disciplina.objects.annotate(
    total_alunos=Count("inscricoes"),
    media_turma=Avg("inscricoes__nota1"),
)

for d in disciplinas:
    print(d.nome, d.total_alunos, d.media_turma)
```

Isso é um `GROUP BY` — e resolve sozinho boa parte dos relatórios da
Entrega 2.

## Espiando o SQL gerado

Você não precisa confiar cegamente. Abra o shell:

```bash
python manage.py shell
```

```python
>>> from academico.models import Inscricao
>>> qs = Inscricao.objects.select_related("aluno").filter(nota1__gte=7)
>>> print(qs.query)
SELECT "inscricao"."id", ... FROM "inscricao"
INNER JOIN "aluno" ON ("inscricao"."aluno_id" = "aluno"."id")
WHERE "inscricao"."nota1" >= 7
```

Para contar quantas consultas um trecho fez:

```python
>>> from django.db import connection, reset_queries
>>> reset_queries()
>>> lista = list(Inscricao.objects.all())
>>> for i in lista: _ = i.aluno.nome
>>> len(connection.queries)     # veja o N+1 com os próprios olhos
```

(Só funciona com `DEBUG = True`.)

**Use esses dois comandos.** Eles transformam o ORM de caixa-preta em
ferramenta — e são a melhor preparação possível para a arguição oral.

## E quando o ORM não dá conta?

Existe saída:

```python
Aluno.objects.raw("SELECT * FROM aluno WHERE matricula = %s", [matricula])
```

Repare no `%s` com a lista de parâmetros: é o mesmo `?` com tupla da
Entrega 1, pelo mesmo motivo. **Montar essa string com f-string reabre a
brecha de SQL Injection e zera o item 4 da rubrica.**

Na prática, você não vai precisar de `raw()` neste trabalho.

---

Anterior: [02 — Models e migrations](02-models-e-migrations.md) ·
Próximo: [04 — Forms e validação](04-forms-e-validacao.md)
