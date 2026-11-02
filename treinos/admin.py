from datetime import timedelta

from django.contrib import admin
from django.db.models import Count, F
from django.utils import timezone

from .models import (AvaliacaoFisica, Equipamento, Exercicio, FichaTreino, Frequencia,
                     InscricaoTurma, Instrutor, ItemFicha, Modalidade, Sala, Turma)


class LotacaoFilter(admin.SimpleListFilter):
    title = 'lotação'
    parameter_name = 'lotacao'

    def lookups(self, request, model_admin):
        return [('lotada', 'Turmas lotadas'), ('vagas', 'Com vagas')]

    def queryset(self, request, queryset):
        qs = queryset.annotate(ocupadas=Count('inscricoes'))
        if self.value() == 'lotada':
            return qs.filter(ocupadas__gte=F('vagas'))
        if self.value() == 'vagas':
            return qs.filter(ocupadas__lt=F('vagas'))
        return queryset


class ManutencaoFilter(admin.SimpleListFilter):
    title = 'manutenção'
    parameter_name = 'manut'

    def lookups(self, request, model_admin):
        return [('atrasada', 'Revisão há mais de 180 dias'), ('nunca', 'Nunca revisado')]

    def queryset(self, request, queryset):
        limite = timezone.localdate() - timedelta(days=180)
        if self.value() == 'atrasada':
            return queryset.filter(ultima_manutencao__lt=limite)
        if self.value() == 'nunca':
            return queryset.filter(ultima_manutencao__isnull=True)
        return queryset


class ImcFilter(admin.SimpleListFilter):
    title = 'classificação IMC'
    parameter_name = 'imc'

    def lookups(self, request, model_admin):
        return [('baixo', 'Abaixo do peso'), ('normal', 'Peso normal'), ('sobre', 'Sobrepeso'), ('obeso', 'Obesidade')]

    def queryset(self, request, queryset):
        qs = queryset.annotate(imc_calc=F('peso_kg') / (F('altura_m') * F('altura_m')))
        v = self.value()
        if v == 'baixo':
            return qs.filter(imc_calc__lt=18.5)
        if v == 'normal':
            return qs.filter(imc_calc__gte=18.5, imc_calc__lt=25)
        if v == 'sobre':
            return qs.filter(imc_calc__gte=25, imc_calc__lt=30)
        if v == 'obeso':
            return qs.filter(imc_calc__gte=30)
        return queryset


class ItemFichaInline(admin.TabularInline):
    model = ItemFicha
    extra = 1
    autocomplete_fields = ('exercicio',)


class InscricaoInline(admin.TabularInline):
    model = InscricaoTurma
    extra = 0
    autocomplete_fields = ('aluno',)


@admin.register(Instrutor)
class InstrutorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'cref', 'especialidade', 'ativo')
    list_filter = ('ativo', 'especialidade')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'cref')


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    search_fields = ('nome',)


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'capacidade')
    list_filter = ('capacidade',)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'instrutor', 'sala', 'vagas', 'vagas_ocupadas', 'lotada', 'ativa')
    list_filter = ('ativa', 'modalidade', 'dia_semana', 'instrutor', 'sala', LotacaoFilter)
    search_fields = ('modalidade__nome', 'instrutor__usuario__first_name')
    inlines = [InscricaoInline]

    @admin.display(boolean=True, description='Lotada')
    def lotada(self, obj):
        return obj.lotada


@admin.register(InscricaoTurma)
class InscricaoTurmaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'turma', 'data_inscricao')
    list_filter = ('turma__modalidade', 'data_inscricao')
    date_hierarchy = 'data_inscricao'
    search_fields = ('aluno__usuario__first_name', 'aluno__usuario__last_name')


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'status', 'data_aquisicao', 'ultima_manutencao')
    list_filter = ('status', ManutencaoFilter, 'marca', 'data_aquisicao')
    search_fields = ('nome', 'marca')
    date_hierarchy = 'data_aquisicao'
    actions = ['enviar_manutencao', 'liberar_equipamento']

    @admin.action(description='Enviar para manutenção')
    def enviar_manutencao(self, request, queryset):
        queryset.update(status=Equipamento.Status.MANUTENCAO)

    @admin.action(description='Liberar (manutenção concluída hoje)')
    def liberar_equipamento(self, request, queryset):
        queryset.update(status=Equipamento.Status.DISPONIVEL, ultima_manutencao=timezone.localdate())


@admin.register(Exercicio)
class ExercicioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'grupo_muscular', 'equipamento')
    list_filter = ('grupo_muscular', 'equipamento')
    search_fields = ('nome',)


@admin.register(FichaTreino)
class FichaTreinoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'instrutor', 'objetivo', 'data_inicio', 'ativa')
    list_filter = ('ativa', 'instrutor', 'data_inicio')
    search_fields = ('aluno__usuario__first_name', 'aluno__usuario__last_name', 'objetivo')
    date_hierarchy = 'data_inicio'
    inlines = [ItemFichaInline]


@admin.register(ItemFicha)
class ItemFichaAdmin(admin.ModelAdmin):
    list_display = ('ficha', 'divisao', 'exercicio', 'series', 'repeticoes', 'carga_kg')
    list_filter = ('divisao', 'exercicio__grupo_muscular')
    search_fields = ('exercicio__nome',)


@admin.register(AvaliacaoFisica)
class AvaliacaoFisicaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'data', 'peso_kg', 'altura_m', 'imc', 'classificacao_imc', 'percentual_gordura')
    list_filter = ('instrutor', ImcFilter, 'data')
    search_fields = ('aluno__usuario__first_name', 'aluno__usuario__last_name')
    date_hierarchy = 'data'


@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'entrada', 'saida', 'duracao')
    list_filter = ('entrada',)
    search_fields = ('aluno__usuario__first_name', 'aluno__usuario__last_name')
    date_hierarchy = 'entrada'
