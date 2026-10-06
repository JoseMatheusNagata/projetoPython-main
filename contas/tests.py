"""
Testes do app de contas.

DUAS razoes para este arquivo existir:

  1. Provar que o login e a gestao de usuarios funcionam de verdade,
     sem ninguem precisar clicar na tela para conferir.

  2. Servir de GABARITO de como se escreve teste em Django -- voce vai
     ler estes testes para entender o que o academico/tests/ espera de
     voce.

--- COMO RODAR -------------------------------------------------------

    python manage.py test contas -v 2

--- O QUE O DJANGO FAZ POR VOCE --------------------------------------

Antes de rodar, o Django cria um banco NOVO chamado test_escola_db,
aplica todas as migrations nele, roda os testes e APAGA o banco no
final. Os seus dados de verdade nunca sao tocados.

Com SQLite esse banco de teste fica so na memoria -- some sozinho e
nem chega a virar arquivo no disco.

Alem disso, cada teste roda dentro de uma transacao que sofre ROLLBACK
no fim -- entao os testes nao interferem uns nos outros e a ordem em
que rodam nao importa.
"""

from django.test import TestCase
from django.urls import reverse

from .models import Usuario

SENHA = "senha-de-teste-123"


class UsuarioModeloTest(TestCase):
    """Testes do modelo, sem passar pela interface web."""

    def test_senha_e_guardada_com_hash(self):
        """A senha NUNCA pode ficar em texto puro no banco."""
        usuario = Usuario.objects.create_user(
            username="joao", email="joao@escola.edu.br", password=SENHA
        )

        # O que esta gravado nao e a senha.
        self.assertNotEqual(usuario.password, SENHA)
        # Mas o Django consegue verificar se confere.
        self.assertTrue(usuario.check_password(SENHA))

    def test_perfil_padrao_e_secretaria(self):
        usuario = Usuario.objects.create_user(
            username="novo", email="novo@escola.edu.br", password=SENHA
        )
        self.assertEqual(usuario.perfil, Usuario.Perfil.SECRETARIA)

    def test_eh_coordenacao(self):
        """A regra de permissao mora no modelo, e e testada aqui."""
        coord = Usuario.objects.create_user(
            username="coord", email="c@escola.edu.br", password=SENHA,
            perfil=Usuario.Perfil.COORDENACAO,
        )
        prof = Usuario.objects.create_user(
            username="prof", email="p@escola.edu.br", password=SENHA,
            perfil=Usuario.Perfil.PROFESSOR,
        )

        self.assertTrue(coord.eh_coordenacao)
        self.assertFalse(prof.eh_coordenacao)

    def test_superusuario_tambem_eh_coordenacao(self):
        """Quem cria o sistema precisa conseguir entrar na gestao."""
        admin = Usuario.objects.create_superuser(
            username="admin", email="admin@escola.edu.br", password=SENHA
        )
        self.assertTrue(admin.eh_coordenacao)

    def test_nome_da_tabela(self):
        """O db_table do Meta e o que faz a tabela se chamar `usuario`."""
        self.assertEqual(Usuario._meta.db_table, "usuario")


class LoginTest(TestCase):
    """Testes da tela de login."""

    def setUp(self):
        """Roda ANTES de cada teste desta classe.

        Como cada teste tem a sua propria transacao (revertida no fim),
        este usuario e recriado do zero a cada vez.
        """
        self.usuario = Usuario.objects.create_user(
            username="maria",
            email="maria@escola.edu.br",
            password=SENHA,
            first_name="Maria",
            perfil=Usuario.Perfil.COORDENACAO,
        )
        self.url = reverse("contas:login")

    def test_tela_de_login_abre(self):
        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "contas/login.html")

    def test_login_com_credenciais_validas(self):
        resposta = self.client.post(
            self.url, {"username": "maria", "password": SENHA}, follow=True
        )

        self.assertEqual(resposta.status_code, 200)
        # wsgi_request.user e o usuario da sessao resultante.
        self.assertTrue(resposta.wsgi_request.user.is_authenticated)

    def test_login_com_senha_errada(self):
        resposta = self.client.post(
            self.url, {"username": "maria", "password": "errada"}
        )

        # 200 e nao 302: continua na tela de login, com o erro.
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(resposta.wsgi_request.user.is_authenticated)

    def test_usuario_desativado_nao_entra(self):
        """O soft delete precisa realmente bloquear o acesso.

        Se este teste falhar, "desativar" nao desativa nada -- e a
        tela de exclusao esta mentindo para o usuario.
        """
        self.usuario.is_active = False
        self.usuario.save(update_fields=["is_active"])

        resposta = self.client.post(
            self.url, {"username": "maria", "password": SENHA}
        )

        self.assertFalse(resposta.wsgi_request.user.is_authenticated)


class PermissaoTest(TestCase):
    """Testes do decorator @somente_coordenacao."""

    def setUp(self):
        self.coord = Usuario.objects.create_user(
            username="coord", email="coord@escola.edu.br", password=SENHA,
            perfil=Usuario.Perfil.COORDENACAO,
        )
        self.prof = Usuario.objects.create_user(
            username="prof", email="prof@escola.edu.br", password=SENHA,
            perfil=Usuario.Perfil.PROFESSOR,
        )
        self.url = reverse("contas:usuario_lista")

    def test_visitante_e_mandado_para_o_login(self):
        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("contas:login"), resposta.url)

    def test_professor_recebe_403(self):
        """Logado mas sem permissao: 403, e NAO redirect para o login.

        Mandar para o login quem ja esta logado produz aquele loop de
        tela de login que nao adianta preencher.
        """
        self.client.force_login(self.prof)

        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 403)

    def test_coordenacao_acessa(self):
        self.client.force_login(self.coord)

        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "contas/usuario_lista.html")


class CrudUsuarioTest(TestCase):
    """Testes das cinco operacoes de CRUD."""

    def setUp(self):
        self.coord = Usuario.objects.create_user(
            username="coord", email="coord@escola.edu.br", password=SENHA,
            first_name="Marta", perfil=Usuario.Perfil.COORDENACAO,
        )
        # force_login pula a tela de login: o teste aqui e do CRUD,
        # nao da autenticacao (que a LoginTest ja cobriu).
        self.client.force_login(self.coord)

    def test_criar_usuario(self):
        resposta = self.client.post(
            reverse("contas:usuario_novo"),
            {
                "username": "novo",
                "first_name": "Novo",
                "last_name": "Usuario",
                "email": "novo@escola.edu.br",
                "perfil": Usuario.Perfil.PROFESSOR,
                "password1": "UmaSenhaBoa!2024",
                "password2": "UmaSenhaBoa!2024",
            },
        )

        self.assertRedirects(resposta, reverse("contas:usuario_lista"))
        self.assertTrue(Usuario.objects.filter(username="novo").exists())

    def test_email_duplicado_e_recusado_com_mensagem(self):
        """O item 6 da rubrica da Entrega 1, agora na web.

        Duplicidade deve virar mensagem no formulario -- nunca um
        traceback na cara do usuario.
        """
        resposta = self.client.post(
            reverse("contas:usuario_novo"),
            {
                "username": "outro",
                "first_name": "Outro",
                "last_name": "Usuario",
                "email": "coord@escola.edu.br",  # ja existe
                "perfil": Usuario.Perfil.SECRETARIA,
                "password1": "UmaSenhaBoa!2024",
                "password2": "UmaSenhaBoa!2024",
            },
        )

        self.assertEqual(resposta.status_code, 200)  # nao redirecionou
        self.assertFormError(
            resposta.context["form"], "email", "Ja existe um usuario com este e-mail."
        )
        self.assertFalse(Usuario.objects.filter(username="outro").exists())

    def test_editar_usuario(self):
        alvo = Usuario.objects.create_user(
            username="alvo", email="alvo@escola.edu.br", password=SENHA,
            first_name="Nome Antigo",
        )

        resposta = self.client.post(
            reverse("contas:usuario_editar", args=[alvo.pk]),
            {
                "username": "alvo",
                "first_name": "Nome Novo",
                "last_name": "Sobrenome",
                "email": "alvo@escola.edu.br",  # o proprio e-mail
                "perfil": Usuario.Perfil.PROFESSOR,
                "is_active": "on",
            },
        )

        self.assertRedirects(resposta, reverse("contas:usuario_lista"))
        alvo.refresh_from_db()  # recarrega do banco
        self.assertEqual(alvo.first_name, "Nome Novo")

    def test_editar_mantendo_o_proprio_email_nao_acusa_duplicidade(self):
        """O caso que o .exclude(pk=...) do clean_email resolve.

        Sem ele, editar qualquer usuario acusaria e-mail duplicado --
        porque o proprio registro seria encontrado na busca.
        """
        resposta = self.client.post(
            reverse("contas:usuario_editar", args=[self.coord.pk]),
            {
                "username": "coord",
                "first_name": "Marta Alterada",
                "last_name": "Ribeiro",
                "email": "coord@escola.edu.br",
                "perfil": Usuario.Perfil.COORDENACAO,
                "is_active": "on",
            },
        )

        self.assertRedirects(resposta, reverse("contas:usuario_lista"))

    def test_desativar_usuario_nao_apaga_do_banco(self):
        """Soft delete: o registro continua la, apenas inativo."""
        alvo = Usuario.objects.create_user(
            username="alvo", email="alvo@escola.edu.br", password=SENHA
        )

        resposta = self.client.post(reverse("contas:usuario_excluir", args=[alvo.pk]))

        self.assertRedirects(resposta, reverse("contas:usuario_lista"))
        alvo.refresh_from_db()
        self.assertFalse(alvo.is_active)
        self.assertTrue(Usuario.objects.filter(pk=alvo.pk).exists())

    def test_get_na_exclusao_nao_desativa(self):
        """GET precisa ser seguro: apenas mostra a confirmacao.

        Se este teste falhar, um robo de busca visitando a URL
        desativaria usuarios do sistema.
        """
        alvo = Usuario.objects.create_user(
            username="alvo", email="alvo@escola.edu.br", password=SENHA
        )

        resposta = self.client.get(reverse("contas:usuario_excluir", args=[alvo.pk]))

        self.assertEqual(resposta.status_code, 200)
        alvo.refresh_from_db()
        self.assertTrue(alvo.is_active)  # continua ativo

    def test_nao_pode_desativar_a_propria_conta(self):
        """Sem esta trava, a coordenacao se tranca fora do sistema."""
        resposta = self.client.post(
            reverse("contas:usuario_excluir", args=[self.coord.pk])
        )

        self.assertRedirects(resposta, reverse("contas:usuario_lista"))
        self.coord.refresh_from_db()
        self.assertTrue(self.coord.is_active)

    def test_reativar_usuario(self):
        alvo = Usuario.objects.create_user(
            username="alvo", email="alvo@escola.edu.br", password=SENHA, is_active=False
        )

        self.client.post(reverse("contas:usuario_reativar", args=[alvo.pk]))

        alvo.refresh_from_db()
        self.assertTrue(alvo.is_active)

    def test_busca_filtra_a_listagem(self):
        Usuario.objects.create_user(
            username="fulano", email="fulano@escola.edu.br", password=SENHA,
            first_name="Fulano",
        )

        resposta = self.client.get(reverse("contas:usuario_lista"), {"busca": "Fulano"})

        nomes = [u.username for u in resposta.context["usuarios"]]
        self.assertIn("fulano", nomes)
        self.assertNotIn("coord", nomes)
