"""
=====================================================================
 VERIFICACAO AUTOMATICA DA ENTREGA -- NAO MODIFIQUE ESTE ARQUIVO
=====================================================================

Este e o `autoteste.py` desta fase do trabalho. Ele confere, um por um,
se os TODOs do app academico foram implementados corretamente.

COMO RODAR (o jeito facil, com placar):

    python verificar.py

COMO RODAR (o jeito do Django, com detalhe de cada falha):

    python manage.py test academico -v 2

NO COMECO TUDO FALHA. Isso e o esperado -- as falhas sao o seu mapa.
Implemente um TODO, rode de novo, veja um teste ficar verde.

--- POR QUE VOCE NAO DEVE MEXER AQUI ---------------------------------

Este arquivo e o contrato da entrega: e com ele que o professor
corrige. Alterar o teste para ele passar nao faz o codigo funcionar --
faz o teste parar de dizer a verdade. Se voce acha que um teste esta
errado, chame o professor: pode ser que esteja mesmo, e ai o arquivo e
corrigido para todos.
"""

from decimal import Decimal

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db import connection, models
from django.test import TestCase
from django.urls import reverse

from contas.models import Usuario
from academico.models import Aluno, Disciplina, Inscricao

SENHA = "senha-de-teste-123"


# =====================================================================
# Ferramentas de apoio.
#
# Servem para que uma falha diga O QUE fazer, em vez de despejar um
# traceback do banco.
# =====================================================================


class BaseEntregaTest(TestCase):
    """Base dos testes, com verificacoes que dao mensagem clara."""

    def exigir_campo(self, modelo, nome, todo):
        """Falha com mensagem util se o campo nao existir no modelo."""
        try:
            return modelo._meta.get_field(nome)
        except FieldDoesNotExist:
            self.fail(
                f"\n  TODO {todo}: o modelo {modelo.__name__} nao tem o campo "
                f"'{nome}'.\n"
                f"  Declare-o em academico/models.py e depois rode:\n"
                f"      python manage.py makemigrations academico\n"
                f"      python manage.py migrate\n"
            )

    def exigir_tabela(self, modelo, todo):
        """Falha se a tabela do modelo nao existir no banco.

        Acontece quando os campos ja estao no models.py mas a migration
        nao foi gerada ou nao foi aplicada. E o equivalente ao
        "no such table: disciplina" da tabela de erros da Entrega 1.
        """
        tabela = modelo._meta.db_table
        if tabela not in connection.introspection.table_names():
            self.fail(
                f"\n  TODO {todo}: a tabela '{tabela}' nao existe no banco.\n"
                f"  Os campos podem estar certos, mas falta aplicar a migration:\n"
                f"      python manage.py makemigrations academico\n"
                f"      python manage.py migrate\n"
            )

    def exigir_colunas(self, modelo, nomes, todo):
        """Confere campo a campo E a tabela, na ordem certa."""
        for nome in nomes:
            self.exigir_campo(modelo, nome, todo)
        self.exigir_tabela(modelo, todo)


# =====================================================================
# TODO 0 -- a migration existe?
#
# Roda primeiro e falha ruidosamente, porque sem migration NADA mais
# funciona e todos os outros testes viriam com erro de banco.
# =====================================================================


class Todo00MigracaoTest(TestCase):
    def test_existe_migration_do_app_academico(self):
        from django.db.migrations.loader import MigrationLoader

        loader = MigrationLoader(connection, ignore_no_migrations=True)
        migracoes = [app for app, _ in loader.disk_migrations if app == "academico"]

        self.assertTrue(
            migracoes,
            "\n  O app academico ainda nao tem nenhuma migration.\n"
            "  Depois de declarar os campos dos TODOs 1, 2 e 3, rode:\n"
            "      python manage.py makemigrations academico\n"
            "      python manage.py migrate\n"
            "  A migration e o que transforma as suas classes Python em\n"
            "  tabelas de verdade no banco.\n",
        )


# =====================================================================
# TODO 1 -- modelo Aluno
# =====================================================================


class Todo01AlunoModeloTest(BaseEntregaTest):
    CAMPOS = ["matricula", "nome", "email", "data_nascimento", "ativo"]

    def test_campos_declarados(self):
        self.exigir_colunas(Aluno, self.CAMPOS, todo=1)

    def test_matricula_e_unica(self):
        campo = self.exigir_campo(Aluno, "matricula", todo=1)
        self.assertTrue(
            campo.unique,
            "\n  TODO 1: Aluno.matricula precisa ser unique=True.\n"
            "  Na Entrega 1 era 'matricula TEXT NOT NULL UNIQUE'. E o que\n"
            "  impede as matriculas duplicadas descritas no cenario.\n",
        )

    def test_nome_e_obrigatorio(self):
        campo = self.exigir_campo(Aluno, "nome", todo=1)
        self.assertFalse(
            campo.blank,
            "\n  TODO 1: Aluno.nome e obrigatorio -- nao use blank=True nele.\n",
        )

    def test_ativo_tem_padrao_verdadeiro(self):
        campo = self.exigir_campo(Aluno, "ativo", todo=1)
        self.assertIsInstance(
            campo,
            models.BooleanField,
            "\n  TODO 1: Aluno.ativo deve ser um BooleanField.\n"
            "  Na Entrega 1 era INTEGER 0/1; o Django cuida da conversao\n"
            "  para voce e no Python voce trabalha com True/False.\n",
        )
        self.assertIs(
            campo.default,
            True,
            "\n  TODO 1: Aluno.ativo precisa de default=True.\n"
            "  Era o 'DEFAULT 1' do CREATE TABLE da Entrega 1.\n",
        )

    def test_data_nascimento_e_data_e_aceita_vazio(self):
        campo = self.exigir_campo(Aluno, "data_nascimento", todo=1)
        self.assertIsInstance(
            campo,
            models.DateField,
            "\n  TODO 1: data_nascimento deve ser DateField, nao CharField.\n"
            "  Guardado como data, o banco valida e ordena corretamente --\n"
            "  com texto, '2005-13-45' entraria sem reclamar.\n",
        )
        self.assertTrue(
            campo.null and campo.blank,
            "\n  TODO 1: data_nascimento e opcional: use null=True E blank=True.\n"
            "  null -> a coluna aceita NULL; blank -> o formulario aceita vazio.\n",
        )

    def test_tabela_se_chama_aluno(self):
        self.assertEqual(
            Aluno._meta.db_table,
            "aluno",
            "\n  Nao altere o db_table do Meta: a tabela deve se chamar 'aluno',\n"
            "  igual a da Entrega 1.\n",
        )

    def test_str_e_legivel(self):
        self.exigir_colunas(Aluno, ["matricula", "nome"], todo=1)
        aluno = Aluno.objects.create(matricula="2024999", nome="Teste da Silva")

        texto = str(aluno)

        self.assertIn(
            "Teste da Silva",
            texto,
            "\n  TODO 1b: implemente o __str__ de Aluno devolvendo algo legivel,\n"
            "  por exemplo f'{self.matricula} - {self.nome}'.\n"
            f"  Hoje str(aluno) devolve: {texto!r}\n",
        )

    def test_matricula_duplicada_e_recusada_pelo_banco(self):
        self.exigir_colunas(Aluno, ["matricula", "nome"], todo=1)
        Aluno.objects.create(matricula="2024001", nome="Primeiro")

        from django.db import IntegrityError, transaction

        with self.assertRaises(
            IntegrityError,
            msg="\n  TODO 1: o banco deveria RECUSAR duas matriculas iguais.\n"
            "  Falta unique=True em Aluno.matricula.\n",
        ):
            with transaction.atomic():
                Aluno.objects.create(matricula="2024001", nome="Segundo")


# =====================================================================
# TODO 2 -- modelo Disciplina
# =====================================================================


class Todo02DisciplinaModeloTest(BaseEntregaTest):
    CAMPOS = ["codigo", "nome", "carga_horaria", "periodo"]

    def test_campos_declarados(self):
        self.exigir_colunas(Disciplina, self.CAMPOS, todo=2)

    def test_codigo_e_unico(self):
        campo = self.exigir_campo(Disciplina, "codigo", todo=2)
        self.assertTrue(
            campo.unique,
            "\n  TODO 2: Disciplina.codigo precisa ser unique=True.\n"
            "  E o que impede a mesma disciplina cadastrada tres vezes.\n",
        )

    def test_carga_horaria_e_inteiro_obrigatorio(self):
        campo = self.exigir_campo(Disciplina, "carga_horaria", todo=2)
        self.assertIsInstance(
            campo,
            models.IntegerField,
            "\n  TODO 2: carga_horaria deve ser IntegerField.\n",
        )
        self.assertFalse(
            campo.null,
            "\n  TODO 2: carga_horaria e obrigatoria (sem null=True).\n",
        )

    def test_periodo_e_opcional(self):
        campo = self.exigir_campo(Disciplina, "periodo", todo=2)
        self.assertTrue(
            campo.null and campo.blank,
            "\n  TODO 2: periodo e opcional: null=True e blank=True.\n",
        )

    def test_tabela_se_chama_disciplina(self):
        self.assertEqual(Disciplina._meta.db_table, "disciplina")

    def test_str_e_legivel(self):
        self.exigir_colunas(Disciplina, ["codigo", "nome", "carga_horaria"], todo=2)
        disciplina = Disciplina.objects.create(
            codigo="ARA0095", nome="Desenvolvimento Rapido", carga_horaria=80
        )

        texto = str(disciplina)

        self.assertIn(
            "ARA0095",
            texto,
            "\n  TODO 2b: implemente o __str__ de Disciplina, por exemplo\n"
            "  f'{self.codigo} - {self.nome}'.\n"
            f"  Hoje str(disciplina) devolve: {texto!r}\n",
        )


# =====================================================================
# TODO 3 -- modelo Inscricao (a tabela associativa)
# =====================================================================


class Todo03InscricaoModeloTest(BaseEntregaTest):
    CAMPOS = ["aluno", "disciplina", "nota1", "nota2"]

    def _dados(self):
        """Cria um aluno e uma disciplina para os testes de inscricao."""
        aluno = Aluno.objects.create(matricula="2024001", nome="Ana Souza")
        disciplina = Disciplina.objects.create(
            codigo="ARA0095", nome="Desenvolvimento Rapido", carga_horaria=80
        )
        return aluno, disciplina

    def test_campos_declarados(self):
        self.exigir_colunas(Inscricao, self.CAMPOS, todo=3)

    def test_aluno_e_chave_estrangeira(self):
        campo = self.exigir_campo(Inscricao, "aluno", todo=3)
        self.assertIsInstance(
            campo,
            models.ForeignKey,
            "\n  TODO 3: Inscricao.aluno deve ser um ForeignKey(Aluno, ...).\n"
            "  E a traducao de 'FOREIGN KEY (aluno_id) REFERENCES aluno(id)'.\n",
        )
        self.assertEqual(campo.related_model, Aluno)

    def test_disciplina_e_chave_estrangeira(self):
        campo = self.exigir_campo(Inscricao, "disciplina", todo=3)
        self.assertIsInstance(campo, models.ForeignKey)
        self.assertEqual(campo.related_model, Disciplina)

    def test_fk_usa_protect_para_preservar_historico(self):
        campo = self.exigir_campo(Inscricao, "aluno", todo=3)
        self.assertIs(
            campo.remote_field.on_delete,
            models.PROTECT,
            "\n  TODO 3: use on_delete=models.PROTECT no ForeignKey para Aluno.\n"
            "  Com CASCADE, apagar um aluno apagaria as notas dele em silencio --\n"
            "  o problema das 'notas orfas' citado na Entrega 1. PROTECT faz o\n"
            "  banco recusar a exclusao e preservar o historico academico.\n",
        )

    def test_related_name_permite_o_caminho_de_volta(self):
        campo = self.exigir_campo(Inscricao, "aluno", todo=3)
        self.assertEqual(
            campo.remote_field.get_accessor_name(),
            "inscricoes",
            "\n  TODO 3: use related_name='inscricoes' no ForeignKey para Aluno.\n"
            "  E o que permite escrever aluno.inscricoes.all() -- o JOIN de\n"
            "  volta, sem escrever JOIN.\n",
        )

    def test_unique_composto_declarado(self):
        self.exigir_colunas(Inscricao, ["aluno", "disciplina"], todo=3)

        pares = [
            set(c.fields)
            for c in Inscricao._meta.constraints
            if isinstance(c, models.UniqueConstraint)
        ]
        pares += [set(t) for t in Inscricao._meta.unique_together]

        self.assertIn(
            {"aluno", "disciplina"},
            pares,
            "\n  TODO 3: declare a restricao UNIQUE composta no Meta de Inscricao:\n"
            "      constraints = [\n"
            "          models.UniqueConstraint(\n"
            "              fields=['aluno', 'disciplina'],\n"
            "              name='inscricao_unica_por_aluno_disciplina',\n"
            "          )\n"
            "      ]\n"
            "  Era o 'UNIQUE (aluno_id, disciplina_id)' da Entrega 1: o mesmo\n"
            "  aluno nao pode se inscrever duas vezes na mesma disciplina.\n",
        )

    def test_inscricao_duplicada_e_recusada_pelo_banco(self):
        self.exigir_colunas(Inscricao, ["aluno", "disciplina"], todo=3)
        aluno, disciplina = self._dados()
        Inscricao.objects.create(aluno=aluno, disciplina=disciplina)

        from django.db import IntegrityError, transaction

        with self.assertRaises(
            IntegrityError,
            msg="\n  TODO 3: o banco deveria RECUSAR a inscricao duplicada.\n"
            "  Declarou a UniqueConstraint mas nao rodou makemigrations/migrate?\n"
            "  A restricao so passa a valer depois de aplicada no banco.\n",
        ):
            with transaction.atomic():
                Inscricao.objects.create(aluno=aluno, disciplina=disciplina)

    def test_notas_aceitam_vazio(self):
        for nome in ["nota1", "nota2"]:
            campo = self.exigir_campo(Inscricao, nome, todo=3)
            self.assertTrue(
                campo.null and campo.blank,
                f"\n  TODO 3: {nome} e opcional (a nota pode nao ter sido\n"
                f"  lancada ainda): use null=True e blank=True.\n",
            )

    def test_tabela_se_chama_inscricao(self):
        self.assertEqual(Inscricao._meta.db_table, "inscricao")

    def test_media_com_as_duas_notas(self):
        self.exigir_colunas(Inscricao, self.CAMPOS, todo=3)
        aluno, disciplina = self._dados()
        inscricao = Inscricao.objects.create(
            aluno=aluno, disciplina=disciplina, nota1=Decimal("8.0"), nota2=Decimal("6.0")
        )

        self.assertEqual(
            Decimal(str(inscricao.media)),
            Decimal("7.0"),
            "\n  TODO 3c: a property `media` deve devolver a media das duas notas.\n",
        )

    def test_media_e_none_quando_falta_nota(self):
        self.exigir_colunas(Inscricao, self.CAMPOS, todo=3)
        aluno, disciplina = self._dados()
        inscricao = Inscricao.objects.create(
            aluno=aluno, disciplina=disciplina, nota1=Decimal("8.0"), nota2=None
        )

        self.assertIsNone(
            inscricao.media,
            "\n  TODO 3c: sem as duas notas, a media nao existe -- devolva None.\n",
        )

    def test_media_funciona_com_nota_zero(self):
        """A pegadinha do `if not self.nota1`.

        Zero e falso em Python, mas zero e uma nota valida. Quem testou
        com `if not nota` em vez de `is None` devolve None aqui -- e o
        aluno que tirou 0 e 4 fica sem media na tela.
        """
        self.exigir_colunas(Inscricao, self.CAMPOS, todo=3)
        aluno, disciplina = self._dados()
        inscricao = Inscricao.objects.create(
            aluno=aluno, disciplina=disciplina, nota1=Decimal("0.0"), nota2=Decimal("4.0")
        )

        self.assertIsNotNone(
            inscricao.media,
            "\n  TODO 3c: nota 0 e uma nota VALIDA.\n"
            "  Nao use `if not self.nota1` -- zero e falso em Python e o aluno\n"
            "  que tirou zero ficaria sem media. Compare com `is None`.\n",
        )
        self.assertEqual(Decimal(str(inscricao.media)), Decimal("2.0"))


# =====================================================================
# TODO 4, 5 e 6 -- formularios
# =====================================================================


class Todo04a06FormulariosTest(BaseEntregaTest):
    def test_aluno_form_tem_os_campos(self):
        from academico.forms import AlunoForm

        self.assertEqual(
            set(AlunoForm().fields),
            {"matricula", "nome", "email", "data_nascimento", "ativo"},
            "\n  TODO 4: preencha a lista `fields` do Meta em AlunoForm\n"
            "  (academico/forms.py) com os cinco campos do aluno.\n",
        )

    def test_disciplina_form_tem_os_campos(self):
        from academico.forms import DisciplinaForm

        self.assertEqual(
            set(DisciplinaForm().fields),
            {"codigo", "nome", "carga_horaria", "periodo"},
            "\n  TODO 5: preencha a lista `fields` do Meta em DisciplinaForm.\n",
        )

    def test_inscricao_form_tem_os_campos(self):
        from academico.forms import InscricaoForm

        self.assertEqual(
            set(InscricaoForm().fields),
            {"aluno", "disciplina", "nota1", "nota2"},
            "\n  TODO 6: preencha a lista `fields` do Meta em InscricaoForm.\n",
        )

    def test_aluno_form_recusa_email_invalido(self):
        from academico.forms import AlunoForm

        form = AlunoForm(
            {"matricula": "2024001", "nome": "Ana", "email": "isso-nao-e-email"}
        )

        self.assertFalse(
            form.is_valid(),
            "\n  TODO 4 (bonus): o e-mail precisa ser validado.\n"
            "  Use EmailField no modelo (TODO 1) -- ele ja exige o '@'.\n",
        )
        self.assertIn("email", form.errors)

    def test_disciplina_form_recusa_carga_horaria_negativa(self):
        from academico.forms import DisciplinaForm

        form = DisciplinaForm(
            {"codigo": "ARA0095", "nome": "Teste", "carga_horaria": -10}
        )

        self.assertFalse(
            form.is_valid(),
            "\n  TODO 5 (bonus): carga horaria negativa nao existe.\n"
            "  Valide com MinValueValidator(1) no modelo e/ou com\n"
            "  clean_carga_horaria() no formulario.\n",
        )


# =====================================================================
# TODO 7 a 12 -- as views
# =====================================================================


class ViewsBaseTest(BaseEntregaTest):
    """Base das views: cria um usuario e ja faz login."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="secretaria",
            email="sec@escola.edu.br",
            password=SENHA,
            perfil=Usuario.Perfil.SECRETARIA,
        )
        self.client.force_login(self.usuario)

    def recusar_placeholder(self, resposta, todo):
        """Falha se a view ainda estiver devolvendo a tela provisoria."""
        templates = [t.name for t in resposta.templates if t.name]
        if "academico/nao_implementado.html" in templates:
            self.fail(
                f"\n  TODO {todo}: esta view ainda devolve a tela provisoria.\n"
                f"  Substitua a chamada de todo(...) em academico/views.py pela\n"
                f"  implementacao. O exemplo pronto esta em contas/views.py.\n"
            )


class Todo07AlunoListaTest(ViewsBaseTest):
    def test_exige_login(self):
        self.client.logout()

        resposta = self.client.get(reverse("academico:aluno_lista"))

        self.assertEqual(
            resposta.status_code,
            302,
            "\n  A listagem de alunos nao pode ficar aberta: mantenha o\n"
            "  @login_required na view.\n",
        )

    def test_lista_os_alunos(self):
        self.exigir_colunas(Aluno, ["matricula", "nome"], todo=1)
        Aluno.objects.create(matricula="2024001", nome="Ana Souza")
        Aluno.objects.create(matricula="2024002", nome="Bruno Lima")

        resposta = self.client.get(reverse("academico:aluno_lista"))
        self.recusar_placeholder(resposta, todo=7)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            "alunos",
            resposta.context,
            "\n  TODO 7: o template espera a variavel de contexto 'alunos'.\n"
            "  Use render(request, 'academico/aluno_lista.html',\n"
            "              {'alunos': alunos, 'busca': busca})\n",
        )
        self.assertEqual(len(resposta.context["alunos"]), 2)

    def test_busca_filtra(self):
        self.exigir_colunas(Aluno, ["matricula", "nome"], todo=1)
        Aluno.objects.create(matricula="2024001", nome="Ana Souza")
        Aluno.objects.create(matricula="2024002", nome="Bruno Lima")

        resposta = self.client.get(reverse("academico:aluno_lista"), {"busca": "Ana"})
        self.recusar_placeholder(resposta, todo=7)

        nomes = [a.nome for a in resposta.context["alunos"]]
        self.assertIn("Ana Souza", nomes)
        self.assertNotIn(
            "Bruno Lima",
            nomes,
            "\n  TODO 7: a busca precisa FILTRAR a listagem.\n"
            "  Leia o termo com request.GET.get('busca', '') e aplique\n"
            "  .filter(Q(nome__icontains=busca) | Q(matricula__icontains=busca))\n",
        )


class Todo08AlunoNovoTest(ViewsBaseTest):
    def test_get_mostra_o_formulario(self):
        resposta = self.client.get(reverse("academico:aluno_novo"))
        self.recusar_placeholder(resposta, todo=8)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            "form",
            resposta.context,
            "\n  TODO 8: o template espera a variavel de contexto 'form'.\n",
        )

    def test_post_valido_cadastra_e_redireciona(self):
        self.exigir_colunas(Aluno, ["matricula", "nome"], todo=1)

        resposta = self.client.post(
            reverse("academico:aluno_novo"),
            {
                "matricula": "2024010",
                "nome": "Novo Aluno",
                "email": "novo@aluno.edu.br",
                "data_nascimento": "2005-05-20",
                "ativo": "on",
            },
        )
        self.recusar_placeholder(resposta, todo=8)

        self.assertTrue(
            Aluno.objects.filter(matricula="2024010").exists(),
            "\n  TODO 8: o aluno nao foi gravado no banco.\n"
            "  Faltou o form.save() depois do form.is_valid()?\n",
        )
        self.assertEqual(
            resposta.status_code,
            302,
            "\n  TODO 8: depois de salvar, REDIRECIONE (padrao POST/Redirect/GET).\n"
            "  Sem o redirect, um F5 cadastra o mesmo aluno de novo.\n"
            "  Use: return redirect('academico:aluno_lista')\n",
        )

    def test_post_invalido_nao_cadastra(self):
        self.exigir_colunas(Aluno, ["matricula", "nome"], todo=1)

        resposta = self.client.post(
            reverse("academico:aluno_novo"), {"matricula": "", "nome": ""}
        )
        self.recusar_placeholder(resposta, todo=8)

        self.assertEqual(
            resposta.status_code,
            200,
            "\n  TODO 8: com o formulario invalido, NAO redirecione.\n"
            "  Renderize de novo levando o form com os erros, para o usuario\n"
            "  nao perder o que digitou.\n",
        )
        self.assertEqual(Aluno.objects.count(), 0)

    def test_matricula_duplicada_vira_mensagem_e_nao_traceback(self):
        """Item 6 da rubrica da Entrega 1, agora na web."""
        self.exigir_colunas(Aluno, ["matricula", "nome"], todo=1)
        Aluno.objects.create(matricula="2024001", nome="Ja Existe")

        resposta = self.client.post(
            reverse("academico:aluno_novo"),
            {"matricula": "2024001", "nome": "Outro", "ativo": "on"},
        )
        self.recusar_placeholder(resposta, todo=8)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Aluno.objects.count(), 1)


class Todo09AlunoEditarExcluirTest(ViewsBaseTest):
    def setUp(self):
        super().setUp()
        self.exigir_colunas(Aluno, ["matricula", "nome", "ativo"], todo=1)
        self.aluno = Aluno.objects.create(matricula="2024001", nome="Nome Antigo")

    def test_editar_altera_o_registro_existente(self):
        resposta = self.client.post(
            reverse("academico:aluno_editar", args=[self.aluno.pk]),
            {"matricula": "2024001", "nome": "Nome Novo", "ativo": "on"},
        )
        self.recusar_placeholder(resposta, todo=9)

        self.aluno.refresh_from_db()
        self.assertEqual(
            self.aluno.nome,
            "Nome Novo",
            "\n  TODO 9a: o registro nao foi alterado.\n"
            "  Passou instance=aluno ao montar o form? Sem isso o save()\n"
            "  faz INSERT e cria um aluno novo em vez de atualizar.\n",
        )
        self.assertEqual(
            Aluno.objects.count(),
            1,
            "\n  TODO 9a: em vez de ALTERAR, a sua view CRIOU outro aluno.\n"
            "  Falta o instance=aluno: AlunoForm(request.POST, instance=aluno)\n",
        )

    def test_editar_id_inexistente_da_404(self):
        resposta = self.client.get(reverse("academico:aluno_editar", args=[99999]))

        self.assertEqual(
            resposta.status_code,
            404,
            "\n  TODO 9a: use get_object_or_404(Aluno, pk=pk).\n"
            "  Ele devolve 404 quando o id nao existe -- substitui o\n"
            "  'if aluno is None' da Entrega 1.\n",
        )

    def test_get_na_exclusao_nao_altera_nada(self):
        """GET precisa ser seguro."""
        resposta = self.client.get(
            reverse("academico:aluno_excluir", args=[self.aluno.pk])
        )
        self.recusar_placeholder(resposta, todo=9)

        self.assertEqual(
            resposta.status_code,
            200,
            "\n  TODO 9b: o GET deve MOSTRAR a tela de confirmacao.\n",
        )
        self.assertTrue(
            Aluno.objects.filter(pk=self.aluno.pk).exists(),
            "\n  TODO 9b: o GET NAO pode excluir!\n"
            "  Um link que apaga dados e disparado por robo de busca e por\n"
            "  pre-carregador do navegador. Exclua somente no POST.\n",
        )
        self.aluno.refresh_from_db()
        self.assertTrue(self.aluno.ativo)

    def test_post_na_exclusao_remove_ou_desativa(self):
        resposta = self.client.post(
            reverse("academico:aluno_excluir", args=[self.aluno.pk])
        )
        self.recusar_placeholder(resposta, todo=9)

        self.assertEqual(
            resposta.status_code,
            302,
            "\n  TODO 9b: depois de excluir, redirecione para a listagem.\n",
        )

        # Aceita as DUAS estrategias: delete de verdade ou soft delete.
        # Qual usar e a sua decisao de projeto -- explique no README.
        existe = Aluno.objects.filter(pk=self.aluno.pk).first()
        if existe is not None:
            self.assertFalse(
                existe.ativo,
                "\n  TODO 9b: o aluno continua no banco E continua ativo --\n"
                "  ou seja, nada aconteceu.\n"
                "  Escolha uma estrategia:\n"
                "    DELETE:      aluno.delete()\n"
                "    SOFT DELETE: aluno.ativo = False\n"
                "                 aluno.save(update_fields=['ativo'])\n",
            )


class Todo10e11DisciplinaTest(ViewsBaseTest):
    def test_lista_disciplinas(self):
        self.exigir_colunas(Disciplina, ["codigo", "nome", "carga_horaria"], todo=2)
        Disciplina.objects.create(codigo="ARA0095", nome="DRAP", carga_horaria=80)

        resposta = self.client.get(reverse("academico:disciplina_lista"))
        self.recusar_placeholder(resposta, todo=10)

        self.assertIn(
            "disciplinas",
            resposta.context,
            "\n  TODO 10: o template espera a variavel de contexto 'disciplinas'.\n",
        )
        self.assertEqual(len(resposta.context["disciplinas"]), 1)

    def test_cadastra_disciplina(self):
        self.exigir_colunas(Disciplina, ["codigo", "nome", "carga_horaria"], todo=2)

        resposta = self.client.post(
            reverse("academico:disciplina_nova"),
            {"codigo": "ARA0017", "nome": "Banco de Dados", "carga_horaria": 60, "periodo": 2},
        )
        self.recusar_placeholder(resposta, todo=11)

        self.assertTrue(
            Disciplina.objects.filter(codigo="ARA0017").exists(),
            "\n  TODO 11a: a disciplina nao foi gravada.\n",
        )
        self.assertEqual(resposta.status_code, 302)

    def test_edita_disciplina(self):
        self.exigir_colunas(Disciplina, ["codigo", "nome", "carga_horaria"], todo=2)
        disciplina = Disciplina.objects.create(
            codigo="ARA0095", nome="Nome Antigo", carga_horaria=80
        )

        resposta = self.client.post(
            reverse("academico:disciplina_editar", args=[disciplina.pk]),
            {"codigo": "ARA0095", "nome": "Nome Novo", "carga_horaria": 80},
        )
        self.recusar_placeholder(resposta, todo=11)

        disciplina.refresh_from_db()
        self.assertEqual(
            disciplina.nome,
            "Nome Novo",
            "\n  TODO 11b: faltou o instance=disciplina no form.\n",
        )
        self.assertEqual(Disciplina.objects.count(), 1)

    def test_exclui_disciplina(self):
        self.exigir_colunas(Disciplina, ["codigo", "nome", "carga_horaria"], todo=2)
        disciplina = Disciplina.objects.create(
            codigo="ARA0095", nome="DRAP", carga_horaria=80
        )

        resposta = self.client.post(
            reverse("academico:disciplina_excluir", args=[disciplina.pk])
        )
        self.recusar_placeholder(resposta, todo=11)

        self.assertFalse(
            Disciplina.objects.filter(pk=disciplina.pk).exists(),
            "\n  TODO 11c: a disciplina nao foi excluida no POST.\n",
        )


class Todo12InscricaoTest(ViewsBaseTest):
    def setUp(self):
        super().setUp()
        self.exigir_colunas(Aluno, ["matricula", "nome", "ativo"], todo=1)
        self.exigir_colunas(Disciplina, ["codigo", "nome", "carga_horaria"], todo=2)
        self.exigir_colunas(Inscricao, ["aluno", "disciplina", "nota1", "nota2"], todo=3)

        self.aluno = Aluno.objects.create(matricula="2024001", nome="Ana Souza")
        self.disciplina = Disciplina.objects.create(
            codigo="ARA0095", nome="DRAP", carga_horaria=80
        )

    def test_lista_inscricoes(self):
        Inscricao.objects.create(aluno=self.aluno, disciplina=self.disciplina)

        resposta = self.client.get(reverse("academico:inscricao_lista"))
        self.recusar_placeholder(resposta, todo=12)

        self.assertIn(
            "inscricoes",
            resposta.context,
            "\n  TODO 12a: o template espera a variavel de contexto 'inscricoes'.\n",
        )
        self.assertEqual(len(resposta.context["inscricoes"]), 1)

    def test_listagem_evita_o_problema_n_mais_1(self):
        """A listagem mostra dados de outras tabelas: use select_related.

        Sem ele, cada linha da tabela dispara duas consultas extras
        (uma para o aluno, uma para a disciplina). Com 3 inscricoes o
        gasto seria 7 consultas; com 500, mais de mil.
        """
        for i in range(3):
            aluno = Aluno.objects.create(matricula=f"20250{i}", nome=f"Aluno {i}")
            Inscricao.objects.create(aluno=aluno, disciplina=self.disciplina)

        resposta = self.client.get(reverse("academico:inscricao_lista"))
        self.recusar_placeholder(resposta, todo=12)

        # .all() devolve um CLONE do QuerySet, sem o cache que o template
        # ja preencheu ao renderizar a pagina. Sem esse clone, o laco
        # abaixo nao consultaria o banco nenhuma vez e o teste nao mediria
        # coisa alguma.
        consulta = resposta.context["inscricoes"].all()

        # Com select_related: 1 consulta, com JOIN, e acabou.
        # Sem select_related: 1 para as inscricoes + 2 por linha (aluno e
        # disciplina) = 7 consultas para estas 3 inscricoes.
        with self.assertNumQueries(
            1,
            msg="\n  TODO 12a: use select_related para evitar o problema N+1:\n"
            "      Inscricao.objects.select_related('aluno', 'disciplina')\n"
            "  Sem ele, o Django faz uma consulta por linha para buscar o\n"
            "  aluno e a disciplina. E o assunto da Entrega 2 --\n"
            "  material/03-orm-na-pratica.md.\n",
        ):
            for inscricao in consulta:
                _ = inscricao.aluno.nome
                _ = inscricao.disciplina.nome

    def test_cria_inscricao(self):
        resposta = self.client.post(
            reverse("academico:inscricao_nova"),
            {"aluno": self.aluno.pk, "disciplina": self.disciplina.pk},
        )
        self.recusar_placeholder(resposta, todo=12)

        self.assertTrue(
            Inscricao.objects.filter(
                aluno=self.aluno, disciplina=self.disciplina
            ).exists(),
            "\n  TODO 12b: a inscricao nao foi gravada.\n",
        )

    def test_lanca_notas(self):
        inscricao = Inscricao.objects.create(
            aluno=self.aluno, disciplina=self.disciplina
        )

        resposta = self.client.post(
            reverse("academico:inscricao_editar", args=[inscricao.pk]),
            {
                "aluno": self.aluno.pk,
                "disciplina": self.disciplina.pk,
                "nota1": "8.5",
                "nota2": "7.0",
            },
        )
        self.recusar_placeholder(resposta, todo=12)

        inscricao.refresh_from_db()
        self.assertEqual(
            Decimal(str(inscricao.nota1)),
            Decimal("8.5"),
            "\n  TODO 12c: as notas nao foram gravadas.\n"
            "  Faltou o instance=inscricao no form?\n",
        )

    def test_inscricao_duplicada_nao_quebra_a_tela(self):
        """A UniqueConstraint deve virar mensagem, nao erro 500."""
        Inscricao.objects.create(aluno=self.aluno, disciplina=self.disciplina)

        resposta = self.client.post(
            reverse("academico:inscricao_nova"),
            {"aluno": self.aluno.pk, "disciplina": self.disciplina.pk},
        )
        self.recusar_placeholder(resposta, todo=12)

        self.assertEqual(
            resposta.status_code,
            200,
            "\n  TODO 12b: inscricao duplicada deve voltar o formulario com\n"
            "  a mensagem de erro -- nao um traceback nem um redirect.\n"
            "  O ModelForm faz isso sozinho SE a UniqueConstraint do TODO 3\n"
            "  estiver declarada e aplicada no banco.\n",
        )
        self.assertEqual(Inscricao.objects.count(), 1)


# =====================================================================
# Organizacao do projeto
# =====================================================================


class OrganizacaoTest(TestCase):
    def test_nao_existe_input_nem_print_de_menu_nas_views(self):
        """Item 5 da rubrica: separacao de responsabilidades.

        Na Entrega 1 a regra era: nenhum print() ou input() dentro dos
        crud_*.py. Aqui e o mesmo principio: a view nao conversa pelo
        terminal, ela devolve dados ao template.
        """
        import pathlib

        codigo = pathlib.Path("academico/views.py").read_text()

        self.assertNotIn(
            "input(",
            codigo,
            "\n  academico/views.py nao pode usar input(). Numa aplicacao web\n"
            "  isso travaria o servidor esperando alguem digitar no terminal.\n",
        )

    def test_nao_ha_sql_montado_com_f_string(self):
        """Item 4 da rubrica: parametros, nunca concatenacao.

        O ORM ja parametriza tudo. Se alguem apelou para raw() com
        f-string, a brecha de SQL Injection volta -- e o item e zerado.
        """
        import pathlib
        import re

        for caminho in ["academico/views.py", "academico/models.py", "academico/forms.py"]:
            codigo = pathlib.Path(caminho).read_text()

            suspeitas = re.findall(r'\.raw\(\s*f["\']', codigo)
            self.assertFalse(
                suspeitas,
                f"\n  {caminho}: SQL montado com f-string dentro de .raw().\n"
                "  E a brecha de SQL Injection discutida em aula. Use o ORM,\n"
                "  ou passe parametros: .raw('SELECT ... WHERE id = %s', [valor])\n",
            )

    def test_todos_os_apps_estao_instalados(self):
        self.assertTrue(apps.is_installed("contas"))
        self.assertTrue(apps.is_installed("academico"))
