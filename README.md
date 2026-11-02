# Academia Fit - Sistema de Gestão de Academia

**Disciplina:** GAC116 - Programação Web (Trabalho Prático - Django)
**Integrante:** Guilherme Lima (trabalho individual)

## Descrição
Sistema web para gestão de uma academia: cadastro de alunos, planos, matrículas e pagamentos,
além de turmas, instrutores, equipamentos, fichas de treino, avaliações físicas e controle de frequência.
Possui perfis de usuário (Administrador, Recepcionista, Instrutor e Aluno).

> Estado atual: **Checkpoint 1** (modelagem + ambiente administrativo). A área do usuário final
> (login, cadastro, tema claro/escuro, jQuery) será entregue no Checkpoint 2.

## Tecnologias
- Python 3 / Django
- SQLite (banco relacional)
- django-jazzmin (tema do ambiente administrativo)
- Frontend (Checkpoint 2): Bootstrap + jQuery

## Instalação
```bash
git clone <url-do-repositorio>
cd academia
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py popular_dados  # dados de exemplo
```

## Execução
```bash
python manage.py runserver
```
Acesse http://127.0.0.1:8000/admin/ — usuário `admin`, senha `admin123`.
(Instrutores, recepção e alunos de exemplo usam a senha `senha123`.)

## Principais funcionalidades (Checkpoint 1)
- Modelagem com 16 tabelas (FK, 1:1 e M2M com tabela intermediária)
- Usuário customizado com perfis
- Admin com tema Jazzmin, `list_display`, busca, `date_hierarchy` e inlines
- Filtros customizados: matrículas a vencer, inadimplência, faixa etária, turmas lotadas,
  manutenção de equipamentos e classificação de IMC
- Ações em lote: renovar/cancelar matrículas, baixar pagamentos, enviar equipamento para manutenção

## Estrutura do projeto
```
academia/
├── config/      # settings, urls
├── accounts/    # Usuario (AbstractUser + perfil)
├── gestao/      # Aluno, Plano, Matricula, Pagamento (+ comando popular_dados)
├── treinos/     # Instrutor, Modalidade, Sala, Turma, InscricaoTurma, Equipamento,
│                # Exercicio, FichaTreino, ItemFicha, AvaliacaoFisica, Frequencia
├── docs/DER.md  # Diagrama entidade-relacionamento
└── manage.py
```
