from django.core.management.base import BaseCommand

from accounts.permissoes import configurar_grupos


class Command(BaseCommand):
    help = 'Cria os grupos Recepção e Instrutores com suas permissões.'

    def handle(self, *args, **opts):
        configurar_grupos()
        self.stdout.write(self.style.SUCCESS('Grupos de permissão configurados.'))
