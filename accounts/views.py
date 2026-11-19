from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import CadastroForm, LoginForm
from .utils import url_inicial


class LoginPortal(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or url_inicial(self.request.user)


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect(url_inicial(request.user))


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, 'Cadastro realizado! Bem-vindo(a) à Academia Fit.')
        return redirect('home')
    return render(request, 'accounts/cadastro.html', {'form': form})
