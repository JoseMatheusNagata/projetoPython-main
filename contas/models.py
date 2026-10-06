"""
Modelo de usuario do sistema.

Este arquivo e a resposta para: "como eu declaro uma tabela no Django?".
Compare com o que voce escreveu na Entrega 1:

    CREATE TABLE aluno (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula TEXT NOT NULL UNIQUE,
        ...
    )

Aqui voce escreve uma CLASSE PYTHON e o Django gera esse SQL para voce.
Quer ver o SQL gerado? Rode:

    python manage.py sqlmigrate contas 0001
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario do sistema academico.

    Herda de AbstractUser, entao ja vem com tudo que o Django precisa
    para autenticar: username, password (guardada com hash, NUNCA em
    texto puro), first_name, last_name, email, is_active, is_staff,
    is_superuser, last_login e date_joined.

    Nos so ACRESCENTAMOS o campo `perfil`.

    Por que nao usar o User padrao do Django?
    Porque trocar o modelo de usuario depois que o banco ja existe e um
    dos procedimentos mais dolorosos do Django. Comecar com um modelo
    proprio custa 5 linhas hoje e evita uma reescrita amanha -- e
    exatamente o mesmo raciocinio do enunciado da Entrega 1: "se a base
    ficar torta, voce vai reescrever tudo tres vezes".
    """

    class Perfil(models.TextChoices):
        """As opcoes validas do campo `perfil`.

        TextChoices e um "enum" do Django. Cada linha tem:
            NOME_NO_CODIGO = "valor_no_banco", "Texto para o usuario ler"

        A vantagem sobre escrever a string solta: o banco ganha uma
        restricao CHECK, o formulario ganha um <select> pronto e no
        codigo voce escreve Usuario.Perfil.COORDENACAO em vez de
        "COORD" -- se digitar errado, o Python acusa na hora.
        """

        COORDENACAO = "COORD", "Coordenacao"
        PROFESSOR = "PROF", "Professor"
        SECRETARIA = "SEC", "Secretaria"

    perfil = models.CharField(
        "perfil de acesso",
        max_length=5,
        choices=Perfil.choices,
        default=Perfil.SECRETARIA,
        help_text="Define o que este usuario pode fazer no sistema.",
    )

    # O email vem do AbstractUser sem UNIQUE e podendo ficar vazio.
    # Redeclarar o campo sobrescreve aquela definicao -- e o mesmo
    # NOT NULL UNIQUE que voce colocou na coluna `matricula`.
    email = models.EmailField("e-mail", unique=True)

    class Meta:
        # Nome da tabela no banco. Sem isto o Django criaria
        # "contas_usuario" (app + modelo). Fixamos para que voce
        # reconheca a tabela ao abrir o escola.sqlite3 no DB Browser.
        db_table = "usuario"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        # Ordem padrao de TODA consulta a este modelo -- equivale a
        # colocar ORDER BY first_name em todo SELECT.
        ordering = ["first_name", "username"]

    def __str__(self):
        """Como este objeto aparece quando vira texto.

        Usado no admin, nos <select> dos formularios e sempre que o
        template escreve {{ usuario }}. Sem isto voce veria
        "Usuario object (3)", que nao ajuda ninguem.
        """
        return f"{self.get_full_name() or self.username}"

    # -----------------------------------------------------------------
    # Metodos de apoio.
    #
    # Regra de negocio mora no MODELO, nao na view. Assim a resposta
    # para "esta pessoa e da coordenacao?" existe em UM lugar so -- e
    # funciona igual na view, no template e no teste.
    # -----------------------------------------------------------------

    @property
    def eh_coordenacao(self):
        """True se este usuario pode gerenciar outros usuarios.

        Superusuario tambem passa: quem instala o sistema precisa
        conseguir entrar na gestao ANTES de existir qualquer usuario de
        coordenacao. E o caso do 'admin' criado pelo seed_demo.
        """
        return self.is_superuser or self.perfil == self.Perfil.COORDENACAO
