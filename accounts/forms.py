import re
from datetime import date

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from gestao.models import Aluno

from .models import Usuario


def estilizar(form):
    """Aplica classes do Bootstrap a todos os campos."""
    for campo in form.fields.values():
        w = campo.widget
        if isinstance(w, forms.Select):
            classe = 'form-select'
        elif isinstance(w, forms.CheckboxInput):
            classe = 'form-check-input'
        else:
            classe = 'form-control'
        w.attrs['class'] = f"{w.attrs.get('class', '')} {classe}".strip()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['autofocus'] = True
        estilizar(self)


class CadastroForm(UserCreationForm):
    cpf = forms.CharField(label='CPF', max_length=14, widget=forms.TextInput(
        attrs={'class': 'mask-cpf', 'placeholder': '000.000.000-00', 'inputmode': 'numeric'}))
    telefone = forms.CharField(label='Telefone', max_length=20, widget=forms.TextInput(
        attrs={'class': 'mask-tel', 'placeholder': '(00) 00000-0000', 'inputmode': 'numeric'}))
    data_nascimento = forms.DateField(label='Data de nascimento', widget=forms.DateInput(
        attrs={'type': 'date'}, format='%Y-%m-%d'))
    objetivo = forms.ChoiceField(label='Objetivo', choices=Aluno.Objetivo.choices)

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome in ('first_name', 'last_name', 'email'):
            self.fields[nome].required = True
        estilizar(self)

    def clean_cpf(self):
        digitos = re.sub(r'\D', '', self.cleaned_data['cpf'])
        if len(digitos) != 11:
            raise forms.ValidationError('Informe um CPF com 11 dígitos.')
        formatado = f'{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}'
        if Usuario.objects.filter(cpf=formatado).exists():
            raise forms.ValidationError('Este CPF já está cadastrado.')
        return formatado

    def clean_data_nascimento(self):
        data = self.cleaned_data['data_nascimento']
        if data >= date.today() or data.year < 1900:
            raise forms.ValidationError('Informe uma data de nascimento válida.')
        return data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.perfil = Usuario.Perfil.ALUNO
        usuario.cpf = self.cleaned_data['cpf']
        usuario.telefone = self.cleaned_data['telefone']
        with transaction.atomic():
            usuario.save()
            Aluno.objects.create(
                usuario=usuario,
                data_nascimento=self.cleaned_data['data_nascimento'],
                objetivo=self.cleaned_data['objetivo'],
            )
        return usuario
