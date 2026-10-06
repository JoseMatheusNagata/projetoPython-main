# Entrega — Sistema de Registro Acadêmico em Django

**Disciplina:** ARA0095 — Desenvolvimento Rápido de Aplicações em Python
**Modalidade:** grupos de 3 a 4 alunos
**Base:** projeto base fornecido pelo professor

---

## 1. Por que esta entrega existe

Na Entrega 1 você construiu o CRUD conversando com o SQLite na mão:
`CREATE TABLE`, `INSERT ... VALUES (?, ?)`, `commit()`, `PRAGMA
foreign_keys = ON`. Funcionava, e era trabalhoso — cada operação exigia
abrir conexão, montar SQL, parametrizar, confirmar e fechar.

Agora você faz a mesma coisa uma camada acima, com Django. O banco
continua sendo SQLite. O que muda é quem escreve o SQL.

O ponto pedagógico é ver **o que o framework assume** e **o que continua
sendo sua responsabilidade**. Spoiler: cinco dos sete requisitos "não
negociáveis" da Entrega 1 passam a ser automáticos. Os dois que sobram
são os que dependem de julgamento, não de digitação.

---

## 2. O que você recebe pronto

O projeto base já roda. Nele:

- **Login funcionando**, com senha em hash e controle de sessão
- **Gestão de usuários completa** — as cinco operações de CRUD,
  comentadas linha a linha, com controle de acesso por perfil
- **Todos os templates**, inclusive os do app que você vai implementar
- **Material de estudo** — 11 documentos em `material/`
- **Verificação automática** — `python verificar.py`

O app `contas` não é enfeite: ele é a **implementação de referência**.
Cada arquivo dele responde uma pergunta que você vai ter. Abra os dois
apps lado a lado.

### Como entrar

Depois de instalar (manual completo no `README.md`) e rodar
`python manage.py seed_demo`:

| | |
|---|---|
| **Usuário** | `admin` |
| **Senha** | `escola2024` |

Há também `coordenacao`, `professor` e `secretaria`, com a mesma senha,
para você ver o controle de acesso por perfil. Entre com `professor` e
tente abrir `/contas/usuarios/`: recebe **403**.

---

## 3. O que você implementa

O app `academico`: alunos, disciplinas e o relacionamento N:N entre eles,
com notas.

São **13 TODOs numerados**, cada um com docstring explicando o que fazer,
onde está o exemplo equivalente e qual a armadilha.

| TODO | O quê | Arquivo |
|---|---|---|
| 1-3 | Modelos `Aluno`, `Disciplina`, `Inscricao` | `academico/models.py` |
| 4-6 | Os três `ModelForm` | `academico/forms.py` |
| 7-9 | CRUD de aluno | `academico/views.py` |
| 10-11 | CRUD de disciplina | `academico/views.py` |
| 12 | Inscrições e lançamento de notas | `academico/views.py` |
| 13 | Registro no admin (bônus) | `academico/admin.py` |

**Você não precisa escrever HTML.** Os templates vêm prontos. Eles
esperam nomes específicos de variável no contexto, e cada TODO diz quais.

---

## 4. O modelo de dados

Os mesmos nomes de tabela e coluna da Entrega 1 — `aluno`, `disciplina`,
`inscricao`. Abra o `escola.sqlite3` no DB Browser e você vai reconhecer
o esquema que você mesmo modelou em SQL.

A pergunta da arguição continua a mesma: **por que `nota1` fica em
`inscricao`, e não em `aluno` nem em `disciplina`?**

---

## 5. Requisitos técnicos (não negociáveis)

1. **Migrations versionadas.** As alterações do banco vão no `.zip` como
   código. O `escola.sqlite3`, não — o banco é gerado por `migrate`.
2. **Nada de SQL montado com f-string.** O ORM parametriza sozinho. Se
   apelar para `.raw()` com f-string, **o item 4 da rubrica é zerado** —
   é a mesma brecha de SQL Injection da Entrega 1.
3. **`on_delete` explícito** em toda chave estrangeira, com justificativa
   no README.
4. **`UniqueConstraint`** composta em `inscricao` — o mesmo
   `UNIQUE (aluno_id, disciplina_id)`.
5. **Separação de responsabilidades.** A view não monta HTML; o template
   não consulta o banco; a regra de negócio mora no modelo. É o item 5 da
   Entrega 1, do outro lado.
6. **`{% csrf_token %}`** em todo formulário POST.
7. **Exclusão só no POST.** GET mostra a confirmação. Um link que apaga
   dados é disparado por robô de busca e por pré-carregador do navegador.
8. **`@login_required`** em todas as views do app acadêmico.
9. **Duplicidade vira mensagem**, não traceback.

---

## 6. Roteiro

Em `material/08-roteiro-do-trabalho.md`, com a ordem recomendada, o
critério de "pronto" de cada TODO e uma sugestão de divisão para o grupo.

O resumo:

1. **Juntos:** os TODOs 1-3 (o modelo). Depois `makemigrations` +
   `migrate` uma vez só.
2. Rode `python manage.py sqlmigrate academico 0001` e veja o
   `CREATE TABLE` que o Django gerou a partir das suas classes.
3. Os formulários (4-6) — rápidos.
4. O CRUD de aluno (7-9) — **é o bloco que importa**; o resto é
   repetição do mesmo padrão.
5. Disciplina (10-11) e notas (12).
6. `python verificar.py` até dar **0 FALHA**.
7. README, diagrama, `.zip`.

---

## 7. O que entregar

`ARA0095_Django_<sobrenomes>.zip` contendo o projeto, **com as
migrations** e **sem**:

- `escola.sqlite3` — o banco é gerado pelo código
- `.venv/` — cada um cria o seu
- `__pycache__/`
- `.env`

Mais o `README.md` preenchido e o `modelo_dados.png`.

---

## 8. Avaliação

| # | Critério | Pontos |
|---|---|---|
| 1 | **Modelo de dados** — três modelos, tipos e restrições corretos, `on_delete` justificado, `UniqueConstraint`, `__str__`, migrations aplicadas, diagrama coerente | 2,0 |
| 2 | **CRUD de aluno** — as quatro views funcionando, com busca | 2,0 |
| 3 | **CRUD de disciplina e inscrições** — incluindo `select_related` na listagem de notas | 2,0 |
| 4 | **Qualidade técnica** — ORM sem SQL na mão, `instance=` no editar, POST/Redirect/GET, exclusão só no POST, `csrf_token`, `login_required`, separação de responsabilidades | 2,0 |
| 5 | **README, organização e arguição** — README preenchido com modelo, decisões e uso de IA; projeto navegável sem travar | 2,0 |
| — | **Total** | **10,0** |

### Bônus (até +1,0, não ultrapassa 10,0)

- **+0,5** — soft delete no aluno (`ativo = False`), com a listagem
  mostrando só os ativos. Explique no README o que se ganha e o que se
  perde num sistema acadêmico.
- **+0,5** — validações amigáveis: e-mail, carga horária positiva, nota
  entre 0 e 10, normalização de código de disciplina. Diga no README
  **onde** cada uma foi feita (modelo ou formulário) e por quê.

### Descontos

- `escola.sqlite3`, `.venv/` ou `__pycache__/` no zip: **−0,5**
- Migrations faltando (o projeto não sobe do zero): **−1,0**
- Projeto que não roda por erro de sintaxe: **−2,0**
- SQL montado com f-string: **item 4 zerado**

---

## 9. Sobre uso de IA

Você pode usar assistentes de IA. Mas o grupo inteiro será **arguido
oralmente**: qualquer integrante pode ser chamado a explicar qualquer
trecho, ou a fazer uma alteração pequena ao vivo.

**Código que o grupo não sabe explicar vale zero**, independentemente de
funcionar.

Registre no README o que foi gerado com auxílio de IA e o que o grupo
revisou. Isso é boa prática profissional, não delação.

As dez perguntas do fim de `material/07-tour-do-app-contas.md` são uma
amostra realista do que será perguntado. Se o grupo responde àquelas,
está preparado.

---

## 10. Material de apoio

- `material/` — 11 documentos, do zero ao glossário. Comece pelo
  [índice](../material/README.md).
- **DB Browser for SQLite** — <https://sqlitebrowser.org>
- Documentação do Django em português —
  <https://docs.djangoproject.com/pt-br/5.2/>
- Django Girls Tutorial (em português, excelente para começar) —
  <https://tutorial.djangogirls.org/pt/>

---

**Uma última coisa.** O objetivo não é o CRUD — você já fez CRUD. É
entender o que um framework assume por você, o que ele **não** assume, e
saber decidir a diferença. Essa é a habilidade que sobrevive à próxima
mudança de tecnologia.
