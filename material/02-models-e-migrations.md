# 02 — Models e migrations

Leia antes dos **TODO 1, 2 e 3**.

## A ideia central

Um *model* é uma classe Python que descreve uma tabela. Cada atributo da
classe vira uma coluna.

```python
class Aluno(models.Model):
    matricula = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=120)
```

Isso substitui:

```sql
CREATE TABLE aluno (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula TEXT NOT NULL UNIQUE,
    nome      TEXT NOT NULL
);
```

**Você não declara o `id`.** O Django cria a chave primária
auto-incremento sozinha, em todo modelo. Declarar um campo `id` é erro
comum de quem vem do SQL.

## O ciclo da migration

Alterar `models.py` não altera o banco. São dois passos:

```bash
python manage.py makemigrations academico   # 1. escreve o plano
python manage.py migrate                    # 2. executa o plano
```

O `makemigrations` compara os seus modelos com o estado registrado nas
migrations anteriores e gera um arquivo Python descrevendo a diferença —
"criar tabela aluno", "adicionar coluna email". O `migrate` pega esse
plano e roda o SQL correspondente.

Quer ver o SQL? Ele existe:

```bash
python manage.py sqlmigrate academico 0001
```

A saída é o `CREATE TABLE` que você escreveu na mão na Entrega 1. Rode
este comando pelo menos uma vez — é o momento em que a ficha cai.

### Por que dois passos?

Porque a migration é um **arquivo versionado**. Ela entra no Git, e
quando o colega do grupo faz `git pull` e roda `migrate`, o banco dele
fica igual ao seu. Sem isso, cada pessoa teria um banco diferente e
"funciona na minha máquina" viraria rotina.

### Quando rodar

Toda vez que você mexer em `models.py`. Esqueceu? O sintoma é
`no such table` ou `no such column`.

## Os tipos de campo

| Você quer guardar | Campo | Observação |
|---|---|---|
| Texto curto | `CharField(max_length=N)` | `max_length` é obrigatório |
| Texto longo | `TextField()` | sem limite |
| E-mail | `EmailField()` | é um `CharField` que já valida o `@` |
| Número inteiro | `IntegerField()` | |
| Verdadeiro/falso | `BooleanField()` | no SQLite era `INTEGER` 0/1 |
| Data | `DateField()` | vira `date` do Python, não texto |
| Data e hora | `DateTimeField()` | |
| Decimal exato | `DecimalField(max_digits, decimal_places)` | **use para notas** |
| Número quebrado | `FloatField()` | evite para valores que precisam ser exatos |

### Por que `DecimalField` e não `FloatField` para notas

`float` é binário e não representa decimais exatamente:

```python
>>> 0.1 + 0.2
0.30000000000000004
>>> 0.1 + 0.2 == 0.3
False
```

Em nota de aluno, um centésimo decide aprovação. `DecimalField` guarda o
valor exato. (A Entrega 1 usou `REAL` porque o SQLite não oferece coisa
melhor; o Django oferece.)

## `null` e `blank` não são a mesma coisa

Esta é a pegadinha número 1.

- **`null=True`** — a *coluna do banco* aceita `NULL`.
- **`blank=True`** — o *formulário* aceita o campo vazio.

São camadas diferentes: uma é banco, a outra é validação de entrada.

A regra prática:

```python
# Texto opcional: SÓ blank.
email = models.EmailField(blank=True)

# Data ou número opcional: os DOIS.
data_nascimento = models.DateField(null=True, blank=True)
```

Por que a diferença? Porque para texto o Django guarda string vazia
(`""`), e ela já significa "vazio". Se você permitisse `NULL` também,
passaria a existir dois "vazios" diferentes e todo filtro seu teria que
testar os dois. Já para data e número não existe "data vazia" — só
`NULL` serve.

## Chaves estrangeiras

```python
aluno = models.ForeignKey(
    Aluno,
    on_delete=models.PROTECT,
    related_name="inscricoes",
)
```

Isso cria a coluna `aluno_id` e a restrição de integridade.

### `on_delete` é obrigatório

O Django recusa a migration sem ele, porque não há resposta padrão
correta para "e se o aluno for apagado?".

| Opção | O que faz | Quando usar |
|---|---|---|
| `PROTECT` | recusa apagar o aluno se houver inscrição | **histórico acadêmico** |
| `CASCADE` | apaga as inscrições junto | dados que só existem junto com o pai |
| `SET_NULL` | põe `NULL` na FK (exige `null=True`) | quando "sem dono" faz sentido |
| `RESTRICT` | como `PROTECT`, com regra mais fina em cascata | casos raros |

No trabalho, use `PROTECT`. É a tradução direta daquela linha da tabela
de erros da Entrega 1: *"Excluiu um aluno e as notas dele viraram
órfãs"*. Com `PROTECT`, o banco simplesmente não deixa.

Na prática, tentar apagar levanta `ProtectedError`, e a sua view trata:

```python
from django.db.models import ProtectedError

try:
    aluno.delete()
except ProtectedError:
    messages.error(request, "Este aluno tem inscrições e não pode ser excluído.")
```

### `related_name` — o caminho de volta

```python
# Sem related_name, a partir da inscrição:
inscricao.aluno          # funciona sempre

# Com related_name="inscricoes", a partir do aluno:
aluno.inscricoes.all()   # todas as inscrições daquele aluno
```

É o `JOIN` de volta, escrito com um ponto. Sem `related_name`, o Django
inventa o nome `inscricao_set` — funciona, mas lê pior.

## Restrições compostas

`UNIQUE (aluno_id, disciplina_id)` vira:

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["aluno", "disciplina"],
            name="inscricao_unica_por_aluno_disciplina",
        )
    ]
```

O `name` precisa ser único no banco inteiro — por isso o nome longo.

Isso vai no `Meta`, e **só passa a valer depois de `makemigrations` +
`migrate`**. Declarar sem migrar é o mesmo que não declarar.

## A classe `Meta`

```python
class Meta:
    db_table = "aluno"              # nome da tabela
    verbose_name = "aluno"          # como o Django se refere ao modelo
    verbose_name_plural = "alunos"
    ordering = ["nome"]             # ORDER BY padrão de toda consulta
    constraints = [...]
```

**`ordering`** economiza um `.order_by()` em toda consulta. Mas cuidado:
ele aponta para um campo. Se o campo não existir, o projeto inteiro se
recusa a subir — é por isso que, no esqueleto, essa linha vem comentada,
esperando você declarar os campos.

**`db_table`** fixa o nome da tabela. Sem ele, o Django criaria
`academico_aluno`. Fixamos para você reconhecer o banco no DB Browser.

## `__str__` — não é opcional

```python
def __str__(self):
    return f"{self.matricula} - {self.nome}"
```

Sem isso, todo `<select>` de aluno mostra `Aluno object (1)`,
`Aluno object (2)`… e a tela de inscrição fica inutilizável. É uma linha
que muda a usabilidade do sistema inteiro.

## `property` — campo calculado

```python
@property
def media(self):
    if self.nota1 is None or self.nota2 is None:
        return None
    return (self.nota1 + self.nota2) / 2
```

Uma `property` é um método que se usa como atributo: `inscricao.media`,
sem parênteses. Não existe coluna `media` no banco — o valor é calculado
na hora.

**Por que não guardar a média numa coluna?** Porque ela é derivada das
notas. Guardada, ela pode ficar defasada quando alguém corrigir uma nota
e esquecer de recalcular. O princípio: não armazene o que você consegue
calcular.

> **A armadilha do zero.** `if not self.nota1` está errado: zero é falso
> em Python, e zero é nota válida. O aluno que tirou 0 ficaria sem média.
> Compare com `is None`.

## Onde a regra de negócio deve morar

No **modelo**, sempre que possível. A pergunta "qual é a média desta
inscrição?" tem uma resposta só, e ela deve existir num lugar só —
funcionando igual na view, no template, no admin e no teste.

Regra espalhada pelas views é regra que vai divergir.

---

Anterior: [01 — De `sqlite3` cru para Django](01-de-sqlite-cru-para-django.md) ·
Próximo: [03 — ORM na prática](03-orm-na-pratica.md)
