from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def perfil_required(*perfis):
    """Exige login e que o usuário tenha um dos perfis informados."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.perfil not in perfis:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return login_required(wrapper)
    return decorator
