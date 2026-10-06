# 08 — Roteiro do trabalho

Os 13 TODOs, na ordem recomendada, com o critério de "pronto" de cada um.

## Como saber onde você está

```bash
python verificar.py
```

Ele roda a suíte `academico/tests/` e imprime o placar. **No começo quase
tudo falha — isso é o seu mapa, não um problema.** Cada falha diz qual
TODO fazer e onde.

Para ver o traceback completo de uma falha:

```bash
python manage.py test academico -v 2
```

> `academico/tests/test_entrega.py` é **para não modificar**. Alterar o
> teste para ele passar não faz o código funcionar — faz o teste parar de
> dizer a verdade. Achou que um teste está errado? Chame o professor.

## A ordem

### Bloco 1 — o modelo (TODO 1, 2, 3)

Faça os três **juntos**, depois migre uma vez só. Assim o
`makemigrations` gera uma migration limpa, sem perguntar default para
coluna nova em tabela existente.

| TODO | Arquivo | Pronto quando |
|---|---|---|
| 1 | `models.py` :: `Aluno` | campos, `unique` na matrícula, `__str__` |
| 2 | `models.py` :: `Disciplina` | campos, `unique` no código, `__str__` |
| 3 | `models.py` :: `Inscricao` | FKs com `on_delete=PROTECT`, `related_name`, `UniqueConstraint`, `media` |

Depois:

```bash
python manage.py makemigrations academico
python manage.py migrate
python manage.py sqlmigrate academico 0001   # veja o CREATE TABLE gerado
python manage.py seed_demo                   # agora carrega alunos e notas
python verificar.py
```

Não esqueça de **descomentar as linhas `ordering`** no `Meta` dos três
modelos — elas vêm comentadas porque apontam para campos que ainda não
existiam.

Leitura: [módulo 02](02-models-e-migrations.md).

### Bloco 2 — os formulários (TODO 4, 5, 6)

Rápidos: cada um é uma lista de campos no `Meta`. As validações do bônus
podem ficar para depois.

| TODO | Arquivo | Pronto quando |
|---|---|---|
| 4 | `forms.py` :: `AlunoForm` | `fields` preenchido, widget de data com `format` |
| 5 | `forms.py` :: `DisciplinaForm` | `fields` preenchido |
| 6 | `forms.py` :: `InscricaoForm` | `fields` preenchido |

Leitura: [módulo 04](04-forms-e-validacao.md).

### Bloco 3 — o CRUD de aluno (TODO 7, 8, 9)

**Este é o bloco que importa.** Os TODOs 10 a 12 são repetição do mesmo
padrão; se este ficar bom, o resto sai rápido.

| TODO | View | Pronto quando |
|---|---|---|
| 7 | `aluno_lista` | lista aparece e a busca filtra |
| 8 | `aluno_novo` | cadastra, redireciona, e erro volta o form preenchido |
| 9a | `aluno_editar` | **altera** (não cria outro), 404 em id inexistente |
| 9b | `aluno_excluir` | GET confirma, POST executa |

Trabalhe com `contas/views.py` aberto ao lado. Leitura: [módulo
05](05-views-urls-templates.md) e [módulo 07](07-tour-do-app-contas.md).

### Bloco 4 — disciplina e notas (TODO 10, 11, 12)

| TODO | View | Observação |
|---|---|---|
| 10 | `disciplina_lista` | espelha o TODO 7 |
| 11 | `disciplina_nova/editar/excluir` | espelha o TODO 8 e 9 |
| 12 | `inscricao_*` | **atenção ao `select_related`** |

O TODO 12 é o único com assunto novo: a listagem mostra dados de outras
tabelas. Sem `select_related`, são 2 consultas extras por linha. Leitura:
[módulo 03](03-orm-na-pratica.md), seção "problema N+1".

### Bloco 5 — bônus

| TODO | Arquivo | Vale |
|---|---|---|
| 13 | `admin.py` | inspeção dos dados |
| — | soft delete no aluno | +0,5 (explique no README) |
| — | validações amigáveis | +0,5 |

## Divisão sugerida para o grupo

Com 3 ou 4 pessoas:

| Quem | O quê |
|---|---|
| **Todos, juntos** | Bloco 1 (o modelo). É a fundação — decidir junto evita retrabalho. |
| Pessoa A | TODO 4 e 7-9 (aluno) |
| Pessoa B | TODO 5 e 10-11 (disciplina) |
| Pessoa C | TODO 6 e 12 (inscrições e notas) |
| Pessoa D (ou A) | README, diagrama, bônus, revisão |

> **Todo mundo precisa entender o código todo.** Qualquer integrante pode
> ser chamado a explicar qualquer trecho, ou a fazer uma alteração ao
> vivo. Reserve trinta minutos no fim para cada um apresentar o seu
> pedaço ao grupo — é a melhor preparação possível, e sai de graça.

## Antes de entregar

```bash
python verificar.py          # tem que dar 0 FALHA
python manage.py test        # os dois apps
python manage.py runserver   # e navegue como um usuário faria
```

Teste passando não é o mesmo que sistema usável. Cadastre um aluno de
verdade, tente quebrar, veja se a mensagem faz sentido.

**Checklist do `.zip`:**

- [ ] `verificar.py` com 0 FALHA
- [ ] `README.md` preenchido (modelo, decisões, uso de IA)
- [ ] `modelo_dados.png` legível e coerente com o código
- [ ] **Sem** `escola.sqlite3`, `.venv/`, `__pycache__/`, `.env`
- [ ] As migrations **incluídas** (elas são código, vão no zip)
- [ ] Nome: `ARA0095_Django_<sobrenomes>.zip`

> O banco não vai no zip porque é **gerado** pelo código. As migrations
> vão, porque são o código que o gera. Mesma regra da Entrega 1: se o
> projeto não recria o banco do zero, ele está errado.

---

Anterior: [07 — Tour do app `contas`](07-tour-do-app-contas.md) ·
Próximo: [09 — Erros comuns](09-erros-comuns.md)
