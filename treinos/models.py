from datetime import date, datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from gestao.models import Aluno


class Instrutor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instrutor',
        limit_choices_to={'perfil': 'INS'}, verbose_name='usuário',
    )
    cref = models.CharField('CREF', max_length=20, unique=True)
    especialidade = models.CharField('especialidade', max_length=80, blank=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'instrutor'
        verbose_name_plural = 'instrutores'

    def __str__(self):
        return str(self.usuario)


class Modalidade(models.Model):
    nome = models.CharField('nome', max_length=60, unique=True)
    descricao = models.TextField('descrição', blank=True)

    class Meta:
        verbose_name_plural = 'modalidades'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Sala(models.Model):
    nome = models.CharField('nome', max_length=60, unique=True)
    capacidade = models.PositiveSmallIntegerField('capacidade')

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return f'{self.nome} (cap. {self.capacidade})'


class Turma(models.Model):
    class Dia(models.IntegerChoices):
        SEGUNDA = 0, 'Segunda'
        TERCA = 1, 'Terça'
        QUARTA = 2, 'Quarta'
        QUINTA = 3, 'Quinta'
        SEXTA = 4, 'Sexta'
        SABADO = 5, 'Sábado'

    modalidade = models.ForeignKey(Modalidade, on_delete=models.PROTECT, related_name='turmas')
    instrutor = models.ForeignKey(Instrutor, on_delete=models.PROTECT, related_name='turmas')
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT, related_name='turmas')
    dia_semana = models.IntegerField('dia da semana', choices=Dia.choices)
    horario_inicio = models.TimeField('início')
    horario_fim = models.TimeField('fim')
    vagas = models.PositiveSmallIntegerField('vagas')
    alunos = models.ManyToManyField(Aluno, through='InscricaoTurma', related_name='turmas', blank=True)
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        ordering = ['dia_semana', 'horario_inicio']

    @property
    def vagas_ocupadas(self):
        return self.inscricoes.count()

    @property
    def lotada(self):
        return self.vagas_ocupadas >= self.vagas

    def __str__(self):
        return f'{self.modalidade} - {self.get_dia_semana_display()} {self.horario_inicio:%H:%M}'


class InscricaoTurma(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='inscricoes')
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='inscricoes')
    data_inscricao = models.DateField('data da inscrição', default=date.today)

    class Meta:
        verbose_name = 'inscrição em turma'
        verbose_name_plural = 'inscrições em turmas'
        constraints = [models.UniqueConstraint(fields=['aluno', 'turma'], name='inscricao_unica')]

    def __str__(self):
        return f'{self.aluno} em {self.turma}'


class Equipamento(models.Model):
    class Status(models.TextChoices):
        DISPONIVEL = 'DIS', 'Disponível'
        MANUTENCAO = 'MAN', 'Em manutenção'
        INATIVO = 'INA', 'Inativo'

    nome = models.CharField('nome', max_length=80)
    marca = models.CharField('marca', max_length=60, blank=True)
    status = models.CharField('status', max_length=3, choices=Status.choices, default=Status.DISPONIVEL)
    data_aquisicao = models.DateField('data de aquisição')
    ultima_manutencao = models.DateField('última manutenção', blank=True, null=True)

    def __str__(self):
        return self.nome


class Exercicio(models.Model):
    class Grupo(models.TextChoices):
        PEITO = 'PEI', 'Peito'
        COSTAS = 'COS', 'Costas'
        PERNAS = 'PER', 'Pernas'
        OMBROS = 'OMB', 'Ombros'
        BRACOS = 'BRA', 'Braços'
        ABDOMEN = 'ABD', 'Abdômen'
        CARDIO = 'CAR', 'Cardio'

    nome = models.CharField('nome', max_length=80)
    grupo_muscular = models.CharField('grupo muscular', max_length=3, choices=Grupo.choices)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='exercicios')
    descricao = models.TextField('descrição', blank=True)

    class Meta:
        verbose_name = 'exercício'
        ordering = ['grupo_muscular', 'nome']

    def __str__(self):
        return self.nome


class FichaTreino(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='fichas')
    instrutor = models.ForeignKey(Instrutor, on_delete=models.PROTECT, related_name='fichas')
    objetivo = models.CharField('objetivo', max_length=120)
    data_inicio = models.DateField('início', default=date.today)
    data_fim = models.DateField('fim', blank=True, null=True)
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'ficha de treino'
        verbose_name_plural = 'fichas de treino'
        ordering = ['-data_inicio']

    def __str__(self):
        return f'Ficha de {self.aluno} ({self.data_inicio:%d/%m/%Y})'


class ItemFicha(models.Model):
    class Divisao(models.TextChoices):
        A = 'A', 'Treino A'
        B = 'B', 'Treino B'
        C = 'C', 'Treino C'
        D = 'D', 'Treino D'

    ficha = models.ForeignKey(FichaTreino, on_delete=models.CASCADE, related_name='itens')
    exercicio = models.ForeignKey(Exercicio, on_delete=models.PROTECT, related_name='itens', verbose_name='exercício')
    divisao = models.CharField('divisão', max_length=1, choices=Divisao.choices, default=Divisao.A)
    series = models.PositiveSmallIntegerField('séries', default=3)
    repeticoes = models.PositiveSmallIntegerField('repetições', default=12)
    carga_kg = models.DecimalField('carga (kg)', max_digits=6, decimal_places=2, default=0)
    descanso_segundos = models.PositiveSmallIntegerField('descanso (s)', default=60)

    class Meta:
        verbose_name = 'item da ficha'
        verbose_name_plural = 'itens da ficha'
        ordering = ['divisao', 'id']

    def __str__(self):
        return f'{self.get_divisao_display()}: {self.exercicio} {self.series}x{self.repeticoes}'


class AvaliacaoFisica(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='avaliacoes')
    instrutor = models.ForeignKey(Instrutor, on_delete=models.PROTECT, related_name='avaliacoes')
    data = models.DateField('data', default=date.today)
    peso_kg = models.DecimalField('peso (kg)', max_digits=5, decimal_places=2)
    altura_m = models.DecimalField('altura (m)', max_digits=3, decimal_places=2)
    percentual_gordura = models.DecimalField('% de gordura', max_digits=4, decimal_places=1, blank=True, null=True)
    observacoes = models.TextField('observações', blank=True)

    class Meta:
        verbose_name = 'avaliação física'
        verbose_name_plural = 'avaliações físicas'
        ordering = ['-data']

    @property
    def imc(self):
        return round(float(self.peso_kg) / (float(self.altura_m) ** 2), 1)

    @property
    def classificacao_imc(self):
        v = self.imc
        if v < 18.5:
            return 'Abaixo do peso'
        if v < 25:
            return 'Peso normal'
        if v < 30:
            return 'Sobrepeso'
        return 'Obesidade'

    def __str__(self):
        return f'Avaliação de {self.aluno} em {self.data:%d/%m/%Y}'


class Frequencia(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='frequencias')
    entrada = models.DateTimeField('entrada', default=timezone.now)
    saida = models.DateTimeField('saída', blank=True, null=True)

    class Meta:
        verbose_name = 'frequência'
        ordering = ['-entrada']

    @property
    def duracao(self):
        if self.saida:
            return self.saida - self.entrada
        return None

    def __str__(self):
        return f'{self.aluno} - {timezone.localtime(self.entrada):%d/%m/%Y %H:%M}'
