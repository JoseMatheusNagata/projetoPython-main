# 09 — Erros comuns

No formato da tabela de erros da Entrega 1: sintoma → causa quase sempre.

## Ambiente

| Sintoma | Causa quase sempre |
|---|---|
| `ModuleNotFoundError: No module named 'django'` | Esqueceu de ativar o `.venv` |
| `command not found: python` | Use `python3` |
| `No module named 'venv'` | Falta `python3-venv` (Linux: `sudo apt install python3-venv`) |
| `That port is already in use` | Já tem servidor rodando: use `runserver 8001` |
| Mudei o HTML e a página não muda | Salvou o arquivo? Rodou com `--noreload`? |

## Banco e migrations

| Sintoma | Causa quase sempre |
|---|---|
| `no such table: aluno` | Faltou `makemigrations` + `migrate`, ou os TODOs 1-3 |
| `no such column: aluno.email` | Alterou o modelo e não migrou |
| `Your models have changes that are not yet reflected in a migration` | Exatamente isso: rode `makemigrations` |
| `You are trying to add a non-nullable field...` | Está adicionando campo obrigatório a tabela com dados. Faça os TODOs 1-3 juntos, antes da primeira migration |
| `UNIQUE constraint failed: aluno.matricula` | Matrícula repetida — **é o banco te protegendo** |
| `FOREIGN KEY constraint failed` | Apontando para um id que não existe |
| `ProtectedError` ao excluir | `on_delete=PROTECT` funcionando: há inscrições. Trate com `try/except` |

> **Deu ruim de vez nas migrations?** Em ambiente de estudo, com dados de
> exemplo, vale recomeçar:
> ```bash
> rm escola.sqlite3
> rm academico/migrations/0*.py
> python manage.py makemigrations academico
> python manage.py migrate
> python manage.py seed_demo
> ```
> Isso **nunca** se faz em produção. Aqui pode, porque o banco é gerado
> pelo código — que é justamente o ponto.

## Models

| Sintoma | Causa quase sempre |
|---|---|
| `'ordering' refers to the nonexistent field` | Descomentou o `ordering` antes de declarar o campo |
| `ForeignKey must be provided with on_delete` | Falta o `on_delete` — não existe padrão |
| `<select>` mostra `Aluno object (1)` | Falta o `__str__` (TODO 1b) |
| Aluno com nota 0 aparece sem média | `if not self.nota1` — zero é falso. Use `is None` |
| `NOT NULL constraint failed` | Campo obrigatório ficando vazio: falta `null=True`/`blank=True`, ou o `clean_` esqueceu o `return` |

## Forms

| Sintoma | Causa quase sempre |
|---|---|
| Formulário vazio na tela | `fields = []` — preencha o `Meta` (TODO 4/5/6) |
| Editar **cria** outro registro | Falta `instance=objeto` |
| Campo de data vazio ao editar | Falta `format="%Y-%m-%d"` no widget |
| Campo salvo como `None` sem erro | O `clean_<campo>` esqueceu o `return` |
| `'AlunoForm' object has no attribute 'cleaned_data'` | Usou `cleaned_data` antes de `is_valid()` |
| Erro de duplicidade sempre ao editar | Falta `.exclude(pk=self.instance.pk)` |

## Views e templates

| Sintoma | Causa quase sempre |
|---|---|
| **Página em branco, sem erro** | Nome errado na variável de contexto. O template ignora variável inexistente em silêncio |
| `NoReverseMatch` | Nome de rota errado, faltou o namespace (`academico:`) ou o argumento |
| 403 ao enviar formulário | Faltou `{% csrf_token %}` |
| F5 duplica o cadastro | Faltou o `redirect` depois do `save()` |
| `TemplateDoesNotExist` | Nome ou caminho errado no `render` |
| `'block' tag takes only one argument` | `{# #}` com mais de uma linha. Use `{% comment %}` |
| `{% extends %} must be the first tag` | Tem alguma tag antes do `extends` |
| Texto de comentário aparecendo na tela | `{# #}` multi-linha — o mesmo problema |
| Nota 0 aparece como "--" | `\|default` em vez de `\|default_if_none` |
| Listagem lenta com muitos registros | Problema N+1: falta `select_related` |

## Autenticação

| Sintoma | Causa quase sempre |
|---|---|
| Login não funciona com a senha certa | Criou com `objects.create` em vez de `create_user` — senha sem hash |
| Usuário não consegue entrar | `is_active=False` (foi desativado) |
| Loop na tela de login | Redirecionando para o login quem já está logado. Use 403 |
| 403 inesperado | Perfil sem permissão, ou faltou `{% csrf_token %}` |
| Comando `seed_demo` não existe | Falta algum `__init__.py` em `management/` ou `management/commands/` |

## Testes

| Sintoma | Causa quase sempre |
|---|---|
| `verificar.py` diz que não há migration | Faça os TODOs 1-3 e rode `makemigrations academico` |
| Testes passam mas a tela não funciona | Teste passando ≠ sistema usável. Navegue de verdade |
| `assertNumQueries` falhando | Falta `select_related` (TODO 12a) |

## Como pedir ajuda direito

Ao chamar o professor ou postar no grupo, traga:

1. **O comando** que você rodou
2. **A mensagem de erro completa** — a última linha costuma ser a que
   importa, mas mande tudo
3. **O que você já tentou**

"Não funciona" não dá para depurar. `NoReverseMatch at /academico/alunos/`
dá.

E leia a última linha do traceback antes de pedir ajuda. Ela quase sempre
diz exatamente o que está errado — o Django é bom nisso.

---

Anterior: [08 — Roteiro do trabalho](08-roteiro-do-trabalho.md) ·
Próximo: [10 — Glossário e CBV](10-glossario-e-cbv.md)
