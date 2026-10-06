# Notas do professor

> Esta pasta **não vai** no `.zip` entregue aos alunos.

## O gabarito

`gabarito/` tem a solução completa dos TODOs do app `academico`:
`models.py`, `forms.py`, `views.py`, `admin.py`.

Para demonstrar o sistema completo em aula:

```bash
cp gabarito/*.py academico/
python manage.py makemigrations academico
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Para voltar ao esqueleto (o estado em que o aluno recebe):

```bash
git checkout academico/          # se estiver versionado
# ou restaure do backup, e:
rm -f academico/migrations/0*.py escola.sqlite3
```

Com o gabarito instalado, `python verificar.py` dá **55 OK / 0 FALHA**.
Isso é o que garante que os TODOs e a suíte são satisfazíveis — vale
rodar depois de qualquer alteração no enunciado ou nos testes.

## Como preparar o pacote do aluno

Remova do zip:

- `professor/` (esta pasta)
- `gabarito/`
- `escola.sqlite3`, `.venv/`, `__pycache__/`, `.env`
- `academico/migrations/0*.py` — o aluno gera a dele

Mantenha `contas/migrations/0001_initial.py`: sem ela o app de referência
não sobe.

## Decisões de projeto, e por quê

**SQLite, não PostgreSQL.** Zero instalação, zero serviço rodando, e
continuidade direta com a Entrega 1 — o banco volta a ser um arquivo que
abre no DB Browser. O custo é não exercitar cliente/servidor; se quiser
isso depois, trocar o `DATABASES` do `settings.py` é a única mudança.

**Views em função, não CBV.** Cada linha é explícita e defensável na
arguição. As CBVs entram como leitura de bônus no módulo 10, com o mesmo
CRUD lado a lado — quem escreveu na mão entende o atalho.

**`Usuario(AbstractUser)` desde a primeira migration.** Trocar o modelo
de usuário depois é doloroso. Custa cinco linhas hoje.

**`urls.py` do `academico` vem pronto.** Não é generosidade: o
`base.html` referencia aquelas rotas, e um `urls.py` vazio derrubaria o
site inteiro — o aluno não conseguiria nem ver o login. Além disso é o
contrato dos testes.

**Templates prontos.** HTML não é objetivo de aprendizagem da
disciplina, e template pronto faz o TODO falhar pelo motivo certo (a
query está errada) em vez de por typo em `{% for %}`.

**`ordering` comentado no esqueleto.** Aponta para campos que ainda não
existem; se viesse ativo, o `manage.py check` falharia e nada rodaria. O
aluno descomenta ao fazer o TODO.

**Sem migration do `academico`.** O aluno roda `makemigrations` depois
dos TODOs 1-3 e gera tudo de uma vez, sem prompt de default para coluna
não-nula. O `verificar.py` detecta esse estado e orienta.

**Views-placeholder.** Cada view não implementada renderiza uma tela
dizendo qual TODO fazer e onde está o exemplo. O sistema roda desde o
minuto zero — o aluno navega, loga e vê o menu antes de escrever
qualquer linha.

## Sobre a suíte de verificação

`academico/tests/test_entrega.py` — 55 verificações, marcado "não
modifique".

Cada asserção tem mensagem escrita para o aluno, dizendo o que fazer.
Alguns testes que vale conhecer:

- `test_media_funciona_com_nota_zero` — pega quem usou `if not nota` em
  vez de `is None`. Zero é nota válida.
- `test_get_na_exclusao_nao_altera_nada` — pega exclusão no GET.
- `test_listagem_evita_o_problema_n_mais_1` — exige `select_related`.
- `test_editar_altera_o_registro_existente` — pega quem esqueceu o
  `instance=`, checando também que não foi criado um segundo registro.
- `test_nao_ha_sql_montado_com_f_string` — varre o código atrás de
  `.raw(f"...")`.

O `verificar.py` embrulha a suíte e imprime o placar no formato do
`autoteste.py` da Entrega 1, com pré-checagens que dão instrução em vez
de traceback (banco inacessível, migration faltando, migration não
aplicada).

## Ideias para as próximas entregas

- **Entrega 2 (consultas)** — vira ORM: `annotate(Avg(...))`,
  `select_related`, boletim por aluno, média por disciplina, alunos sem
  nota lançada. O módulo 03 já prepara o terreno.
  *Alternativa:* manter SQL cru com `cursor.execute()` contra o mesmo
  banco, e pedir a **mesma** consulta nas duas linguagens. Vira um
  exercício melhor do que qualquer uma das duas isolada.
- **Entrega 3** — deixa de ser "agora com Tkinter": as telas já nascem
  web. Vira paginação, filtros, usabilidade, e talvez o tema escuro.
- **Entrega 4** — integração, apresentação, e a arguição individual.
