"""
Comando de carga de dados de exemplo -- o `seed.py` da Entrega 1, agora
como comando do Django.

Uso:

    python manage.py seed_demo           # cria o que faltar
    python manage.py seed_demo --limpar  # apaga os dados de exemplo antes

--- POR QUE UM "MANAGEMENT COMMAND" E NAO UM SCRIPT SOLTO? -----------

Na Entrega 1 o seed.py era um script comum: voce rodava `python seed.py`
e ele abria a propria conexao com o banco.

Um script solto nao funciona aqui. Ao importar um modelo do Django fora
do `manage.py`, voce recebe:

    ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings
    are not configured.

Porque o Django precisa ser inicializado antes -- ler o settings,
montar o registro de apps, abrir a conexao. O `manage.py` faz isso.
Colocando o codigo em management/commands/, voce herda toda essa
preparacao de graca.

A estrutura de pastas e OBRIGATORIA e o Django a descobre sozinho:

    contas/management/__init__.py
    contas/management/commands/__init__.py
    contas/management/commands/seed_demo.py   -> vira `manage.py seed_demo`

Faltou um dos __init__.py? O comando simplesmente nao aparece, sem
mensagem de erro. E o erro mais comum aqui.
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from contas.models import Usuario

# =====================================================================
#  CREDENCIAIS PADRAO DO SISTEMA
#
#  Senha unica para todo mundo porque isto e ambiente de ESTUDO.
#  Em producao, cada pessoa define a propria senha e nada disso fica
#  escrito em arquivo versionado.
# =====================================================================

SENHA_PADRAO = "escola2024"

# --- O usuario principal ---------------------------------------------
# E superusuario: entra no sistema E no painel /admin/.
# E o login que voce usa no dia a dia enquanto desenvolve.
ADMIN = ("admin", "Administrador", "do Sistema", "admin@escola.edu.br")

# --- Um usuario por perfil, para testar o controle de acesso ---------
# Entre com cada um deles para ver o menu mudar: so a coordenacao
# enxerga a gestao de usuarios.
USUARIOS = [
    ("coordenacao", "Marta", "Ribeiro", "marta.ribeiro@escola.edu.br", Usuario.Perfil.COORDENACAO),
    ("professor", "Carlos", "Antunes", "carlos.antunes@escola.edu.br", Usuario.Perfil.PROFESSOR),
    ("secretaria", "Helena", "Duarte", "helena.duarte@escola.edu.br", Usuario.Perfil.SECRETARIA),
]

ALUNOS = [
    ("2024001", "Ana Beatriz Souza", "ana.souza@aluno.edu.br", date(2005, 3, 14)),
    ("2024002", "Bruno Carvalho Lima", "bruno.lima@aluno.edu.br", date(2004, 7, 2)),
    ("2024003", "Camila Ferreira Rocha", "camila.rocha@aluno.edu.br", date(2005, 11, 23)),
    ("2024004", "Diego Martins Alves", "diego.alves@aluno.edu.br", date(2003, 1, 30)),
    ("2024005", "Eduarda Nunes Pinto", "eduarda.pinto@aluno.edu.br", date(2005, 6, 9)),
    ("2024006", "Felipe Ramos Teixeira", "felipe.teixeira@aluno.edu.br", date(2004, 9, 17)),
    ("2024007", "Gabriela Moreira Dias", "gabriela.dias@aluno.edu.br", date(2005, 2, 5)),
    ("2024008", "Henrique Barbosa Cruz", "henrique.cruz@aluno.edu.br", date(2004, 12, 28)),
]

DISCIPLINAS = [
    ("ARA0095", "Desenvolvimento Rapido de Aplicacoes em Python", 80, 3),
    ("ARA0042", "Estrutura de Dados", 80, 2),
    ("ARA0017", "Banco de Dados", 60, 2),
    ("ARA0111", "Engenharia de Software", 60, 4),
    ("ARA0208", "Interface Humano-Computador", 40, 4),
]

# (matricula, codigo, nota1, nota2) -- None = nota ainda nao lancada.
# Repare no 0.0 da ultima linha: e uma nota VALIDA, e um bom teste para
# quem confundiu "sem nota" com "nota zero" no TODO 3c.
INSCRICOES = [
    ("2024001", "ARA0095", "9.0", "8.5"),
    ("2024001", "ARA0017", "7.5", "8.0"),
    ("2024002", "ARA0095", "6.0", "5.5"),
    ("2024002", "ARA0042", "8.0", None),
    ("2024003", "ARA0095", "10.0", "9.5"),
    ("2024003", "ARA0111", None, None),
    ("2024004", "ARA0017", "4.5", "6.0"),
    ("2024005", "ARA0095", "7.0", "7.5"),
    ("2024005", "ARA0208", "8.5", "9.0"),
    ("2024006", "ARA0042", "5.0", "6.5"),
    ("2024007", "ARA0095", "8.0", "8.0"),
    ("2024008", "ARA0111", "0.0", "3.0"),
]


class Command(BaseCommand):
    help = "Carrega usuarios, alunos, disciplinas e notas de exemplo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga os dados de exemplo antes de recriar.",
        )

    # @transaction.atomic embrulha o metodo inteiro em UMA transacao:
    # se algo falhar no meio, NADA e gravado. Sem isso, um erro na
    # ultima inscricao deixaria o banco meio populado.
    @transaction.atomic
    def handle(self, *args, **opcoes):
        if opcoes["limpar"]:
            self._limpar()

        self._criar_usuarios()
        self._criar_dados_academicos()

        self._mostrar_credenciais()

    def _mostrar_credenciais(self):
        """Imprime as credenciais numa caixa dificil de nao ver.

        O aluno acabou de rodar tres comandos e precisa saber como
        entrar. Esconder isso numa linha de log seria crueldade.
        """
        linha = "=" * 66

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(linha))
        self.stdout.write(self.style.SUCCESS("  CARGA CONCLUIDA -- ENTRE COM:"))
        self.stdout.write(self.style.SUCCESS(linha))
        self.stdout.write("")
        self.stdout.write(f"      usuario:  {self.style.SUCCESS(ADMIN[0])}")
        self.stdout.write(f"      senha:    {self.style.SUCCESS(SENHA_PADRAO)}")
        self.stdout.write("")
        self.stdout.write("      Acesso total: o sistema e tambem o painel /admin/.")
        self.stdout.write("")
        self.stdout.write("  " + "-" * 64)
        self.stdout.write("  Outros usuarios, para testar o controle de acesso")
        self.stdout.write(f"  (todos com a mesma senha '{SENHA_PADRAO}'):")
        self.stdout.write("")
        for username, nome, _sobrenome, _email, perfil in USUARIOS:
            rotulo = Usuario.Perfil(perfil).label
            self.stdout.write(f"      {username:<14} {rotulo}")
        self.stdout.write("")
        self.stdout.write("  Abra:  http://127.0.0.1:8000")
        self.stdout.write(self.style.SUCCESS(linha))
        self.stdout.write("")

    # -----------------------------------------------------------------

    def _limpar(self):
        Usuario.objects.filter(
            username__in=[ADMIN[0]] + [u[0] for u in USUARIOS]
        ).delete()
        self.stdout.write(self.style.WARNING("Usuarios de exemplo removidos."))

        modelos = self._modelos_academicos()
        if modelos:
            Aluno, Disciplina, Inscricao = modelos
            # A ordem importa: primeiro as inscricoes, que APONTAM para
            # aluno e disciplina. Tentar apagar um aluno que ainda tem
            # inscricao levanta ProtectedError -- o banco protegendo o
            # historico (on_delete=PROTECT no TODO 3).
            Inscricao.objects.all().delete()
            Aluno.objects.all().delete()
            Disciplina.objects.all().delete()
            self.stdout.write(self.style.WARNING("Dados academicos removidos."))

    def _criar_admin(self):
        """Cria o superusuario padrao.

        create_superuser e igual a create_user, mais is_staff=True e
        is_superuser=True -- as duas flags que liberam o painel /admin/.

        Isto poupa o aluno de rodar `manage.py createsuperuser` e
        responder tres perguntas antes de conseguir olhar o banco.
        """
        username, nome, sobrenome, email = ADMIN

        if Usuario.objects.filter(username=username).exists():
            self.stdout.write(f"  usuario '{username}' ja existe, mantido")
            return

        Usuario.objects.create_superuser(
            username=username,
            password=SENHA_PADRAO,
            first_name=nome,
            last_name=sobrenome,
            email=email,
            perfil=Usuario.Perfil.COORDENACAO,
        )
        self.stdout.write(
            self.style.SUCCESS(f"  usuario '{username}' criado (superusuario)")
        )

    def _criar_usuarios(self):
        self._criar_admin()

        for username, nome, sobrenome, email, perfil in USUARIOS:
            if Usuario.objects.filter(username=username).exists():
                self.stdout.write(f"  usuario '{username}' ja existe, mantido")
                continue

            # create_user (e nao objects.create) porque ele aplica o
            # HASH na senha. Com objects.create(password="x") a senha
            # iria em texto puro para o banco e o login nunca
            # funcionaria -- o Django compararia hash com texto.
            Usuario.objects.create_user(
                username=username,
                password=SENHA_PADRAO,
                first_name=nome,
                last_name=sobrenome,
                email=email,
                perfil=perfil,
            )
            self.stdout.write(self.style.SUCCESS(f"  usuario '{username}' criado ({perfil})"))

    def _criar_dados_academicos(self):
        modelos = self._modelos_academicos()
        if not modelos:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "Os modelos do app academico ainda estao incompletos (TODO 1 a 3).\n"
                    "  Carreguei somente os usuarios. Rode este comando de novo\n"
                    "  depois de declarar os campos e aplicar a migration."
                )
            )
            return

        Aluno, Disciplina, Inscricao = modelos

        for matricula, nome, email, nascimento in ALUNOS:
            # get_or_create devolve (objeto, foi_criado) e evita o erro
            # de matricula duplicada ao rodar o seed duas vezes.
            _, criado = Aluno.objects.get_or_create(
                matricula=matricula,
                defaults={"nome": nome, "email": email, "data_nascimento": nascimento},
            )
            if criado:
                self.stdout.write(f"  aluno {matricula} - {nome}")

        for codigo, nome, carga, periodo in DISCIPLINAS:
            _, criado = Disciplina.objects.get_or_create(
                codigo=codigo,
                defaults={"nome": nome, "carga_horaria": carga, "periodo": periodo},
            )
            if criado:
                self.stdout.write(f"  disciplina {codigo} - {nome}")

        for matricula, codigo, nota1, nota2 in INSCRICOES:
            Inscricao.objects.get_or_create(
                aluno=Aluno.objects.get(matricula=matricula),
                disciplina=Disciplina.objects.get(codigo=codigo),
                defaults={"nota1": nota1, "nota2": nota2},
            )

        self.stdout.write(f"  {Inscricao.objects.count()} inscricoes")

    def _modelos_academicos(self):
        """Devolve (Aluno, Disciplina, Inscricao) se os modelos estiverem
        prontos; None caso contrario.

        Existe para que o seed funcione TAMBEM no esqueleto: sem isto,
        o aluno nao conseguiria criar os usuarios nem fazer login antes
        de terminar o TODO 3 -- e ficaria sem como testar nada.
        """
        from academico.models import Aluno, Disciplina, Inscricao

        obrigatorios = {
            Aluno: {"matricula", "nome"},
            Disciplina: {"codigo", "nome", "carga_horaria"},
            Inscricao: {"aluno", "disciplina"},
        }

        for modelo, campos in obrigatorios.items():
            existentes = {f.name for f in modelo._meta.get_fields()}
            if not campos.issubset(existentes):
                return None

        return Aluno, Disciplina, Inscricao
