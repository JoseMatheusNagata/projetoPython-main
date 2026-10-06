"""
=====================================================================
 FORMULARIOS DO SISTEMA ACADEMICO -- TODO 4, 5 e 6
=====================================================================

Um ModelForm le o modelo e monta sozinho os campos do HTML, a
validacao e a conversao de tipos. Voce so diz QUAL modelo e QUAIS
campos.

EXEMPLO PRONTO PARA COPIAR O PADRAO: contas/forms.py
LEITURA: material/04-forms-e-validacao.md

--- ONDE VALIDAR -----------------------------------------------------

Ha dois lugares, e eles nao competem:

  no MODELO (validators=[...])  -> integridade. Vale para o formulario,
                                   o admin, o shell e o seed. E a rede
                                   de seguranca.
  no FORMULARIO (clean_<campo>) -> mensagem amigavel para quem esta
                                   digitando.

O bonus de "validacao de entrada" da rubrica e avaliado aqui.
=====================================================================
"""

from django import forms

from .models import Aluno, Disciplina, Inscricao


class BootstrapMixin:
    """Aplica as classes CSS do Bootstrap nos campos.

    Ja vem pronto -- e o mesmo de contas/forms.py, copiado para o app
    ficar independente. Voce nao precisa mexer aqui.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            widget = campo.widget

            if isinstance(widget, forms.CheckboxInput):
                classe = "form-check-input"
            elif isinstance(widget, forms.Select):
                classe = "form-select"
            else:
                classe = "form-control"

            existente = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existente} {classe}".strip()


class AlunoForm(BootstrapMixin, forms.ModelForm):
    """
    TODO 4 -- Formulario de cadastro e edicao de aluno.
    ===================================================

    Passo 1: declare o Meta apontando para o modelo e os campos:

        class Meta:
            model = Aluno
            fields = ["matricula", "nome", "email", "data_nascimento", "ativo"]

    Passo 2: o campo de data. Por padrao o Django gera um <input
    type="text"> e o usuario precisa adivinhar o formato. Troque pelo
    seletor de data nativo do navegador:

            widgets = {
                "data_nascimento": forms.DateInput(
                    attrs={"type": "date"},
                    format="%Y-%m-%d",
                ),
            }

    O `format` importa: sem ele, ao EDITAR um aluno o campo aparece
    vazio -- o navegador so entende AAAA-MM-DD e o Django estaria
    mandando dd/mm/aaaa. Bug classico, dificil de achar sozinho.

    Passo 3 (bonus): valide a matricula. Sugestoes de regra --
    nao pode ser so espaco, deve ter ao menos 4 caracteres, e convem
    normalizar para maiusculas:

        def clean_matricula(self):
            matricula = self.cleaned_data["matricula"].strip().upper()
            if len(matricula) < 4:
                raise forms.ValidationError("A matricula deve ter ao menos 4 caracteres.")
            return matricula

    Repare que clean_<campo> sempre DEVOLVE o valor. Se voce esquecer
    o return, o campo vira None e o aluno e salvo sem matricula.

    NAO precisa validar duplicidade na mao: o unique=True do modelo ja
    faz isso e o ModelForm converte a violacao em mensagem de campo
    automaticamente. E o "tratamento de erro no cadastro duplicado" do
    item 6 da rubrica da Entrega 1 -- de graca.
    """

    class Meta:
        model = Aluno
        fields = []  # >>> SUBSTITUA pela lista de campos <<<


class DisciplinaForm(BootstrapMixin, forms.ModelForm):
    """
    TODO 5 -- Formulario de disciplina.
    ===================================

    Espelhe o AlunoForm:

        class Meta:
            model = Disciplina
            fields = ["codigo", "nome", "carga_horaria", "periodo"]

    Bonus -- carga horaria positiva, com mensagem amigavel:

        def clean_carga_horaria(self):
            valor = self.cleaned_data["carga_horaria"]
            if valor <= 0:
                raise forms.ValidationError("A carga horaria deve ser maior que zero.")
            return valor

    E convem normalizar o codigo para maiusculas em clean_codigo(),
    para que "ara0095" e "ARA0095" nao virem duas disciplinas -- que e
    exatamente o problema dos "nomes de disciplina escritos de tres
    formas diferentes" descrito no cenario do trabalho.
    """

    class Meta:
        model = Disciplina
        fields = []  # >>> SUBSTITUA pela lista de campos <<<


class InscricaoForm(BootstrapMixin, forms.ModelForm):
    """
    TODO 6 -- Inscricao de aluno em disciplina e lancamento de notas.
    =================================================================

        class Meta:
            model = Inscricao
            fields = ["aluno", "disciplina", "nota1", "nota2"]

    Para as FKs o Django gera um <select> sozinho, ja preenchido com
    todos os alunos e disciplinas. O texto de cada opcao vem do
    __str__ do modelo -- se o TODO 1b nao estiver feito, a lista vai
    mostrar "Aluno object (1)" e nao dara para usar.

    --- DUAS VALIDACOES QUE VALEM PONTO ------------------------------

    1) So aluno ATIVO pode se inscrever. Limite as opcoes do <select>
       no __init__:

           def __init__(self, *args, **kwargs):
               super().__init__(*args, **kwargs)
               self.fields["aluno"].queryset = Aluno.objects.filter(ativo=True)

       Filtrar a lista e melhor do que aceitar e depois reclamar: o
       usuario nao chega nem a ver a opcao errada.

    2) A mensagem de inscricao duplicada. A UniqueConstraint do TODO 3
       ja impede no banco, e o ModelForm exibe o erro -- porem com o
       texto padrao do Django. Para uma mensagem melhor, sobrescreva:

           class Meta:
               ...
               error_messages = {
                   forms.models.NON_FIELD_ERRORS: {
                       "unique_together": "Este aluno ja esta inscrito nesta disciplina.",
                   }
               }

    --- O QUE NAO FAZER ----------------------------------------------

    Nao tente checar a duplicidade com um `if Inscricao.objects.filter(...)`
    e mais nada. Entre a sua consulta e o save() existe uma janela em
    que outra requisicao pode inserir o mesmo par. Quem garante de
    verdade e a restricao no banco; o formulario so traduz o erro para
    o usuario. Foi por isso que o enunciado da Entrega 1 dizia que o
    "UNIQUE constraint failed" e o banco protegendo voce.
    """

    class Meta:
        model = Inscricao
        fields = []  # >>> SUBSTITUA pela lista de campos <<<
