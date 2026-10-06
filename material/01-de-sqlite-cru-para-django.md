# 01 — De `sqlite3` cru para Django

Este é o módulo que dá sentido a todos os outros. Leia antes de abrir o
código.

## O que mudou, de verdade

Na Entrega 1 você escreveu, em `crud_aluno.py`, algo assim:

```python
def inserir_aluno(matricula, nome, email, data_nascimento):
    conexao = sqlite3.connect("escola.db")
    conexao.execute("PRAGMA foreign_keys = ON")
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO aluno (matricula, nome, email, data_nascimento) "
        "VALUES (?, ?, ?, ?)",
        (matricula, nome, email, data_nascimento),
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    conexao.close()
    return novo_id
```

No Django, a mesma coisa é:

```python
aluno = Aluno.objects.create(
    matricula=matricula, nome=nome, email=email,
    data_nascimento=data_nascimento,
)
```

Não é mágica, e é importante você saber o que sumiu:

- **A conexão** sumiu porque o Django abre, reaproveita e fecha por você.
- **O `commit()`** sumiu porque `ATOMIC_REQUESTS = True` no `settings.py`
  embrulha cada requisição HTTP numa transação.
- **O `PRAGMA foreign_keys = ON`** sumiu porque o Django liga sozinho em
  toda conexão SQLite que abre.
- **Os `?`** sumiram porque o ORM parametriza tudo, sempre.
- **O SQL** sumiu porque o Django o gera a partir da sua classe.

Nada disso deixou de acontecer. Tudo continua acontecendo — só que num
lugar que você não precisa mais escrever nem lembrar.

## A tabela de tradução

| Entrega 1 (`sqlite3`) | Django | Onde ver no projeto |
|---|---|---|
| `CREATE TABLE aluno (...)` | `class Aluno(models.Model)` | `academico/models.py` |
| Rodar `python database.py` | `makemigrations` + `migrate` | [módulo 02](02-models-e-migrations.md) |
| `INTEGER PRIMARY KEY AUTOINCREMENT` | (nada — o Django cria o `id`) | [módulo 02](02-models-e-migrations.md) |
| `TEXT NOT NULL UNIQUE` | `CharField(max_length=20, unique=True)` | [módulo 02](02-models-e-migrations.md) |
| `FOREIGN KEY ... REFERENCES` | `ForeignKey(Modelo, on_delete=...)` | [módulo 02](02-models-e-migrations.md) |
| `UNIQUE (a, b)` | `UniqueConstraint(fields=["a", "b"], ...)` | [módulo 02](02-models-e-migrations.md) |
| `SELECT * FROM aluno` | `Aluno.objects.all()` | [módulo 03](03-orm-na-pratica.md) |
| `WHERE nome LIKE ?` | `.filter(nome__icontains=...)` | [módulo 03](03-orm-na-pratica.md) |
| `JOIN aluno ON ...` | `.select_related("aluno")` | [módulo 03](03-orm-na-pratica.md) |
| `INSERT INTO ... VALUES (?, ?)` | `form.save()` / `.objects.create()` | [módulo 04](04-forms-e-validacao.md) |
| `UPDATE ... WHERE id = ?` | `Form(..., instance=obj).save()` | [módulo 04](04-forms-e-validacao.md) |
| `DELETE FROM ... WHERE id = ?` | `obj.delete()` | [módulo 05](05-views-urls-templates.md) |
| `conexao.commit()` | `ATOMIC_REQUESTS` (automático) | `config/settings.py` |
| `PRAGMA foreign_keys = ON` | (automático) | `config/settings.py` |
| `input()` no `main.py` | o `<form>` no template | [módulo 05](05-views-urls-templates.md) |
| `print()` no `main.py` | `{{ variavel }}` no template | [módulo 05](05-views-urls-templates.md) |
| `print("Cadastrado!")` | `messages.success(request, ...)` | [módulo 05](05-views-urls-templates.md) |
| menu `while True` | `urls.py` | [módulo 05](05-views-urls-templates.md) |
| `autoteste.py` | `python verificar.py` | [módulo 08](08-roteiro-do-trabalho.md) |

## As regras da Entrega 1, revisitadas

O enunciado da Entrega 1 tinha sete requisitos "não negociáveis". Veja o
que aconteceu com cada um:

**1. SQLite pelo módulo `sqlite3`.** Continua SQLite. O Django fala com
ele por você.

**2. Parâmetros com `?`, nunca f-string.** O ORM parametriza tudo
sozinho. A brecha de SQL Injection só volta se você apelar para
`.raw()` com f-string — e aí o item continua zerado.

**3. `commit()` depois de todo INSERT/UPDATE/DELETE.** Virou
`ATOMIC_REQUESTS`. Agora é impossível esquecer.

**4. `WHERE` obrigatório em UPDATE e DELETE.** Garantido pelo ORM: quando
você chama `obj.delete()`, ele sempre filtra pela chave primária daquele
objeto. Não existe `DELETE FROM aluno` por descuido.

**5. Separação de responsabilidades.** Continua valendo, e é o item mais
importante. Lá: nada de `print()` dentro do CRUD. Aqui: nada de HTML
dentro da view. A view consulta, decide e entrega dados; o template
exibe.

**6. Tratar cadastro duplicado.** O `unique=True` no modelo faz o
`ModelForm` transformar a violação em mensagem de campo automaticamente.
Ganho de graça — desde que você declare o `unique=True`.

**7. `PRAGMA foreign_keys = ON`.** Automático.

Cinco dos sete viraram responsabilidade do framework. Os dois que
sobraram — **separação de responsabilidades** e **não montar SQL na mão**
— são justamente os que dependem de julgamento, não de digitação.

Isso é o RAD: o framework assume o trabalho mecânico para você gastar
atenção onde ela decide alguma coisa.

## O que você ganha em troca

Uma pergunta justa: se o Django faz tudo isso, por que aprender SQL
antes?

Porque quando algo der errado — e vai — o erro aparece em SQL. A
listagem lenta do [módulo 03](03-orm-na-pratica.md) é um `SELECT` por
linha. O `IntegrityError` é uma restrição do banco. Quem não sabe o que
está acontecendo embaixo fica refém do framework.

Você aprendeu a fazer na mão para poder entender o que a máquina faz por
você. Essa ordem não é acidente.

## E as próximas entregas?

- **Entrega 2 (consultas)** — os mesmos `SELECT`, `WHERE` e `JOIN`,
  escritos como QuerySet. [Módulo 03](03-orm-na-pratica.md).
- **Entrega 3 (interface)** — as telas já nascem web neste projeto; a
  entrega vira refino: busca, paginação, usabilidade.
- **Entrega 4 (aplicação final)** — integração e apresentação.

---

Próximo: [02 — Models e migrations](02-models-e-migrations.md)
