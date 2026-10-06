# 00 — Instalação e primeiro run

Meta deste módulo: sair do zero e ver o sistema rodando no navegador, com
dados dentro. Deve levar menos de dez minutos.

## Antes de começar

Você precisa de Python 3.10 ou mais novo. Confira:

```bash
python --version
```

Se o comando não existir, tente `python3 --version`. Em todos os exemplos
a seguir, use o que funcionou na sua máquina.

**Não precisa instalar banco de dados.** O projeto usa SQLite — o mesmo
da Entrega 1 — que já vem embutido no Python. O banco é um arquivo.

## Os seis comandos

```bash
# 1. Crie o ambiente virtual (uma pasta com um Python só deste projeto)
python -m venv .venv

# 2. Ative o ambiente
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows (PowerShell)

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie as tabelas no banco
python manage.py migrate

# 5. Carregue os dados de exemplo
python manage.py seed_demo

# 6. Suba o servidor
python manage.py runserver
```

Abra <http://127.0.0.1:8000> e entre com:

| | |
|---|---|
| **Usuário** | `admin` |
| **Senha** | `escola2024` |

O `seed_demo` imprime essas credenciais na tela ao terminar — se
esquecer, é só rodar de novo.

Há mais três contas, com a mesma senha, para você ver o controle de
acesso por perfil funcionando:

| Usuário | Perfil | Enxerga a gestão de usuários? |
|---|---|---|
| `admin` | Coordenação (superusuário) | sim, e também o `/admin/` |
| `coordenacao` | Coordenação | sim |
| `professor` | Professor | não — recebe 403 |
| `secretaria` | Secretaria | não — recebe 403 |

Entre com `professor` e repare que o item "Usuários" some do menu. Depois
digite `/contas/usuarios/` na barra de endereço: você recebe **403**, e
não a tela. Esconder o link é cortesia; a proteção está na view.

Para parar o servidor: `Ctrl+C`.

> Precisa de instruções passo a passo para Windows ou Linux, com as
> telas do instalador e os erros de PowerShell? Estão no
> [README.md](../README.md) do projeto, na seção **Manual de
> instalação**.

### Por que o ambiente virtual?

Sem ele, o `pip install` joga o Django na instalação global do Python.
Aí o próximo projeto que precisar de outra versão do Django quebra este.
O `.venv` é uma caixa isolada por projeto — e por isso ele **não vai** no
`.zip` da entrega: cada pessoa cria o seu.

Você sabe que está ativo quando o prompt do terminal mostra `(.venv)`.
Esqueceu de ativar? O sintoma é `ModuleNotFoundError: No module named
'django'`.

## O que cada comando fez

**`migrate`** leu os arquivos de migration e criou as tabelas no arquivo
`escola.sqlite3`. É o equivalente a rodar o seu `database.py` da Entrega
1 — a diferença é que você não escreveu o `CREATE TABLE`, ele foi gerado
a partir das classes em `models.py`.

**`seed_demo`** é o seu `seed.py`, agora como comando do Django. Ele
cria os três usuários e, quando os modelos do app `academico` estiverem
prontos, também alunos, disciplinas e notas.

## Confira o banco com os próprios olhos

Instale o **DB Browser for SQLite** (<https://sqlitebrowser.org>) e abra
o arquivo `escola.sqlite3`. É a mesma ferramenta da Entrega 1, e vale o
mesmo conselho: vai poupar horas de depuração.

Repare que as tabelas se chamam `aluno`, `disciplina`, `inscricao` e
`usuario` — exatamente os nomes que você usou em SQL. Isso não é
coincidência, é o `db_table` declarado no `Meta` de cada modelo.

O Django também acompanha um inspetor próprio, em
<http://127.0.0.1:8000/admin/>. Entre com o mesmo `admin` /
`escola2024` — o `seed_demo` já o criou como superusuário.

(Se um dia precisar criar outro, o comando é
`python manage.py createsuperuser`.)

> Pense no `/admin/` como o DB Browser: é ferramenta de desenvolvedor
> para olhar os dados. **Ele não é a entrega.** As telas que você
> constrói é que são.

## Deu erro?

| Mensagem | Causa quase sempre |
|---|---|
| `command not found: python` | Use `python3` |
| `No module named 'django'` | Esqueceu de ativar o `.venv` |
| `No module named 'venv'` | Falta o pacote `python3-venv` (Linux: `sudo apt install python3-venv`) |
| `That port is already in use` | Já tem um servidor rodando. Use `python manage.py runserver 8001` |
| `no such table: aluno` | Faltou `migrate`, ou os TODOs 1-3 ainda não foram feitos |
| A página não muda quando edito o HTML | Salvou o arquivo? O servidor recarrega sozinho, mas só se você salvar |

Travou em algo que não está nesta tabela? Chame o professor. Não perca a
tarde numa questão de ambiente — o conteúdo da disciplina está do outro
lado dela.
