from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Usuario
from .permissoes import GRUPO_POR_PERFIL


@receiver(post_save, sender=Usuario)
def sincronizar_grupo(sender, instance, **kwargs):
    """Coloca o usuário no grupo correspondente ao seu perfil."""
    alvo = GRUPO_POR_PERFIL.get(instance.perfil)
    for grupo in Group.objects.filter(name__in=GRUPO_POR_PERFIL.values()):
        if grupo.name == alvo:
            instance.groups.add(grupo)
        else:
            instance.groups.remove(grupo)
