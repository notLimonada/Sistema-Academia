# Academia Fit - Sistema de Gestão de Academia

**Disciplina:** GAC116 - Programação Web (Trabalho Prático - Django)
**Integrante:** Guilherme Lima (trabalho individual)

## Descrição
Sistema web para gestão de uma academia: alunos, planos, matrículas e pagamentos, além de turmas,
instrutores, equipamentos, fichas de treino, avaliações físicas e controle de frequência.

O sistema tem **três ambientes**, conforme o perfil do usuário:

| Perfil | Onde atua |
|---|---|
| Administrador (dono) | Painel administrativo (`/admin/`), acesso total |
| Recepcionista | Painel administrativo, com permissões limitadas (grupo *Recepção*) |
| Instrutor | Área do instrutor (`/instrutor/`) e painel com permissões de treinos (grupo *Instrutores*) |
| Aluno | Área do aluno (`/aluno/`), com acesso apenas aos próprios dados |

## Tecnologias
- Python 3 e Django
- SQLite (banco relacional)
- django-jazzmin (tema do painel administrativo)
- Bootstrap 5 (CSS, responsivo, com tema claro e escuro)
- jQuery 3 (máscaras, alternância de tema e AJAX)
- Git e GitHub

## Instalação
```bash
git clone https://github.com/notLimonada/Sistema-Academia.git
cd Sistema-Academia
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py popular_dados  # dados de exemplo e grupos de permissão
```

## Execução
```bash
python manage.py runserver
```
Acesse http://127.0.0.1:8000/ (as bibliotecas Bootstrap e jQuery são carregadas por CDN, então é necessário internet).

### Usuários de exemplo
| Perfil | Usuário | Senha |
|---|---|---|
| Administrador | `admin` | `admin123` |
| Recepcionista | `recepcao` | `senha123` |
| Instrutor | `instrutor1` (a `instrutor3`) | `senha123` |
| Aluno | `aluno4` (a `aluno12`, `aluno1`...) | `senha123` |

Também é possível criar uma conta de aluno pela tela **Cadastre-se**.

## Principais funcionalidades
- **Autenticação:** login, logout e cadastro de alunos (usuário e senha), com redirecionamento por perfil.
- **Autorização:** perfis ligados a grupos de permissão do Django; telas protegidas por login e por perfil; cada aluno vê apenas os próprios dados.
- **Painel administrativo (Jazzmin):** CRUD de todas as entidades, buscas, filtros personalizados (matrículas a vencer, inadimplência, faixa etária, lotação de turmas, manutenção de equipamentos e IMC), inlines e ações em lote.
- **Área do aluno:** matrícula e próximo pagamento, histórico de pagamentos, ficha de treino, avaliações físicas, frequência e inscrição/cancelamento em turmas (AJAX).
- **Área do instrutor:** turmas e alunos inscritos, fichas de treino ativas e atalho para criar/editar fichas.
- **Interface:** Bootstrap, responsiva, com alternância entre tema claro e escuro (salva no navegador).

## Estrutura do projeto
```
Sistema-Academia/
├── config/        # settings e urls do projeto
├── accounts/      # Usuario (perfis), login, logout, cadastro, grupos de permissão
├── gestao/        # Aluno, Plano, Matricula, Pagamento (+ comando popular_dados)
├── treinos/       # Instrutor, Modalidade, Sala, Turma, InscricaoTurma, Equipamento,
│                  # Exercicio, FichaTreino, ItemFicha, AvaliacaoFisica, Frequencia
├── portal/        # Áreas do aluno e do instrutor (views e rotas)
├── templates/     # base.html (Bootstrap), login, cadastro e telas do portal
├── static/        # css/app.css e js/app.js (jQuery)
├── docs/DER.md    # Diagrama entidade-relacionamento
└── manage.py
```

## Fluxo de Git
Branches `main` (estável), `develop` (integração) e `feature/...` (desenvolvimento), com merges via Pull Request.
