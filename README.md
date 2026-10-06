# Sistema de Registro Acadêmico — projeto base Django

**ARA0095 — Desenvolvimento Rápido de Aplicações em Python**

Projeto base para o Trabalho da Disciplina. Login e gestão de usuários
**já funcionam** e servem de implementação de referência; o app acadêmico
(alunos, disciplinas e notas) é o que você implementa.

---

## Credenciais padrão

Depois de rodar o `seed_demo` (passo 6 da instalação), entre com:

| | |
|---|---|
| **Usuário** | `admin` |
| **Senha** | `escola2024` |

Essa conta é superusuário: abre o sistema **e** o painel `/admin/`.

Existem mais três contas, todas com a mesma senha, para você ver o
controle de acesso por perfil funcionando:

| Usuário | Senha | Perfil | Enxerga a gestão de usuários? |
|---|---|---|---|
| `admin` | `escola2024` | Coordenação (superusuário) | sim |
| `coordenacao` | `escola2024` | Coordenação | sim |
| `professor` | `escola2024` | Professor | não — recebe 403 |
| `secretaria` | `escola2024` | Secretaria | não — recebe 403 |

Entre com `professor` e repare que o item "Usuários" some do menu. Depois
digite `/contas/usuarios/` na barra de endereço: você recebe **403**, e
não a tela. Esconder o link é cortesia; a proteção está na view.

> Senha única e escrita no código só porque isto é **ambiente de
> estudo**. Em produção, nada disso existe: cada pessoa define a própria
> senha e o arquivo de credenciais nunca é versionado.

---

# Manual de instalação

Funciona igual em Windows, Linux e macOS. Onde houver diferença, ela está
marcada.

**Não é preciso instalar banco de dados.** O projeto usa SQLite — o mesmo
da Entrega 1 — que já vem embutido no Python. O banco é um arquivo.

## Passo 1 — Instalar o Python

Você precisa da versão **3.10 ou mais nova**.

### Windows

1. Baixe em <https://www.python.org/downloads/windows/>
2. Execute o instalador e — **isto é o mais importante** — marque a caixa
   **"Add python.exe to PATH"** na primeira tela, antes de clicar em
   "Install Now".
3. Se você esquecer de marcar, o Windows não vai encontrar o comando
   `python`. A correção é rodar o instalador de novo, escolher "Modify" e
   marcar a opção.

### Linux (Debian, Ubuntu, Mint)

```bash
sudo apt update
sudo apt install python3 python3-venv
```

O pacote `python3-venv` é separado em algumas distribuições e é
obrigatório. Sem ele, o passo 3 falha com `No module named 'venv'`.

### macOS

```bash
brew install python
```

### Confira

Abra um terminal e rode:

```bash
python --version      # Windows
python3 --version     # Linux / macOS
```

Deve aparecer algo como `Python 3.12.3`.

> **Qual terminal?**
> No Windows: PowerShell (tecle `Win`, digite "PowerShell").
> No Linux: o Terminal.
> Nos exemplos a seguir, use `python` no Windows e `python3` no Linux e
> no macOS.

## Passo 2 — Entrar na pasta do projeto

Descompacte o `.zip` e entre na pasta pelo terminal:

```bash
cd caminho/para/projetoPython
```

No Windows, um atalho: abra a pasta no Explorador de Arquivos, clique na
barra de endereço, digite `powershell` e tecle Enter. O terminal abre já
na pasta certa.

Confira que você está no lugar certo — o arquivo `manage.py` precisa
estar aqui:

```bash
dir manage.py      # Windows
ls manage.py       # Linux / macOS
```

## Passo 3 — Criar o ambiente virtual

```bash
python -m venv .venv       # Windows
python3 -m venv .venv      # Linux / macOS
```

Isso cria a pasta `.venv`, com um Python isolado só deste projeto.

**Por que isso importa:** sem o ambiente virtual, o `pip install` joga o
Django na instalação global do sistema. Aí o próximo projeto que precisar
de outra versão quebra este. O `.venv` é uma caixa por projeto — e por
isso ele **não vai** no `.zip` da entrega: cada pessoa cria o seu.

## Passo 4 — Ativar o ambiente virtual

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

Deu o erro **"execução de scripts foi desabilitada neste sistema"**? É
uma política de segurança do Windows. Libere para o seu usuário:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Responda `S` (ou `Y`) e tente ativar de novo.

### Windows (Prompt de Comando antigo, `cmd.exe`)

```cmd
.venv\Scripts\activate.bat
```

### Linux / macOS

```bash
source .venv/bin/activate
```

### Como saber que deu certo

O prompt do terminal passa a começar com `(.venv)`:

```
(.venv) PS C:\Users\voce\projetoPython>
```

> **Você precisa ativar o ambiente toda vez que abrir um terminal novo.**
> Esqueceu? O sintoma é `ModuleNotFoundError: No module named 'django'`.
> É o erro mais comum da disciplina inteira.

## Passo 5 — Instalar as dependências

```bash
pip install -r requirements.txt
```

Baixa o Django e o `python-dotenv`. Leva de dez segundos a um minuto.

Sem internet no momento? Esse passo é o único que precisa dela.

## Passo 6 — Criar o banco e carregar os dados

```bash
python manage.py migrate
python manage.py seed_demo
```

O `migrate` cria o arquivo `escola.sqlite3` com as tabelas — é o
equivalente a rodar o seu `database.py` da Entrega 1.

O `seed_demo` é o seu `seed.py`: cria os usuários e, quando os modelos do
app `academico` estiverem prontos, também alunos, disciplinas e notas.
Ao terminar ele **imprime as credenciais na tela**.

## Passo 7 — Subir o servidor

```bash
python manage.py runserver
```

Abra <http://127.0.0.1:8000> no navegador e entre com **`admin` /
`escola2024`**.

Para parar o servidor: `Ctrl+C` no terminal.

> O servidor recarrega sozinho quando você salva um arquivo `.py`. Não
> precisa reiniciar a cada alteração.

## Resumo — os comandos, de uma vez

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Nas próximas vezes

Instalação é só uma vez. Depois, para voltar a trabalhar, bastam dois
comandos:

```bash
.venv\Scripts\Activate.ps1      # Windows
source .venv/bin/activate        # Linux / macOS

python manage.py runserver
```

## Se der errado

| Mensagem | O que fazer |
|---|---|
| `python: command not found` / `não é reconhecido` | Windows: reinstale marcando "Add python.exe to PATH". Linux: use `python3` |
| `No module named 'venv'` | Linux: `sudo apt install python3-venv` |
| `execução de scripts foi desabilitada` | Rode o `Set-ExecutionPolicy` do passo 4 |
| `No module named 'django'` | Esqueceu de ativar o `.venv` (passo 4) |
| `That port is already in use` | Já há um servidor rodando. Use `python manage.py runserver 8001` |
| `no such table: aluno` | Faltou o `migrate`, ou os TODOs 1-3 ainda não foram feitos |
| A página não muda quando edito o arquivo | Salvou o arquivo? O `Ctrl+S` é seu amigo |
| Quero recomeçar do zero | Apague `escola.sqlite3` e rode `migrate` e `seed_demo` de novo |

Mais detalhes e uma lista completa de erros:
[`material/00-instalacao.md`](material/00-instalacao.md) e
[`material/09-erros-comuns.md`](material/09-erros-comuns.md).

**Travou em algo que não está nesta tabela? Chame o professor.** Não
perca a tarde numa questão de ambiente — o conteúdo da disciplina está do
outro lado dela.

## Instalando o DB Browser for SQLite (recomendado)

Serve para abrir o `escola.sqlite3` e ver as tabelas com os próprios
olhos. É a mesma ferramenta da Entrega 1.

- **Windows / macOS:** baixe em <https://sqlitebrowser.org>
- **Linux:** `sudo apt install sqlitebrowser`

Abra o arquivo `escola.sqlite3` e repare: as tabelas se chamam `aluno`,
`disciplina`, `inscricao` e `usuario` — exatamente os nomes que você usou
em SQL. Isso não é coincidência.

---

## Conferindo o seu progresso

```bash
python verificar.py
```

É o `autoteste.py` desta fase. No começo quase tudo falha — isso é o seu
mapa. Cada falha diz qual TODO fazer e onde.

```bash
python manage.py test academico -v 2   # detalhe de uma falha
python manage.py test contas           # o app de referência (deve dar 21 OK)
```

---

## Mapa do repositório

```
.
├── manage.py                utilitário de linha de comando
├── verificar.py             placar dos TODOs  (não modifique)
│
├── config/                  configuração do projeto
│   ├── settings.py          apps, banco, idioma, autenticação
│   └── urls.py              ponto de entrada de toda URL
│
├── contas/                  ◀ PRONTO — sua referência
│   ├── models.py            Usuario(AbstractUser) + perfil
│   ├── forms.py             login, criação e edição de usuário
│   ├── views.py             as 5 operações de CRUD, comentadas
│   ├── decorators.py        @somente_coordenacao
│   ├── admin.py             registro no painel administrativo
│   ├── tests.py             21 testes — gabarito de como testar
│   └── management/commands/seed_demo.py
│
├── academico/               ◀ VOCÊ IMPLEMENTA
│   ├── models.py            TODO 1-3    Aluno, Disciplina, Inscricao
│   ├── forms.py             TODO 4-6    ModelForms e validações
│   ├── views.py             TODO 7-12   os CRUDs
│   ├── admin.py             TODO 13     bônus
│   ├── urls.py              pronto (é o contrato dos testes)
│   └── tests/test_entrega.py            não modifique
│
├── templates/               HTML — já pronto, não precisa escrever
├── static/                  Bootstrap 5 local (sem CDN)
└── material/                MATERIAL DE ESTUDO — 11 documentos
```

---

## Material de estudo

Comece pelo [índice](material/README.md). Com pressa, leia:

1. [00 — Instalação](material/00-instalacao.md)
2. [01 — De `sqlite3` cru para Django](material/01-de-sqlite-cru-para-django.md)
3. [07 — Tour do app `contas`](material/07-tour-do-app-contas.md)
4. [08 — Roteiro do trabalho](material/08-roteiro-do-trabalho.md)

---

## Por que este projeto existe

Na Entrega 1 você escreveu o CRUD em `sqlite3` cru: `CREATE TABLE`,
`INSERT ... VALUES (?, ?)`, `commit()`, `PRAGMA foreign_keys = ON`.

Aqui você faz a mesma coisa, uma camada acima. Cinco dos sete requisitos
"não negociáveis" daquele enunciado passaram a ser responsabilidade do
framework. Os dois que sobraram — **separação de responsabilidades** e
**nunca montar SQL na mão** — são os que dependem de julgamento.

Isso é o RAD: a ferramenta assume o trabalho mecânico para você gastar
atenção onde ela decide alguma coisa.

O app `contas` está pronto porque ele é a **resposta escrita** de toda
pergunta que você vai ter ao implementar o app `academico`. Abra os dois
lado a lado.

---

## Para o aluno preencher

> Substitua esta seção pelo conteúdo do seu grupo antes de entregar.

### Integrantes

| Nome | Matrícula |
|---|---|
| | |

### Modelo de dados

Anexe o `modelo_dados.png` e explique em poucas linhas as três tabelas e
o relacionamento N:N.

**Responda:** por que `nota1` fica em `inscricao`, e não em `aluno` nem
em `disciplina`?

### Decisões do grupo

- **Exclusão de aluno:** `DELETE` ou soft delete (`ativo = False`)? Por
  quê? O que se ganha e o que se perde num sistema acadêmico?
- **`on_delete` das chaves estrangeiras:** qual opção e por quê?
- **Validações implementadas:** quais e onde (modelo ou formulário)?
- Outras decisões que vocês discutiram.

### Uso de IA

Registre o que foi gerado com auxílio de IA e o que o grupo revisou. Isso
é boa prática profissional, não delação — e o grupo será arguido
oralmente sobre o código de qualquer forma.

| Trecho | Gerado com IA? | Quem revisou | O que foi alterado |
|---|---|---|---|
| | | | |

### Dificuldades

O que travou o grupo e como vocês resolveram.
