"""GABARITO -- academico/forms.py resolvido."""

from django import forms

from .models import Aluno, Disciplina, Inscricao


class BootstrapMixin:
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
    class Meta:
        model = Aluno
        fields = ["matricula", "nome", "email", "data_nascimento", "ativo"]
        widgets = {
            "data_nascimento": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def clean_matricula(self):
        matricula = self.cleaned_data["matricula"].strip().upper()
        if len(matricula) < 4:
            raise forms.ValidationError("A matricula deve ter ao menos 4 caracteres.")
        return matricula


class DisciplinaForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ["codigo", "nome", "carga_horaria", "periodo"]

    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip().upper()

    def clean_carga_horaria(self):
        valor = self.cleaned_data["carga_horaria"]
        if valor <= 0:
            raise forms.ValidationError("A carga horaria deve ser maior que zero.")
        return valor


class InscricaoForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ["aluno", "disciplina", "nota1", "nota2"]
        error_messages = {
            forms.models.NON_FIELD_ERRORS: {
                "unique_together": "Este aluno ja esta inscrito nesta disciplina.",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # So aluno ativo aparece no <select>.
        self.fields["aluno"].queryset = Aluno.objects.filter(ativo=True)
