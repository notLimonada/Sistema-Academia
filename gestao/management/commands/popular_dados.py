import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import Usuario
from gestao.models import Aluno, Matricula, Pagamento, Plano, somar_meses
from treinos.models import (AvaliacaoFisica, Equipamento, Exercicio, FichaTreino, Frequencia,
                            InscricaoTurma, Instrutor, ItemFicha, Modalidade, Sala, Turma)

NOMES = [('Ana', 'Souza'), ('Bruno', 'Lima'), ('Carla', 'Mendes'), ('Diego', 'Alves'), ('Elisa', 'Rocha'),
         ('Felipe', 'Costa'), ('Gabriela', 'Nunes'), ('Henrique', 'Pires'), ('Isabela', 'Duarte'),
         ('João', 'Ferreira'), ('Karina', 'Martins'), ('Lucas', 'Barros')]


def cpf_falso(n):
    return f'{100 + n:03d}.{200 + n:03d}.{300 + n:03d}-{n % 100:02d}'


class Command(BaseCommand):
    help = 'Popula o banco com dados de exemplo (admin / admin123).'

    @transaction.atomic
    def handle(self, *args, **opts):
        if Usuario.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Dados já existem. Apague db.sqlite3 para recriar.'))
            return
        random.seed(7)
        hoje = timezone.localdate()

        Usuario.objects.create_superuser('admin', 'admin@academia.com', 'admin123',
                                         first_name='Administrador', perfil='ADM')
        rec = Usuario.objects.create_user('recepcao', 'rec@academia.com', 'senha123', first_name='Marta',
                                          last_name='Recepção', perfil='REC', is_staff=True)

        planos = [Plano.objects.create(nome=n, valor=Decimal(v), duracao_meses=d, descricao=desc)
                  for n, v, d, desc in [
                      ('Mensal', '119.90', 1, 'Acesso livre à musculação.'),
                      ('Trimestral', '99.90', 3, 'Musculação + aulas coletivas.'),
                      ('Semestral', '89.90', 6, 'Musculação + aulas + avaliação física.'),
                      ('Anual', '79.90', 12, 'Todos os benefícios, melhor preço.')]]

        modalidades = [Modalidade.objects.create(nome=n) for n in
                       ['Musculação', 'Spinning', 'Yoga', 'Funcional', 'Pilates']]
        salas = [Sala.objects.create(nome=n, capacidade=c) for n, c in
                 [('Sala Coletiva', 20), ('Studio Spinning', 12), ('Studio Zen', 10)]]

        instrutores = []
        for i, (nome, sob, esp) in enumerate([('Rafael', 'Teixeira', 'Musculação'),
                                              ('Patrícia', 'Gomes', 'Yoga e Pilates'),
                                              ('Thiago', 'Ribeiro', 'Funcional e Spinning')]):
            u = Usuario.objects.create_user(f'instrutor{i+1}', f'i{i+1}@academia.com', 'senha123',
                                            first_name=nome, last_name=sob, perfil='INS', is_staff=True,
                                            cpf=cpf_falso(50 + i))
            instrutores.append(Instrutor.objects.create(usuario=u, cref=f'00{i+1}234-G/MG', especialidade=esp))

        turmas = []
        horarios = [(time(7), time(8)), (time(18), time(19)), (time(19), time(20))]
        for i in range(8):
            ini, fim = horarios[i % 3]
            turmas.append(Turma.objects.create(
                modalidade=modalidades[1 + i % 4], instrutor=instrutores[i % 3], sala=salas[i % 3],
                dia_semana=i % 6, horario_inicio=ini, horario_fim=fim, vagas=random.choice([3, 5, 10])))

        equipamentos = []
        for nome, marca, status, anos, manut in [
                ('Supino reto', 'Technogym', 'DIS', 4, 40), ('Leg press 45', 'Life Fitness', 'DIS', 3, 200),
                ('Esteira 01', 'Movement', 'MAN', 2, 10), ('Bicicleta ergométrica', 'Movement', 'DIS', 2, None),
                ('Puxador alto', 'Technogym', 'DIS', 5, 220), ('Cadeira extensora', 'Life Fitness', 'DIS', 3, 90)]:
            equipamentos.append(Equipamento.objects.create(
                nome=nome, marca=marca, status=status, data_aquisicao=hoje - timedelta(days=365 * anos),
                ultima_manutencao=hoje - timedelta(days=manut) if manut else None))

        exercicios = [Exercicio.objects.create(nome=n, grupo_muscular=g, equipamento=equipamentos[e] if e is not None else None)
                      for n, g, e in [('Supino reto', 'PEI', 0), ('Leg press', 'PER', 1), ('Corrida na esteira', 'CAR', 2),
                                      ('Remada alta', 'COS', 4), ('Extensão de pernas', 'PER', 5),
                                      ('Rosca direta', 'BRA', None), ('Desenvolvimento', 'OMB', None),
                                      ('Abdominal prancha', 'ABD', None)]]

        status_mat = ['ATI'] * 8 + ['VEN', 'TRA', 'CAN', 'ATI']
        objetivos = [c[0] for c in Aluno.Objetivo.choices]
        for i, (nome, sob) in enumerate(NOMES):
            u = Usuario.objects.create_user(f'aluno{i+1}', f'aluno{i+1}@email.com', 'senha123',
                                            first_name=nome, last_name=sob, perfil='ALU',
                                            cpf=cpf_falso(i), telefone=f'(35) 9{random.randint(8000,9999)}-{random.randint(1000,9999)}')
            aluno = Aluno.objects.create(usuario=u, data_nascimento=date(1970 + random.randint(0, 38), random.randint(1, 12), random.randint(1, 28)),
                                         objetivo=random.choice(objetivos), ativo=status_mat[i] != 'CAN',
                                         restricoes_medicas='Hipertensão controlada.' if i % 5 == 0 else '')
            plano = planos[i % 4]
            inicio = hoje - timedelta(days=random.randint(10, 200))
            if status_mat[i] == 'VEN':
                inicio = hoje - timedelta(days=plano.duracao_meses * 30 + 20)
            if i in (1, 5):  # vencem em breve
                inicio = somar_meses(hoje, -plano.duracao_meses) + timedelta(days=12)
            mat = Matricula.objects.create(aluno=aluno, plano=plano, data_inicio=inicio, status=status_mat[i])

            # pagamentos mensais
            for m in range(min(plano.duracao_meses, 4)):
                venc = somar_meses(inicio, m)
                if venc <= hoje - timedelta(days=5) and not (i % 4 == 3 and m == 0 and False):
                    pago = not (i % 4 == 2 and venc >= hoje - timedelta(days=45))  # alguns inadimplentes
                    Pagamento.objects.create(
                        matricula=mat, valor=plano.valor, data_vencimento=venc,
                        data_pagamento=venc if pago else None, forma=random.choice(['PIX', 'CAR', 'DIN']) if pago else '',
                        status='PAG' if pago else 'PEN')
                else:
                    Pagamento.objects.create(matricula=mat, valor=plano.valor, data_vencimento=venc)

            instrutor = instrutores[i % 3]
            ficha = FichaTreino.objects.create(aluno=aluno, instrutor=instrutor, objetivo=aluno.get_objetivo_display(),
                                               data_inicio=hoje - timedelta(days=30))
            for div in ['A', 'B']:
                for ex in random.sample(exercicios, 3):
                    ItemFicha.objects.create(ficha=ficha, exercicio=ex, divisao=div, series=random.choice([3, 4]),
                                             repeticoes=random.choice([8, 10, 12, 15]),
                                             carga_kg=Decimal(random.choice([0, 10, 20, 30, 40])))
            for k in range(2):
                AvaliacaoFisica.objects.create(
                    aluno=aluno, instrutor=instrutor, data=hoje - timedelta(days=90 * k + 5),
                    peso_kg=Decimal(random.randint(55, 105)), altura_m=Decimal(f'1.{random.randint(55, 90)}'),
                    percentual_gordura=Decimal(random.randint(10, 35)))
            for d in range(random.randint(4, 12)):
                ent = timezone.make_aware(datetime.combine(hoje - timedelta(days=d * 2 + 1), time(random.randint(6, 20), 0)))
                Frequencia.objects.create(aluno=aluno, entrada=ent, saida=ent + timedelta(minutes=random.randint(40, 110)))
            for t in random.sample(turmas, 3):
                if not t.lotada:
                    InscricaoTurma.objects.create(aluno=aluno, turma=t)

        self.stdout.write(self.style.SUCCESS(
            'Dados criados. Login: admin / admin123 (alunos e instrutores: senha123).'))
