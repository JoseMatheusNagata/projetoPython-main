"""
Configuracao do projeto -- ARA0095 Sistema de Registro Academico.

Este arquivo e o "painel de controle" do Django. Ele e lido uma vez,
quando o servidor sobe, e tudo que esta aqui vira configuracao global.

Leitura recomendada: material/00-instalacao.md e material/02-models-e-migrations.md
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# ---------------------------------------------------------------------
# BASE_DIR e a pasta que contem o manage.py.
#
# __file__ = .../config/settings.py
#   .resolve()  -> caminho absoluto
#   .parent     -> .../config/
#   .parent     -> .../         (a raiz do projeto)
#
# Usamos BASE_DIR para montar todos os outros caminhos. Assim o projeto
# funciona em qualquer pasta, em qualquer maquina -- nada de caminho
# fixo tipo "C:\Users\joao\projeto".
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Le o arquivo .env (se existir) e injeta as variaveis no os.environ.
load_dotenv(BASE_DIR / ".env")


# =====================================================================
# SEGURANCA
# =====================================================================

# Chave usada para assinar cookies de sessao e tokens CSRF.
# Vem do .env justamente para nao ficar escrita no codigo versionado.
SECRET_KEY = os.getenv("SECRET_KEY", "chave-insegura-apenas-para-desenvolvimento")

# os.getenv devolve SEMPRE uma string. A string "False" e um valor
# verdadeiro em Python (toda string nao vazia e), entao comparar com
# "true" e obrigatorio -- escrever DEBUG = os.getenv("DEBUG") deixaria o
# DEBUG ligado para sempre, inclusive em producao.
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]


# =====================================================================
# APLICACOES
# =====================================================================

INSTALLED_APPS = [
    # --- apps que vem com o Django ---
    "django.contrib.admin",         # o painel administrativo
    "django.contrib.auth",          # usuarios, grupos, permissoes, senhas
    "django.contrib.contenttypes",  # base do sistema de permissoes
    "django.contrib.sessions",      # mantem o usuario logado entre requisicoes
    "django.contrib.messages",      # as mensagens de sucesso/erro das telas
    "django.contrib.staticfiles",   # serve CSS, JS e imagens
    # --- apps deste projeto ---
    "contas",       # login e gestao de usuarios   (PRONTO, serve de exemplo)
    "academico",    # alunos, disciplinas e notas  (VOCE implementa)
]


# =====================================================================
# MIDDLEWARE
#
# Uma fila de "porteiros" por onde TODA requisicao passa na ida e toda
# resposta passa na volta. A ordem importa:
#   - SessionMiddleware precisa rodar antes do AuthenticationMiddleware,
#     porque a autenticacao le a sessao para descobrir quem e o usuario;
#   - e o AuthenticationMiddleware e quem coloca o `request.user` que
#     voce usa nas views e nos templates.
# =====================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"


# =====================================================================
# TEMPLATES (os arquivos HTML)
# =====================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # DIRS: pastas de template do PROJETO (as compartilhadas, como o
        # base.html). O Django procura aqui primeiro.
        "DIRS": [BASE_DIR / "templates"],
        # APP_DIRS: alem das DIRS, procure tambem em <app>/templates/.
        "APP_DIRS": True,
        "OPTIONS": {
            # Context processors injetam variaveis em TODOS os templates,
            # sem que a view precise passa-las uma por uma.
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",      # -> {{ user }}
                "django.contrib.messages.context_processors.messages",  # -> {{ messages }}
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# =====================================================================
# BANCO DE DADOS -- SQLite
#
# Compare com a Entrega 1:
#
#     conexao = sqlite3.connect("escola.db")
#     cursor = conexao.cursor()
#     ...
#     conexao.commit()
#     conexao.close()
#
# Era isso a conexao inteira, e voce a abria e fechava em toda funcao.
# Aqui voce apenas DESCREVE como conectar. Quem abre a conexao, a
# reaproveita entre as requisicoes e a fecha no final e o Django. Voce
# nunca mais chama connect(), commit() ou close() na mao.
#
# E o MESMO SQLite da Entrega 1 -- inclusive da para abrir o arquivo
# escola.sqlite3 no DB Browser for SQLite e ver as tabelas nascidas
# das suas classes Python.
# =====================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # O banco e um ARQUIVO. Ele nao vai para o Git nem para o .zip
        # da entrega (veja o .gitignore) porque e GERADO pelo codigo,
        # com `python manage.py migrate`. Mesma regra da Entrega 1: se o
        # projeto nao consegue recriar o banco do zero, ele esta errado.
        "NAME": BASE_DIR / "escola.sqlite3",
        # ATOMIC_REQUESTS = True embrulha cada requisicao HTTP em UMA
        # transacao: se a view terminar bem, o Django da COMMIT; se
        # estourar uma excecao, da ROLLBACK e NADA e gravado.
        #
        # E o substituto do `conexao.commit()` que voce escrevia na mao
        # depois de todo INSERT/UPDATE/DELETE -- com a vantagem de que
        # agora e impossivel esquecer.
        "ATOMIC_REQUESTS": True,
        "OPTIONS": {
            # Espera ate 20s se o banco estiver travado por outra
            # escrita, em vez de falhar na hora. SQLite aceita muitas
            # leituras simultaneas, mas uma escrita por vez.
            "timeout": 20,
        },
    }
}

# SOBRE O "PRAGMA foreign_keys = ON" DA ENTREGA 1
#
# Voce precisava ligar isso em TODA conexao, senao o SQLite aceitava
# calado uma inscricao apontando para um aluno inexistente.
#
# O Django ja liga sozinho, em toda conexao que abre. Por isso o
# on_delete=PROTECT do TODO 3 funciona de verdade aqui: a chave
# estrangeira e conferida pelo banco, nao so pelo Python.

# =====================================================================
# USUARIO
#
# Por padrao o Django usa o modelo django.contrib.auth.models.User.
# Aqui trocamos pelo nosso Usuario, que tem o campo `perfil`.
#
# ATENCAO: isto precisa ser definido ANTES da primeira migration do
# projeto. Trocar o modelo de usuario com o banco ja criado e um dos
# procedimentos mais dolorosos do Django -- por isso ja nasce assim.
# =====================================================================

AUTH_USER_MODEL = "contas.Usuario"

# Para onde o @login_required manda quem nao esta logado.
LOGIN_URL = "contas:login"
# Para onde vai depois de logar com sucesso.
LOGIN_REDIRECT_URL = "contas:usuario_lista"
# Para onde vai depois de sair.
LOGOUT_REDIRECT_URL = "contas:login"

# Regras que a senha precisa cumprir no cadastro.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =====================================================================
# IDIOMA E FUSO HORARIO
# =====================================================================

LANGUAGE_CODE = "pt-br"

# Guardamos tudo em UTC no banco e o Django converte para o fuso abaixo
# na hora de exibir. Isso evita o pesadelo do horario de verao.
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# =====================================================================
# ARQUIVOS ESTATICOS (CSS, JS, imagens)
# =====================================================================

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


# =====================================================================
# OUTROS
# =====================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Faz as mensagens do django.contrib.messages usarem as classes CSS do
# Bootstrap: messages.error(...) vira <div class="alert alert-danger">.
from django.contrib.messages import constants as messages  # noqa: E402

MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}
