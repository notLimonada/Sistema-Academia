import calendar
from datetime import date

from django.conf import settings
from django.db import models
from django.utils import timezone


def somar_meses(data, meses):
    """Soma meses a uma data, ajustando o dia quando necessário."""
    mes_total = data.month - 1 + meses
    ano = data.year + mes_total // 12
    mes = mes_total % 12 + 1
    dia = min(data.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


class Aluno(models.Model):
    class Objetivo(models.TextChoices):
        EMAGRECIMENTO = 'EMA', 'Emagrecimento'
        HIPERTROFIA = 'HIP', 'Hipertrofia'
        CONDICIONAMENTO = 'CON', 'Condicionamento físico'
        SAUDE = 'SAU', 'Saúde e bem-estar'
        REABILITACAO = 'REA', 'Reabilitação'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='aluno',
        limit_choices_to={'perfil': 'ALU'}, verbose_name='usuário',
    )
    data_nascimento = models.DateField('data de nascimento')
    objetivo = models.CharField('objetivo', max_length=3, choices=Objetivo.choices, default=Objetivo.SAUDE)
    restricoes_medicas = models.TextField('restrições médicas', blank=True)
    contato_emergencia = models.CharField('contato de emergência', max_length=100, blank=True)
    ativo = models.BooleanField('ativo', default=True)
    data_cadastro = models.DateTimeField('data de cadastro', auto_now_add=True)

    class Meta:
        ordering = ['usuario__first_name', 'usuario__username']

    @property
    def idade(self):
        hoje = date.today()
        n = self.data_nascimento
        return hoje.year - n.year - ((hoje.month, hoje.day) < (n.month, n.day))

    def __str__(self):
        return str(self.usuario)


class Plano(models.Model):
    nome = models.CharField('nome', max_length=60, unique=True)
    valor = models.DecimalField('valor mensal (R$)', max_digits=8, decimal_places=2)
    duracao_meses = models.PositiveSmallIntegerField('duração (meses)', default=1)
    descricao = models.TextField('descrição', blank=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ['valor']

    def __str__(self):
        return f'{self.nome} ({self.duracao_meses} mês(es))'


class Matricula(models.Model):
    class Status(models.TextChoices):
        ATIVA = 'ATI', 'Ativa'
        VENCIDA = 'VEN', 'Vencida'
        TRANCADA = 'TRA', 'Trancada'
        CANCELADA = 'CAN', 'Cancelada'

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='matriculas')
    plano = models.ForeignKey(Plano, on_delete=models.PROTECT, related_name='matriculas')
    data_inicio = models.DateField('início', default=date.today)
    data_fim = models.DateField('fim', blank=True, null=True, help_text='Se vazio, é calculado pela duração do plano.')
    status = models.CharField('status', max_length=3, choices=Status.choices, default=Status.ATIVA)

    class Meta:
        ordering = ['-data_inicio']
        verbose_name = 'matrícula'

    def save(self, *args, **kwargs):
        if not self.data_fim and self.plano_id:
            self.data_fim = somar_meses(self.data_inicio, self.plano.duracao_meses)
        super().save(*args, **kwargs)

    @property
    def dias_restantes(self):
        return (self.data_fim - date.today()).days if self.data_fim else None

    def __str__(self):
        return f'{self.aluno} - {self.plano.nome}'


class Pagamento(models.Model):
    class Forma(models.TextChoices):
        PIX = 'PIX', 'Pix'
        CARTAO = 'CAR', 'Cartão'
        DINHEIRO = 'DIN', 'Dinheiro'
        BOLETO = 'BOL', 'Boleto'

    class Status(models.TextChoices):
        PENDENTE = 'PEN', 'Pendente'
        PAGO = 'PAG', 'Pago'
        CANCELADO = 'CAN', 'Cancelado'

    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='pagamentos', verbose_name='matrícula')
    valor = models.DecimalField('valor (R$)', max_digits=8, decimal_places=2)
    data_vencimento = models.DateField('vencimento')
    data_pagamento = models.DateField('data do pagamento', blank=True, null=True)
    forma = models.CharField('forma', max_length=3, choices=Forma.choices, blank=True)
    status = models.CharField('status', max_length=3, choices=Status.choices, default=Status.PENDENTE)

    class Meta:
        ordering = ['-data_vencimento']

    @property
    def em_atraso(self):
        return self.status == self.Status.PENDENTE and self.data_vencimento < timezone.localdate()

    def __str__(self):
        return f'{self.matricula.aluno} - R$ {self.valor} ({self.data_vencimento:%d/%m/%Y})'
