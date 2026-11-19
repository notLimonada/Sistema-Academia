from django.urls import reverse

from .models import Usuario


def url_inicial(user):
    """Tela inicial de cada perfil após o login."""
    if user.is_superuser or user.perfil in (Usuario.Perfil.ADMINISTRADOR, Usuario.Perfil.RECEPCIONISTA):
        return reverse('admin:index')
    if user.perfil == Usuario.Perfil.INSTRUTOR:
        return reverse('portal:instrutor_home')
    return reverse('portal:aluno_home')
