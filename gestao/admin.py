from datetime import timedelta

from django.contrib import admin, messages
from django.utils import timezone

from .models import Aluno, Matricula, Pagamento, Plano, somar_meses


class MatriculaInline(admin.TabularInline):
    model = Matricula
    extra = 0
    fields = ('plano', 'data_inicio', 'data_fim', 'status')


class VencimentoProximoFilter(admin.SimpleListFilter):
    title = 'vencimento da matrícula'
    parameter_name = 'vencimento'

    def lookups(self, request, model_admin):
        return [('7', 'Próximos 7 dias'), ('30', 'Próximos 30 dias'), ('vencidas', 'Já vencidas')]

    def queryset(self, request, queryset):
        hoje = timezone.localdate()
        v = self.value()
        if v in ('7', '30'):
            return queryset.filter(status=Matricula.Status.ATIVA, data_fim__range=(hoje, hoje + timedelta(days=int(v))))
        if v == 'vencidas':
            return queryset.filter(data_fim__lt=hoje).exclude(status=Matricula.Status.CANCELADA)
        return queryset


class InadimplenciaFilter(admin.SimpleListFilter):
    title = 'situação de cobrança'
    parameter_name = 'cobranca'

    def lookups(self, request, model_admin):
        return [('atraso', 'Em atraso'), ('a_vencer', 'A vencer (pendentes)'), ('quitados', 'Quitados')]

    def queryset(self, request, queryset):
        hoje = timezone.localdate()
        v = self.value()
        if v == 'atraso':
            return queryset.filter(status=Pagamento.Status.PENDENTE, data_vencimento__lt=hoje)
        if v == 'a_vencer':
            return queryset.filter(status=Pagamento.Status.PENDENTE, data_vencimento__gte=hoje)
        if v == 'quitados':
            return queryset.filter(status=Pagamento.Status.PAGO)
        return queryset


class FaixaEtariaFilter(admin.SimpleListFilter):
    title = 'faixa etária'
    parameter_name = 'faixa'

    def lookups(self, request, model_admin):
        return [('18', 'Até 17 anos'), ('18-30', '18 a 30'), ('31-50', '31 a 50'), ('51', '51 ou mais')]

    def queryset(self, request, queryset):
        hoje = timezone.localdate()
        def nasc(anos):
            return somar_meses(hoje, -12 * anos)
        v = self.value()
        if v == '18':
            return queryset.filter(data_nascimento__gt=nasc(18))
        if v == '18-30':
            return queryset.filter(data_nascimento__lte=nasc(18), data_nascimento__gt=nasc(31))
        if v == '31-50':
            return queryset.filter(data_nascimento__lte=nasc(31), data_nascimento__gt=nasc(51))
        if v == '51':
            return queryset.filter(data_nascimento__lte=nasc(51))
        return queryset


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'idade', 'objetivo', 'ativo', 'data_cadastro')
    list_filter = ('ativo', 'objetivo', FaixaEtariaFilter, 'data_cadastro')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'usuario__username', 'usuario__cpf')
    date_hierarchy = 'data_cadastro'
    autocomplete_fields = ('usuario',)
    inlines = [MatriculaInline]


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'duracao_meses', 'ativo')
    list_filter = ('ativo', 'duracao_meses')
    search_fields = ('nome', 'descricao')


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'plano', 'data_inicio', 'data_fim', 'dias_restantes', 'status')
    list_filter = ('status', 'plano', VencimentoProximoFilter, 'data_inicio')
    search_fields = ('aluno__usuario__first_name', 'aluno__usuario__last_name', 'aluno__usuario__username')
    date_hierarchy = 'data_inicio'
    list_select_related = ('aluno__usuario', 'plano')
    actions = ['renovar_matriculas', 'cancelar_matriculas']

    @admin.action(description='Renovar matrículas selecionadas (nova duração do plano)')
    def renovar_matriculas(self, request, queryset):
        for m in queryset:
            base = max(m.data_fim or timezone.localdate(), timezone.localdate())
            m.data_fim = somar_meses(base, m.plano.duracao_meses)
            m.status = Matricula.Status.ATIVA
            m.save()
        self.message_user(request, f'{queryset.count()} matrícula(s) renovada(s).', messages.SUCCESS)

    @admin.action(description='Cancelar matrículas selecionadas')
    def cancelar_matriculas(self, request, queryset):
        n = queryset.update(status=Matricula.Status.CANCELADA)
        self.message_user(request, f'{n} matrícula(s) cancelada(s).', messages.WARNING)


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'valor', 'data_vencimento', 'data_pagamento', 'forma', 'status', 'em_atraso')
    list_filter = ('status', InadimplenciaFilter, 'forma', 'data_vencimento')
    search_fields = ('matricula__aluno__usuario__first_name', 'matricula__aluno__usuario__last_name')
    date_hierarchy = 'data_vencimento'
    list_select_related = ('matricula__aluno__usuario',)
    actions = ['marcar_como_pago']

    @admin.display(boolean=True, description='Em atraso')
    def em_atraso(self, obj):
        return obj.em_atraso

    @admin.action(description='Marcar pagamentos selecionados como pagos (hoje)')
    def marcar_como_pago(self, request, queryset):
        n = queryset.filter(status=Pagamento.Status.PENDENTE).update(
            status=Pagamento.Status.PAGO, data_pagamento=timezone.localdate())
        self.message_user(request, f'{n} pagamento(s) baixado(s).', messages.SUCCESS)
