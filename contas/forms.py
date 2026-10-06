"""
Formularios do app de contas.

Um Form do Django faz tres coisas que voce fazia na mao na Entrega 1:

  1. DESENHA o HTML dos campos      (era o seu print("Digite o nome: "))
  2. VALIDA o que o usuario mandou  (era o seu if/else antes do INSERT)
  3. CONVERTE texto para o tipo certo -- "2024-03-15" vira date

ModelForm faz tudo isso LENDO O MODELO: voce diz qual modelo e quais
campos, e ele deduz o resto. E o coracao do "desenvolvimento rapido".

Leitura: material/04-forms-e-validacao.md
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Usuario


# =====================================================================
# Um detalhe de aparencia, explicado uma vez so.
#
# O Django gera <input type="text" name="nome">, sem classe CSS. O
# Bootstrap precisa de class="form-control" para estilizar. Em vez de
# repetir isso campo a campo, o mixin abaixo percorre todos os campos
# no __init__ e aplica a classe certa.
#
# "Mixin" = uma classe feita para ser combinada com outras, que carrega
# um comportamento reaproveitavel.
# =====================================================================


class BootstrapMixin:
    """Aplica as classes CSS do Bootstrap a todos os campos do form."""

    def __init__(self, *args, **kwargs):
        # super() chama o __init__ original do Form, que e quem de fato
        # monta self.fields. So depois disso podemos mexer nos campos.
        super().__init__(*args, **kwargs)

        for campo in self.fields.values():
            widget = campo.widget

            if isinstance(widget, forms.CheckboxInput):
                classe = "form-check-input"
            elif isinstance(widget, forms.Select):
                classe = "form-select"
            else:
                classe = "form-control"

            # attrs e o dicionario de atributos HTML do campo.
            # Concatenamos para nao apagar classes que ja existam.
            existente = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existente} {classe}".strip()


class LoginForm(BootstrapMixin, AuthenticationForm):
    """Formulario da tela de login.

    AuthenticationForm ja vem pronto do Django e faz o trabalho pesado:
    confere usuario e senha, rejeita conta inativa (is_active=False) e
    devolve a mensagem de erro adequada. Nos so ajustamos a aparencia e
    os textos.

    Repare que NAO existe nenhuma consulta SQL aqui. Comparar a senha
    digitada com o hash guardado no banco e responsabilidade do Django
    -- e ainda bem, porque fazer isso errado e como se vazam senhas.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "seu usuario", "autofocus": True}
        )
        self.fields["password"].widget.attrs.update({"placeholder": "sua senha"})


class UsuarioCriarForm(BootstrapMixin, UserCreationForm):
    """Cadastro de um novo usuario.

    Herda de UserCreationForm, que ja traz os dois campos de senha
    (password1 e password2), confere se batem e aplica os validadores
    do AUTH_PASSWORD_VALIDATORS (tamanho minimo, senha nao obvia etc.).
    Alem disso, salva a senha com HASH -- nunca em texto puro.
    """

    class Meta:
        model = Usuario
        # A ordem desta lista e a ordem em que os campos aparecem na
        # tela. Os campos de senha sao acrescentados pelo pai.
        fields = ["username", "first_name", "last_name", "email", "perfil"]
        labels = {
            "username": "Usuario (login)",
            "first_name": "Nome",
            "last_name": "Sobrenome",
        }

    def clean_email(self):
        """Validacao de UM campo especifico.

        O Django chama automaticamente todo metodo chamado
        clean_<nome_do_campo>. Ele recebe o valor ja convertido e deve
        DEVOLVER o valor (possivelmente corrigido) ou levantar
        ValidationError.

        O `unique=True` do modelo ja barraria o e-mail repetido no
        banco, mas com uma mensagem tecnica. Aqui barramos antes, com
        uma mensagem que o usuario entende -- e normalizamos para
        minusculas, para que Joao@x.com e joao@x.com nao criem duas
        contas diferentes.
        """
        email = self.cleaned_data["email"].strip().lower()

        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ja existe um usuario com este e-mail.")

        return email


class UsuarioEditarForm(BootstrapMixin, forms.ModelForm):
    """Edicao de um usuario existente.

    Por que um form separado, em vez de reaproveitar o de criacao?
    Porque editar NAO deve pedir senha. Se os campos de senha
    estivessem aqui, quem quisesse so corrigir um sobrenome seria
    obrigado a redigitar a senha -- ou pior, a senha seria apagada.
    Trocar senha e uma operacao a parte.
    """

    class Meta:
        model = Usuario
        fields = ["username", "first_name", "last_name", "email", "perfil", "is_active"]
        labels = {
            "username": "Usuario (login)",
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "is_active": "Conta ativa",
        }
        help_texts = {
            "is_active": "Desmarque para bloquear o acesso sem apagar o historico.",
        }

    def clean_email(self):
        """Mesma checagem do form de criacao, com uma diferenca crucial.

        Ao EDITAR, o proprio usuario ja esta no banco com esse e-mail.
        Uma busca ingenua por "existe alguem com este e-mail?" acharia
        ele mesmo e acusaria duplicidade sempre.

        Por isso o .exclude(pk=self.instance.pk): "existe OUTRO usuario
        com este e-mail?". Em SQL seria
            WHERE email = ? AND id <> ?
        """
        email = self.cleaned_data["email"].strip().lower()

        duplicado = (
            Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
        )
        if duplicado:
            raise forms.ValidationError("Ja existe outro usuario com este e-mail.")

        return email
