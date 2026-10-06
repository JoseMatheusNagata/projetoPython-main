"""
=====================================================================
 MODELO DE DADOS DO SISTEMA ACADEMICO -- TODO 1, 2 e 3
=====================================================================

Este e o arquivo mais importante do trabalho. Tudo o mais depende dele:
os formularios leem os campos daqui, as views consultam estes modelos e
as tabelas do PostgreSQL sao geradas a partir destas classes.

Voce ja escreveu este modelo uma vez, em SQL, na Entrega 1:

    CREATE TABLE IF NOT EXISTS aluno (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula       TEXT NOT NULL UNIQUE,
        nome            TEXT NOT NULL,
        email           TEXT,
        data_nascimento TEXT,
        ativo           INTEGER NOT NULL DEFAULT 1
    )

Agora escreva o MESMO modelo como classes Python. O Django gera o SQL.

--- COMO TRABALHAR NESTE ARQUIVO -------------------------------------

  1. Implemente um TODO.
  2. Gere e aplique a migration:
         python manage.py makemigrations academico
         python manage.py migrate
  3. Confira o que foi gerado:
         python manage.py sqlmigrate academico 0001
  4. Rode a verificacao:
         python verificar.py

--- EXEMPLO COMPLETO PARA CONSULTAR ----------------------------------

  contas/models.py tem um modelo pronto e comentado (o Usuario).
  material/02-models-e-migrations.md explica cada tipo de campo.

--- TABELA DE TRADUCAO ------------------------------------------------

  SQL da Entrega 1              Django
  ----------------------------  -------------------------------------
  TEXT NOT NULL                 models.CharField(max_length=100)
  TEXT (pode ser vazio)         models.CharField(..., blank=True)
  TEXT UNIQUE                   models.CharField(..., unique=True)
  INTEGER                       models.IntegerField()
  REAL                          models.FloatField() / DecimalField
  TEXT no formato AAAA-MM-DD    models.DateField()
  INTEGER 0 ou 1                models.BooleanField()
  FOREIGN KEY (x) REFERENCES    models.ForeignKey(Modelo, on_delete=...)
  UNIQUE (a, b)                 UniqueConstraint(fields=["a", "b"], ...)
  id INTEGER PRIMARY KEY        (nao escreva: o Django cria sozinho)

=====================================================================
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Aluno(models.Model):
    """
    TODO 1 -- Declare os campos da tabela `aluno`.
    ==============================================

    Campos esperados (mesmos nomes da Entrega 1 -- os testes conferem):

      matricula        texto curto, OBRIGATORIO, UNICO
                       -> models.CharField("matricula", max_length=20, unique=True)

      nome             texto, OBRIGATORIO
                       -> models.CharField("nome", max_length=120)

      email            e-mail, OPCIONAL
                       -> models.EmailField("e-mail", blank=True)
                       Use EmailField em vez de CharField: ele ja valida
                       a presenca do "@" -- resolve metade do bonus de
                       validacao de graca.

      data_nascimento  data, OPCIONAL
                       -> models.DateField("data de nascimento",
                                           null=True, blank=True)

      ativo            verdadeiro/falso, padrao VERDADEIRO
                       -> models.BooleanField("ativo", default=True)

    ATENCAO -- `null` e `blank` NAO sao a mesma coisa:

      null=True   -> a COLUNA do banco aceita NULL
      blank=True  -> o FORMULARIO aceita o campo em branco

    Para texto, use SO blank=True (o Django guarda string vazia, nao
    NULL -- assim voce nao precisa testar dois "vazios" diferentes).
    Para data e numero, use os DOIS, porque nao existe "data vazia".

    Esta e a pegadinha numero 1 de quem esta comecando. Esta explicada
    em material/02-models-e-migrations.md.
    """

    # >>> ESCREVA OS CAMPOS AQUI <<<
    #campos da tabela
    matricula = models.CharField("matricula", max_length=20, unique=True)
    nome = models.CharField("nome", max_length=120)
    email = models.EmailField("e-mail", blank=True)
    data_nascimento = models.DateField("data de nascimento", null=True, blank=True)
    ativo = models.BooleanField("ativo", default=True)

    class Meta:
        # Mantemos o nome de tabela da Entrega 1. Sem esta linha, o
        # Django criaria a tabela como "academico_aluno". Assim voce
        # abre o pgAdmin e reconhece o banco que voce mesmo modelou.
        db_table = "aluno"
        verbose_name = "aluno"
        verbose_name_plural = "alunos"
        # DESCOMENTE depois de declarar o campo `nome` (TODO 1).
        # ordering define a ordem padrao de TODA consulta a este
        # modelo -- equivale a por ORDER BY nome em todo SELECT.
        # (Esta linha vem comentada porque o Django recusa subir com
        #  ordering apontando para um campo que ainda nao existe.)
        ordering = ["nome"]

    def __str__(self):
        """
        TODO 1b -- devolva algo legivel, por exemplo:

            return f"{self.matricula} - {self.nome}"

        Isto aparece nos <select> dos formularios e no admin. Sem
        implementar, voce vai ver "Aluno object (1)" na tela de
        inscricao e nao vai saber quem e quem.
        """
        return f"{self.matricula} - {self.nome}"


class Disciplina(models.Model):
    """
    TODO 2 -- Declare os campos da tabela `disciplina`.
    ===================================================

      codigo          texto curto, OBRIGATORIO, UNICO   (ex.: "ARA0095")
      nome            texto, OBRIGATORIO
      carga_horaria   inteiro, OBRIGATORIO
      periodo         inteiro, OPCIONAL

    Dica para o bonus de validacao: carga horaria negativa nao existe.
    Da para impedir isso em DOIS lugares, e o certo e fazer nos dois:

      no MODELO, com validators -- vale para qualquer caminho que grave
      no banco (formulario, admin, shell, seed):

          carga_horaria = models.IntegerField(
              "carga horaria",
              validators=[MinValueValidator(1)],
          )

      no FORMULARIO, com clean_carga_horaria() -- para dar a mensagem
      amigavel ao usuario (TODO 5).

    Regra geral: restricao de INTEGRIDADE mora no modelo/banco; MENSAGEM
    mora no formulario. Validar so na tela deixa a porta dos fundos
    aberta -- foi esse o raciocinio do `UNIQUE` na Entrega 1.

    MinValueValidator e MaxValueValidator ja estao importados no topo
    deste arquivo.
    """

    # >>> ESCREVA OS CAMPOS AQUI <<<
    
    codigo = models.CharField("codigo", max_length=20, unique=True)
    nome = models.CharField("nome", max_length=120)
    carga_horaria = models.IntegerField(
        "carga horaria", 
        validators=[MinValueValidator(1)]
    )
    periodo = models.IntegerField("periodo", null=True, blank=True)

    class Meta:
        db_table = "disciplina"
        verbose_name = "disciplina"
        verbose_name_plural = "disciplinas"
        # DESCOMENTE depois de declarar os campos (TODO 2).
        ordering = ["periodo", "nome"]

    def __str__(self):
        """TODO 2b -- sugestao: f"{self.codigo} - {self.nome}" """
        return f"{self.codigo} - {self.nome}"


class Inscricao(models.Model):
    """
    TODO 3 -- A TABELA ASSOCIATIVA. O coracao do modelo.
    ====================================================

    Um aluno cursa varias disciplinas; uma disciplina tem varios
    alunos. Esse N:N nao cabe em duas tabelas -- precisa desta
    terceira, exatamente como no enunciado da Entrega 1.

      aluno          FK -> Aluno,       OBRIGATORIO
      disciplina     FK -> Disciplina,  OBRIGATORIO
      nota1          decimal 0 a 10, OPCIONAL
      nota2          decimal 0 a 10, OPCIONAL

    --- AS CHAVES ESTRANGEIRAS ---------------------------------------

        aluno = models.ForeignKey(
            Aluno,
            on_delete=models.PROTECT,
            related_name="inscricoes",
            verbose_name="aluno",
        )

    `on_delete` responde: "e se o aluno for apagado?". E OBRIGATORIO --
    o Django recusa a migration sem ele, porque nao existe resposta
    padrao correta. As opcoes que interessam:

        PROTECT  recusa apagar o aluno se ele tiver inscricao.
                 >>> ESCOLHA ESTA. <<<
                 E a traducao do "notas orfas" da tabela de erros da
                 Entrega 1: o banco protegendo voce de destruir
                 historico academico por um clique errado.

        CASCADE  apaga as inscricoes junto com o aluno. Silencioso e
                 destrutivo -- as notas somem sem aviso.

        SET_NULL poe NULL na FK (exige null=True). Deixa inscricao sem
                 aluno, o que nao significa nada.

    `related_name="inscricoes"` cria o caminho de VOLTA. Com ele voce
    escreve `aluno.inscricoes.all()` para pegar as inscricoes de um
    aluno -- o JOIN, sem escrever JOIN.

    --- A RESTRICAO UNIQUE COMPOSTA ----------------------------------

    O mesmo aluno nao pode se inscrever duas vezes na mesma disciplina.
    Em SQL era UNIQUE (aluno_id, disciplina_id). Aqui:

        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "disciplina"],
                name="inscricao_unica_por_aluno_disciplina",
            )
        ]

    Vai dentro da classe Meta, abaixo.

    --- A PERGUNTA DA ARGUICAO ---------------------------------------

    "Por que nota1 fica em `inscricao`, e nao em `aluno` nem em
    `disciplina`?"

    Responda com o modelo na frente. A nota nao e um atributo do aluno
    (ele tem uma nota por disciplina) nem da disciplina (ela tem uma
    nota por aluno). A nota e um atributo do ENCONTRO entre os dois --
    e o encontro e justamente esta tabela.
    """

    # >>> ESCREVA OS CAMPOS AQUI <<<
    #campos da tabela
    aluno = models.ForeignKey("Aluno",
            on_delete=models.PROTECT,
            related_name="inscricoes",
            verbose_name="aluno",
        )

    disciplina = models.ForeignKey("Disciplina",
            on_delete=models.PROTECT,
            related_name="inscricoes",
            verbose_name="disciplina"
            )
    
    nota1 = models.DecimalField(
             "1a nota", max_digits=4, decimal_places=2,
            null=True, blank=True,
             validators=[MinValueValidator(0), MaxValueValidator(10)],
            )

    nota2 = models.DecimalField(
             "2a nota", max_digits=4, decimal_places=2,
             null=True, blank=True,
             validators=[MinValueValidator(0), MaxValueValidator(10)],
            )

    #
    # Para as notas, DecimalField e melhor que FloatField:
    #
    #     nota1 = models.DecimalField(
    #         "1a nota", max_digits=4, decimal_places=2,
    #         null=True, blank=True,
    #         validators=[MinValueValidator(0), MaxValueValidator(10)],
    #     )
    #
    # Por que nao FloatField? Porque float e binario e nao representa
    # decimal exato: em Python, 0.1 + 0.2 == 0.3 e False. Em nota de
    # aluno, um centesimo decide aprovacao. Decimal guarda o valor
    # exato. (A Entrega 1 usou REAL porque o SQLite nao oferece
    # melhor; o PostgreSQL oferece.)

    class Meta:
        db_table = "inscricao"
        verbose_name = "inscricao"
        verbose_name_plural = "inscricoes"
        # DESCOMENTE depois de declarar as chaves estrangeiras (TODO 3).
        ordering = ["aluno", "disciplina"]
        # >>> DECLARE A UniqueConstraint AQUI <<<
        constraints = [
                    models.UniqueConstraint(
                        fields=["aluno", "disciplina"],
                        name="inscricao_unica_por_aluno_disciplina",
                    )
                ]

    def __str__(self):
        """TODO 3b -- sugestao: f"{self.aluno} em {self.disciplina}" """
        return f"{self.aluno} em {self.disciplina}"

    @property
    def media(self):
        """
        TODO 3c (opcional, mas os testes conferem) -- media das notas.

        Regras:
          - as duas notas lancadas  -> devolve a media
          - alguma nota faltando    -> devolve None (media nao existe)

        Cuidado: `if not self.nota1` esta ERRADO. Uma nota 0 e falsa em
        Python, e zero e uma nota valida -- o aluno que tirou 0 ficaria
        sem media. Compare com None explicitamente:

            if self.nota1 is None or self.nota2 is None:
                return None
            return (self.nota1 + self.nota2) / 2
        """
        if self.nota1 is None or self.nota2 is None:
            return None
        return (self.nota1 + self.nota2) / 2
