from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import perfil_required
from accounts.models import Usuario
from gestao.models import Pagamento
from treinos.models import InscricaoTurma, Turma

ALUNO = Usuario.Perfil.ALUNO
INSTRUTOR = Usuario.Perfil.INSTRUTOR


def _aluno(request):
    """Aluno ligado ao usuário logado (ou None se o cadastro estiver incompleto)."""
    return getattr(request.user, 'aluno', None)


def _matricula_vigente(aluno):
    hoje = timezone.localdate()
    return (aluno.matriculas.filter(status='ATI')
            .filter(Q(data_fim__gte=hoje) | Q(data_fim__isnull=True))
            .select_related('plano').order_by('-data_inicio').first())


def _sem_cadastro(request):
    return render(request, 'portal/sem_cadastro.html', status=200)


# ---------------------------------------------------------------- ALUNO
@perfil_required(ALUNO)
def aluno_home(request):
    aluno = _aluno(request)
    if aluno is None:
        return _sem_cadastro(request)
    pagamentos = list(Pagamento.objects.filter(matricula__aluno=aluno)
                      .select_related('matricula__plano').order_by('-data_vencimento')[:10])
    proximo = (Pagamento.objects.filter(matricula__aluno=aluno, status=Pagamento.Status.PENDENTE)
               .order_by('data_vencimento').first())
    contexto = {
        'aluno': aluno,
        'matricula': _matricula_vigente(aluno),
        'pagamentos': pagamentos,
        'proximo': proximo,
        'frequencias': aluno.frequencias.all()[:5],
        'turmas': aluno.turmas.select_related('modalidade', 'sala', 'instrutor__usuario'),
    }
    return render(request, 'portal/aluno_home.html', contexto)


@perfil_required(ALUNO)
def aluno_ficha(request):
    aluno = _aluno(request)
    if aluno is None:
        return _sem_cadastro(request)
    ficha = (aluno.fichas.filter(ativa=True).select_related('instrutor__usuario')
             .prefetch_related('itens__exercicio').first())
    grupos = {}
    if ficha:
        for item in ficha.itens.all():
            grupos.setdefault(item.get_divisao_display(), []).append(item)
    return render(request, 'portal/aluno_ficha.html', {'ficha': ficha, 'grupos': list(grupos.items())})


@perfil_required(ALUNO)
def aluno_avaliacoes(request):
    aluno = _aluno(request)
    if aluno is None:
        return _sem_cadastro(request)
    avaliacoes = aluno.avaliacoes.select_related('instrutor__usuario')
    return render(request, 'portal/aluno_avaliacoes.html', {'avaliacoes': avaliacoes})


@perfil_required(ALUNO)
def aluno_turmas(request):
    aluno = _aluno(request)
    if aluno is None:
        return _sem_cadastro(request)
    turmas = (Turma.objects.filter(ativa=True)
              .select_related('modalidade', 'sala', 'instrutor__usuario')
              .annotate(ocupadas=Count('inscricoes')))
    inscritas = set(aluno.inscricoes.values_list('turma_id', flat=True))
    return render(request, 'portal/aluno_turmas.html', {
        'turmas': turmas, 'inscritas': inscritas, 'matricula': _matricula_vigente(aluno)})


@require_POST
@perfil_required(ALUNO)
def turma_alternar(request, pk):
    """Inscreve ou cancela a inscrição do aluno em uma turma (chamada via AJAX)."""
    aluno = _aluno(request)
    if aluno is None:
        return JsonResponse({'ok': False, 'msg': 'Cadastro de aluno incompleto.'}, status=400)
    with transaction.atomic():
        turma = get_object_or_404(Turma.objects.select_for_update(), pk=pk, ativa=True)
        inscricao = InscricaoTurma.objects.filter(aluno=aluno, turma=turma).first()
        if inscricao:
            inscricao.delete()
            inscrito, msg = False, 'Inscrição cancelada.'
        else:
            if _matricula_vigente(aluno) is None:
                return JsonResponse({'ok': False, 'msg': 'Você precisa de uma matrícula ativa para se inscrever.'}, status=400)
            if turma.lotada:
                return JsonResponse({'ok': False, 'msg': 'Esta turma está lotada.'}, status=400)
            InscricaoTurma.objects.create(aluno=aluno, turma=turma)
            inscrito, msg = True, 'Inscrição realizada!'
        ocupadas = turma.inscricoes.count()
    return JsonResponse({'ok': True, 'inscrito': inscrito, 'ocupadas': ocupadas,
                         'vagas': turma.vagas, 'msg': msg})


# ------------------------------------------------------------- INSTRUTOR
@perfil_required(INSTRUTOR)
def instrutor_home(request):
    instrutor = getattr(request.user, 'instrutor', None)
    if instrutor is None:
        return _sem_cadastro(request)
    turmas = (instrutor.turmas.filter(ativa=True)
              .select_related('modalidade', 'sala')
              .prefetch_related('inscricoes__aluno__usuario'))
    fichas = (instrutor.fichas.filter(ativa=True).select_related('aluno__usuario')[:10])
    total_alunos = (InscricaoTurma.objects.filter(turma__instrutor=instrutor)
                    .values('aluno').distinct().count())
    return render(request, 'portal/instrutor_home.html', {
        'instrutor': instrutor, 'turmas': turmas, 'fichas': fichas,
        'total_alunos': total_alunos, 'total_fichas': instrutor.fichas.filter(ativa=True).count()})
