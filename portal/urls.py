from django.urls import path

from . import views

app_name = 'portal'

urlpatterns = [
    path('aluno/', views.aluno_home, name='aluno_home'),
    path('aluno/ficha/', views.aluno_ficha, name='aluno_ficha'),
    path('aluno/avaliacoes/', views.aluno_avaliacoes, name='aluno_avaliacoes'),
    path('aluno/turmas/', views.aluno_turmas, name='aluno_turmas'),
    path('aluno/turmas/<int:pk>/alternar/', views.turma_alternar, name='turma_alternar'),
    path('instrutor/', views.instrutor_home, name='instrutor_home'),
]
