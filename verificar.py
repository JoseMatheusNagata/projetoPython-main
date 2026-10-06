#!/usr/bin/env python
"""
=====================================================================
 VERIFICADOR DA ENTREGA -- rode `python verificar.py`
=====================================================================

E o `autoteste.py` da Entrega 1, agora para o projeto Django. Ele roda
a suite academico/tests/ e imprime o placar no formato que voce ja
conhece:

    ------------------------------------------
      34 OK   0 FALHA
    ------------------------------------------

No comeco quase tudo falha. Isso e normal e e o seu mapa: cada falha
diz qual TODO fazer e onde.

Para ver o detalhe completo de uma falha:

    python manage.py test academico -v 2
"""

import os
import sys
import unittest
from pathlib import Path

import django
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent

# Antes de importar QUALQUER coisa do Django, e preciso dizer onde esta
# o settings e chamar django.setup(). E isso que o manage.py faz -- e o
# motivo de um script solto nao conseguir importar modelos.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


LARGURA = 74


def cabecalho():
    print()
    print("=" * LARGURA)
    print("  VERIFICACAO DA ENTREGA -- Sistema de Registro Academico")
    print("=" * LARGURA)


def checar_pre_requisitos():
    """Confere o que precisa estar pronto ANTES de a suite poder rodar.

    Sem isto, um banco inacessivel ou uma migration faltando produziria
    um traceback de 40 linhas em vez de uma instrucao de uma linha.

    Devolve True se pode seguir.
    """
    from django.db import connection
    from django.db.migrations.loader import MigrationLoader

    # --- 1. O banco responde? ---
    #
    # Com SQLite isto quase nunca falha: o banco e um arquivo e o Django
    # o cria sozinho. Quando falha, e permissao de escrita na pasta.
    try:
        connection.ensure_connection()
    except Exception as erro:
        print()
        print("  NAO CONSEGUI ABRIR O BANCO")
        print("  " + "-" * (LARGURA - 4))
        print(f"  {erro}".replace("\n", "\n  ")[:400])
        print()
        print("  O banco e o arquivo escola.sqlite3, na raiz do projeto.")
        print("  Confira se voce tem permissao de escrita nesta pasta e se")
        print("  esta rodando o comando de dentro dela.")
        print()
        return False

    # --- 2. Existe migration do app academico? ---
    loader = MigrationLoader(connection, ignore_no_migrations=True)
    tem_migration = any(app == "academico" for app, _ in loader.disk_migrations)

    if not tem_migration:
        print()
        print("  O APP ACADEMICO AINDA NAO TEM MIGRATION")
        print("  " + "-" * (LARGURA - 4))
        print("  Os modelos em academico/models.py viram tabelas no banco por")
        print("  meio de uma MIGRATION. Enquanto ela nao existir, nenhum teste")
        print("  do CRUD pode rodar -- as tabelas nao existem.")
        print()
        print("  Comece pelos TODOs 1, 2 e 3 (os campos dos tres modelos) e")
        print("  depois rode:")
        print()
        print("      python manage.py makemigrations academico")
        print("      python manage.py migrate")
        print()
        print("  Vale espiar o SQL que foi gerado -- e o CREATE TABLE que voce")
        print("  escreveu na mao na Entrega 1:")
        print()
        print("      python manage.py sqlmigrate academico 0001")
        print()
        return False

    # --- 3. As migrations foram aplicadas? ---
    from django.db.migrations.executor import MigrationExecutor

    executor = MigrationExecutor(connection)
    pendentes = executor.migration_plan(executor.loader.graph.leaf_nodes())

    if pendentes:
        print()
        print("  EXISTEM MIGRATIONS NAO APLICADAS")
        print("  " + "-" * (LARGURA - 4))
        for _, migracao in enumerate(pendentes):
            print(f"    {migracao[0]}")
        print()
        print("  A migration existe mas o banco ainda nao a recebeu. Rode:")
        print()
        print("      python manage.py migrate")
        print()
        return False

    return True


def main():
    cabecalho()

    if not checar_pre_requisitos():
        print("=" * LARGURA)
        print()
        return 1

    import contextlib
    import io

    from django.test.utils import get_runner

    Runner = get_runner(settings)
    # verbosity=0 para o placar nao se perder no meio da saida do Django.
    runner = Runner(verbosity=0, interactive=False, keepdb=False)

    print()
    print("  Criando o banco de testes e rodando a suite...")
    print("  (o banco de testes e temporario -- os seus dados nao sao tocados)")
    print()

    # setup_test_environment() e OBRIGATORIO antes de rodar qualquer teste
    # que use o cliente HTTP: e ele que acrescenta "testserver" ao
    # ALLOWED_HOSTS e instrumenta os templates para expor response.context.
    # Sem esta chamada, TODA requisicao do cliente devolveria 400.
    runner.setup_test_environment()
    banco = runner.setup_databases()
    try:
        suite = runner.build_suite(["academico.tests"])
        total = suite.countTestCases()

        # A saida do unittest vai para o lixo: o relatorio abaixo e mais
        # legivel do que a sequencia de pontos e tracebacks.
        silencio = io.StringIO()
        with contextlib.redirect_stderr(silencio):
            resultado = unittest.TextTestRunner(
                verbosity=0, stream=silencio, failfast=False
            ).run(suite)
    finally:
        runner.teardown_databases(banco)
        runner.teardown_test_environment()

    problemas = resultado.failures + resultado.errors
    ok = total - len(problemas)

    # --- Relatorio ---
    if problemas:
        print("  PENDENCIAS")
        print("  " + "-" * (LARGURA - 4))

        for teste, traco in problemas:
            print(f"\n  [FALHA] {_nome_legivel(teste)}")
            for linha in _mensagem_util(traco):
                print(f"      {linha}")

        print()

    print("-" * LARGURA)
    print(f"  {ok} OK   {len(problemas)} FALHA   (de {total} verificacoes)")
    print("-" * LARGURA)

    if not problemas:
        print()
        print("  Tudo verde. Antes de fechar o .zip:")
        print("    1. Preencha o README.md (modelo de dados, decisoes, uso de IA)")
        print("    2. Exporte o modelo_dados.png")
        print("    3. Confira que .env, .venv/ e __pycache__/ NAO estao no zip")
        print("    4. Rode `python manage.py runserver` e navegue pelo sistema")
        print("       como um usuario faria -- teste passando nao e o mesmo que")
        print("       sistema usavel.")
    else:
        print()
        print("  Para ver o traceback completo de uma falha:")
        print("      python manage.py test academico -v 2")

    print()
    return 1 if problemas else 0


def _nome_legivel(teste):
    """Transforma test_matricula_e_unica em 'matricula e unica'."""
    metodo = teste._testMethodName.removeprefix("test_").replace("_", " ")
    classe = teste.__class__.__name__
    return f"{classe}: {metodo}"


def _mensagem_util(traco):
    """Extrai do traceback apenas a mensagem escrita para o aluno.

    Os testes usam mensagens de varias linhas comecando com indentacao.
    Aqui pegamos o trecho depois do 'AssertionError:' -- e nao as 30
    linhas de pilha interna do unittest, que nao ajudam ninguem.
    """
    linhas = traco.splitlines()

    marcadores = ("AssertionError", "Error:", "Exception:")
    inicio = next(
        (i for i, l in enumerate(linhas) if any(m in l for m in marcadores)),
        None,
    )

    if inicio is None:
        # Erro inesperado: mostra as ultimas linhas, que e onde esta a causa.
        return [l.strip() for l in linhas[-4:] if l.strip()][:4]

    uteis = []
    for linha in linhas[inicio:]:
        texto = linha.replace("AssertionError:", "").strip()
        if texto:
            uteis.append(texto)
        if len(uteis) >= 8:
            uteis.append("...")
            break

    return uteis or ["(sem mensagem -- rode com -v 2 para ver o detalhe)"]


if __name__ == "__main__":
    sys.exit(main())
