import textwrap
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

URL_DB = 'postgresql://postgres:postgres@localhost:5432/desafio_dio_db'
engine = create_engine(URL_DB, echo=False)
Session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass


class Cliente(Base):
    __tablename__ = 'cliente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255))
    endereço = Column(String(255))
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'cliente',
        'polymorphic_on': type
    }


class PessoaFisica(Cliente):
    __tablename__ = 'pessoa_fisica'

    id = Column(Integer, ForeignKey('cliente.id'), primary_key=True)
    cpf = Column(String(11), unique=True)
    data_nascimento = Column(String(12))

    __mapper_args__ = {
        'polymorphic_identity': 'pessoa_fisica',
    }


class PessoaJuridica(Cliente):
    __tablename__ = 'pessoa_juridica'

    id = Column(Integer, ForeignKey('cliente.id'), primary_key=True)
    cnpj = Column(String(14), unique=True)

    __mapper_args__ = {
        'polymorphic_identity': 'pessoa_juridica',
    }


class Conta(Base):

    __tablename__ = 'conta'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey('cliente.id'))
    tipo = Column(Enum('corrente', 'poupança', name='tipo_conta'))
    agencia = Column(Integer)
    saldo = Column(Float)


class Transacao(Base):
    __tablename__ = 'transacao'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_conta = Column(Integer, ForeignKey('conta.id'))
    data = Column(DateTime)
    valor = Column(Float)
    tipo = Column(Enum('deposito', 'saque', name='tipo_transacao'))

Base.metadata.create_all(engine)

def criar_cliente():
    session = Session()

    try:
        while True:
            tipo_cliente = input('Digite o tipo de cliente (f/j): ').strip().lower()
            
            if tipo_cliente == 'f':
                nome = input(str('Digite o nome do cliente: '))
                endereço = input('Digite o endereço: ')
                cpf = input('Digite o CPF: ')
                data_nascimento = input('Digite a data de nascimento: ')
                novo_cliente = PessoaFisica(nome=nome, endereço=endereço, cpf=cpf, data_nascimento=data_nascimento)
                session.add(novo_cliente)
                session.commit()
                print('Cliente PF adicionado com sucesso!')
                break

            elif tipo_cliente == 'j':
                nome = input(str('Digite o nome do cliente: '))
                endereço = input('Digite o endereço: ')
                cnpj = input('Digite o CNPJ: ')
                novo_cliente = PessoaJuridica(nome=nome, endereço=endereço, cnpj=cnpj)
                session.add(novo_cliente)
                session.commit()
                print('Cliente PJ adicionado com sucesso!')
                break

            else:
                print('Digite um tipo válido "f" ou "j": ')
    except IntegrityError:
        session.rollback()
        print('Erro: CPF ou CNPJ já cadastrado!')


def exibir_dados(cliente):
    print('*'*80)
    print(f'ID Cliente: {cliente.id}')
    print(f'Nome: {cliente.nome}')
    print(f'Endereço: {cliente.endereço}')

    if isinstance(cliente, PessoaFisica):
        print(f'CPF: {cliente.cpf}')
        print(f'Data de Nascimento: {cliente.data_nascimento}')
    elif isinstance(cliente, PessoaJuridica):
        print(f'CNPJ: {cliente.cnpj}')

    print('*'*80)
    

def consultar_cliente():
    session = Session()
    tipo_documento = input('Cliente pessoa física ou jurídica? [f/j]').strip().lower()

    cliente = None
    if tipo_documento == 'f':
        cpf_input = input('Digite o CPF do cliente: ')
        cliente = session.query(PessoaFisica).filter_by(cpf=cpf_input).first()
    elif tipo_documento == 'j':
        cnpj_input = input('Digite o CNPJ do cliente: ')
        cliente = session.query(PessoaJuridica).filter_by(cnpj=cnpj_input).first()

    session.close()

    if cliente:
        exibir_dados(cliente)
    else:
        print('Cliente não encontrado')


def listar_clientes():
    session = Session()
    clientes = session.query(Cliente).all()

    if clientes:
        for cliente in clientes:
            exibir_dados(cliente)
    else:
        print('Não há clientes registrados!')

    session.close()

def criar_conta():
    session = Session()

    tipo_documento = input('Para qual tipo de cliente? [f/j]: ')
    cliente = None

    if tipo_documento =='f':
        cpf_input = input('Digite o CPF do cliente: ')
        cliente = session.query(PessoaFisica).filter_by(cpf=cpf_input).first()
    elif tipo_documento == 'j':
        cnpj_input = input('Digite o CNPJ do cliente: ')
        cliente = session.query(PessoaJuridica).filter_by(cnpj=cnpj_input).first()

    if not cliente:
        print('Cliente não encontrado!')
        session.close()
        return
    
    tipo_conta = input('Digite o tipo de conta (corrente/poupança):').strip().lower()
    while tipo_conta not in ['corrente', 'poupança']:
        print('Tipo inválido. Escolha entre "corrente" ou "poupança".')
        tipo_conta = input('Digite o tipo de conta (corrente ou poupança): ')

    AGENCIA = 1

    nova_conta = Conta(id_cliente=cliente.id, tipo=tipo_conta, agencia=AGENCIA, saldo=0)
    session.add(nova_conta)
    session.commit()

    print(f'Conta {tipo_conta} criada com sucesso para {cliente.nome}!')
    session.close()


def exibir_conta(conta):
    print('='*80)
    print(f'Tipo de Conta: {conta.tipo.capitalize()}')
    print(f'Agência: {conta.agencia:04}')
    print(f'Número: {conta.id:06}')
    print(f'Saldo: R${conta.saldo:.2f}')
    print('='*80)


def consultar_contas_por_cliente():
    session = Session()
    tipo_cliente = input('Digite o tipo de cliente [f/j]: ').strip().lower()
    cliente = None

    if tipo_cliente == 'f':
        cpf_input = input('Digite o CPF do cliente: ')
        cliente = session.query(PessoaFisica).filter_by(cpf=cpf_input).first()
    elif tipo_cliente == 'j':
        cnpj_input = input('Digite o CNPJ do cliente: ')
        cliente = session.query(PessoaJuridica).filter_by(cnpj=cnpj_input).first()

    if not cliente:
        print('Cliente não encontrado!')
        session.close()
        return
    
    contas = session.query(Conta).filter_by(id_cliente=cliente.id).all()

    if not contas:
        print('O cliente não possui contas cadastradas!')
    else:
        print(f'\nContas associadas ao cliente {cliente.nome}:')
        for conta in contas:
            exibir_conta(conta)

    session.close()


def listar_contas():
    session = Session()

    clientes = session.query(Cliente).all()

    if not clientes:
        print('Não há clientes registrados!')
        session.close()
        return
    
    for cliente in clientes:
        print('\n')
        exibir_dados(cliente)

        contas_cliente = session.query(Conta).filter_by(id_cliente=cliente.id).all()

        if not contas_cliente:
            print('Este cliente não possui contas registradas!')
        else:
            for conta in contas_cliente:
                exibir_conta(conta)

    session.close()


def selecionar_conta_cliente():
    session = Session()
    tipo_documento = input('Para qual tipo de cliente? [f/j]: ')
    cliente = None

    if tipo_documento == 'f':
        cpf_input = input('Digite o CPF do cliente: ')
        cliente = session.query(PessoaFisica).filter_by(cpf=cpf_input).first()
    elif tipo_documento == 'j':
        cnpj_input = input('Digite do CNPJ do cliente: ')
        cliente = session.query(PessoaJuridica).filter_by(cnpj=cnpj_input).first()

    if not cliente:
        print('Cliente não encontrado!!')
        session.close()
        return
    
    contas_cliente = session.query(Conta).filter_by(id_cliente=cliente.id).all()
    if not contas_cliente:
        print('Esse cliente não possui nenhuma conta!')
        session.close()
        return
    
    print('Contas em nome do cliente:')
    for idx, conta in enumerate(contas_cliente, 1):
        print(f'{idx}. Conta {conta.tipo.capitalize()} - Número: {conta.id:06}')

    conta_idx = int(input('Digite o número que se refere à conta que você deseja movimentar: ')) - 1
    if conta_idx not in range(len(contas_cliente)):
        print("Seleção inválida!")
        return None
    
    return contas_cliente[conta_idx]

def depositar():
    session = Session()
    conta = selecionar_conta_cliente()

    if not conta:
        session.close()
        return

    valor_deposito = float(input('Digite o valor a ser depositado: R$ '))
    while valor_deposito <= 0:
        print('Digie um valor válido!!!')
        valor_deposito = float(input('Digite o valor a ser depositado: R$ '))
    
    conta = session.merge(conta)
    transacao = Transacao(id_conta=conta.id, data=datetime.now(), valor=valor_deposito, tipo='deposito')
    conta.saldo += valor_deposito

    session.add(transacao)
    session.commit()

    print(f'Depósito no valor de R${valor_deposito:.2f} realizado com sucesso na conta {conta.id:06}')
    print(f'Saldo atual = R$ {conta.saldo:.2f}')

    session.close()


def sacar():
    session = Session()
    conta = selecionar_conta_cliente()
    if not conta:
        return
    
    saques_hoje = session.query(Transacao).filter(
        Transacao.id_conta == conta.id,
        Transacao.tipo == 'saque',
        Transacao.data >= datetime.today().date()
    ).count()

    if saques_hoje >= 3:
        print('Limite de sques atingido. Volte amanhã!')
        session.close()
        return
    
    valor_saque = float(input('Digite o valor que você deseja sacar: R$ '))
    while valor_saque <= 0 or valor_saque > 500 or valor_saque > conta.saldo:
        if valor_saque <= 0:
            print('Digite um valor positivo')
        elif valor_saque > 500:
            print('Valor do saque excedido (R$500,00)')
        else:
            print(f'Saldo atual: R$ {conta.saldo:.2f}')
            return
        valor_saque = float(input('Digite o valor a ser sacado: R$ '))
    
    conta = session.merge(conta)
    transacao = Transacao(id_conta=conta.id, data=datetime.now(), valor=valor_saque, tipo='saque')
    conta.saldo -= valor_saque

    session.add(transacao)
    session.commit()

    print(f'Saque de R$ {valor_saque:.2f} realizado com sucesso na Conta {conta.tipo.capitalize()} número {conta.id}!')
    print(f'Saldo atual = R$ {conta.saldo:.2f}')
    session.close()


def exibir_transacao(transacao):
    tipo_transacao = 'Depósito' if transacao.tipo == 'deposito' else 'Saque'
    print('-'*80)
    print(f'Data: {transacao.data.strftime("%d/%m/%Y %H:%M:%S")}')
    print(f'Tipo: {tipo_transacao}')
    print(f'Valor: R$ {transacao.valor:.2f}')
    print('-'*80)

def extrato():
    session = Session()

    conta = selecionar_conta_cliente()
    if not conta:
        print('Conta não encontrada!')
        session.close()
        return
    
    cliente = session.query(Cliente).filter_by(id=conta.id_cliente).first()
    exibir_dados(cliente)
    exibir_dados(conta)

    transacoes = session.query(Transacao).filter_by(id_conta=conta.id).all()

    if not transacoes:
        print('Conta não movimentada!')
        session.close()
        return
    
    print('Transações: ')
    for transacao in transacoes:
        exibir_transacao(transacao)

    session.close()


def listar_transacoes():
    session = Session()

    clientes = session.query(Cliente).all()
    if not clientes:
        print('Não há clientes cadastrados')
    for cliente in clientes:        
        exibir_dados(cliente)

        contas = session.query(Conta).filter_by(id_cliente=cliente.id).all()
        if not contas:
            print('Não há contas cadastradas!')
        for conta in contas:
            exibir_conta(conta)

            transacoes = session.query(Transacao).filter_by(id_conta=conta.id).all()
            if not transacoes:
                print('Não há nenhuma movimentação')
            for transacao in transacoes:
                exibir_transacao(transacao)
    
    session.close()

def menu():
    menu = '''\n
    Você pode:
    [ 1 ] Criar Cliente
    [ 2 ] Consultar Cliente
    [ 3 ] Listar Clientes
    [ 4 ] Criar Conta
    [ 5 ] Consultar Contas por Cliente
    [ 6 ] Listar Contas
    [ 7 ] Depositar
    [ 8 ] Sacar
    [ 9 ] Extrato
    [ 10 ] Listar Transações
    [ 11 ] Sair
    '''
    return input(textwrap.dedent(menu))


def main():
    while True:
        operacao = menu()

        if operacao == '1':
            criar_cliente()
        
        elif operacao == '2':
            consultar_cliente()

        elif operacao == '3':
            listar_clientes()

        elif operacao == '4':
            criar_conta()

        elif operacao == '5':
            consultar_contas_por_cliente()

        elif operacao == '6':
            listar_contas()

        elif operacao == '7':
            depositar()

        elif operacao == '8':
            sacar()

        elif operacao == '9':
            extrato()

        elif operacao == '10':
            listar_transacoes()

        elif operacao == '11':
            break
        
        else:
            print('\033[1;43mDigite uma opção válida: \033[m')

main()