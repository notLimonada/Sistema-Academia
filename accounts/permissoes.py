"""Grupos de permissão ligados aos perfis de usuário."""
from django.contrib.auth.models import Group, Permission

GRUPO_POR_PERFIL = {
    'REC': 'Recepção',
    'INS': 'Instrutores',
}

# v = ver, a = adicionar, c = alterar, d = excluir
PERMISSOES = {
    'Recepção': {
        'accounts': {'usuario': 'v'},
        'gestao': {'aluno': 'vac', 'matricula': 'vac', 'pagamento': 'vac', 'plano': 'v'},
        'treinos': {'frequencia': 'vac', 'inscricaoturma': 'vac', 'turma': 'v'},
    },
    'Instrutores': {
        'gestao': {'aluno': 'v', 'matricula': 'v'},
        'treinos': {
            'fichatreino': 'vac', 'itemficha': 'vacd', 'avaliacaofisica': 'vac',
            'exercicio': 'v', 'equipamento': 'v', 'turma': 'v',
            'inscricaoturma': 'v', 'frequencia': 'v',
        },
    },
}

ACOES = {'v': 'view', 'a': 'add', 'c': 'change', 'd': 'delete'}


def configurar_grupos():
    """Cria/atualiza os grupos e associa os usuários existentes pelo perfil."""
    from .models import Usuario

    for nome, apps in PERMISSOES.items():
        grupo, _ = Group.objects.get_or_create(name=nome)
        perms = []
        for app_label, modelos in apps.items():
            for modelo, letras in modelos.items():
                for letra in letras:
                    codename = f'{ACOES[letra]}_{modelo}'
                    perms += list(Permission.objects.filter(
                        content_type__app_label=app_label, codename=codename))
        grupo.permissions.set(perms)

    for usuario in Usuario.objects.filter(perfil__in=GRUPO_POR_PERFIL.keys()):
        usuario.save()  # o signal associa o grupo e o modelo ajusta is_staff
