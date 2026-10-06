"""
GABARITO -- academico/models.py resolvido.

NAO faz parte do pacote entregue ao aluno. Serve para:
  - provar que os TODOs e a suite de testes sao satisfaziveis;
  - dar ao professor a referencia na hora de corrigir;
  - permitir demonstrar o sistema completo em aula.

Para usar:  cp gabarito/models.py academico/models.py   (e os demais)
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Aluno(models.Model):
    matricula = models.CharField("matricula", max_length=20, unique=True)
    nome = models.CharField("nome", max_length=120)
    email = models.EmailField("e-mail", blank=True)
    data_nascimento = models.DateField("data de nascimento", null=True, blank=True)
    ativo = models.BooleanField("ativo", default=True)

    class Meta:
        db_table = "aluno"
        verbose_name = "aluno"
        verbose_name_plural = "alunos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.matricula} - {self.nome}"


class Disciplina(models.Model):
    codigo = models.CharField("codigo", max_length=15, unique=True)
    nome = models.CharField("nome", max_length=120)
    carga_horaria = models.IntegerField(
        "carga horaria",
        validators=[MinValueValidator(1)],
    )
    periodo = models.IntegerField("periodo", null=True, blank=True)

    class Meta:
        db_table = "disciplina"
        verbose_name = "disciplina"
        verbose_name_plural = "disciplinas"
        ordering = ["periodo", "nome"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class Inscricao(models.Model):
    aluno = models.ForeignKey(
        Aluno,
        on_delete=models.PROTECT,
        related_name="inscricoes",
        verbose_name="aluno",
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.PROTECT,
        related_name="inscricoes",
        verbose_name="disciplina",
    )
    nota1 = models.DecimalField(
        "1a nota",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    nota2 = models.DecimalField(
        "2a nota",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )

    class Meta:
        db_table = "inscricao"
        verbose_name = "inscricao"
        verbose_name_plural = "inscricoes"
        ordering = ["aluno", "disciplina"]
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "disciplina"],
                name="inscricao_unica_por_aluno_disciplina",
            )
        ]

    def __str__(self):
        return f"{self.aluno} em {self.disciplina}"

    @property
    def media(self):
        # `is None` e nao `if not`: nota 0 e valida e seria falsa.
        if self.nota1 is None or self.nota2 is None:
            return None
        return (self.nota1 + self.nota2) / 2
