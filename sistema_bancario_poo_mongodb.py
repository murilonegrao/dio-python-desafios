import textwrap
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument


with open('arquivo.txt', 'r', encoding="utf-8") as file:
    uri = file.readline().strip()
client = MongoClient(uri)
db = client['sistema_bancario']
clientes_collection = db['clientes']

if not db['controle'].find_one({'tipo': 'numero_conta'}):
    db['controle'].insert_one({'tipo': 'numero_conta', 'valor': 1})

clientes_collection.create_index('cpf', unique=True, sparse=True)
clientes_collection.create_index('cnpj', unique=True, sparse=True)

def criar_cliente():
    while True:
        tipo_cliente = input('Digite o tipo de cliente [f/j]: ').strip().lower()

        nome = input(str('Digite o nome do cliente: '))
        endereço = input('Digite o endereço: ')
        cliente_data = {
            'nome': nome,
            'endereço': endereço,
            'tipo': tipo_cliente
        }

        if tipo_cliente == 'f':
            cpf = input('Digite o CPF: ')
            data_nascimento = input('Digite a data de nascimento: ')
            cliente_data['cpf'] = cpf
            cliente_data['data_nascimento'] = data_nascimento
        elif tipo_cliente == 'j':
            cnpj = input('Digite o CNPJ: ')
            cliente_data['cnpj'] = cnpj
        else:
            print('Digite um tipo válido [f/j]: ')
            continue

        try:
            clientes_collection.insert_one(cliente_data)
            print(f'Cliente {nome} adicionado com sucesso!')
            break
        except DuplicateKeyError:
            print('ERRO: CPF ou CNPJ já cadastrado!!!')
        except Exception as e:
            print(f'Erro ao adiconar cliente: {e}')

def exibir_dados(cliente):
    print('*' * 80)
    print(f'ID Cliente: {cliente["_id"]}')
    print(f'Nome: {cliente["nome"]}')
    print(f'Endereço: {cliente["endereço"]}')

    if cliente['tipo'] == 'f':
        print(f'CPF: {cliente["cpf"]}')
        print(f'Data de Nascimento: {cliente["data_nascimento"]}')
    elif cliente['tipo'] == 'j':
        print(f'CNPJ: {cliente["cnpj"]}')

    print('*' * 80)


def consultar_cliente():
    tipo_documento = input("Pessoa Física ou Jurídica: [f/j]: ")
    
    if tipo_documento == 'f':
        cpf_input = input('Digite o CPF do cliente: ')
        cliente = clientes_collection.find_one({'cpf': cpf_input})
    elif tipo_documento == 'j':
        cnpj_input = input('Digite o CNPJ do cliente: ')
        cliente = clientes_collection.find_one({'cnpj': cnpj_input})

    if cliente:
        exibir_dados(cliente)
    else:
        print('Cliente não encontrado')


def listar_clientes():
    clientes = clientes_collection.find()

    if clientes:
        for cliente in clientes:
            exibir_dados(cliente)
    else:
        print('Não há clientes registrados!')


def obter_cliente_por_documento():
    tipo_documento = input('Para qual tipo de cliente? [f/j]: ')
    cliente_data = None

    if tipo_documento == 'f':
        cpf_input = input('Digite o CPF do cliente: ')
        cliente_data = clientes_collection.find_one({'cpf': cpf_input})
    elif tipo_documento == 'j':
        cnpj_input = input('Digite o CNPJ do cliente: ')
        cliente_data = clientes_collection.find_one({'cnpj': cnpj_input})

    if not cliente_data:
        print('Cliente não encontrado')
        return None
    
    return cliente_data

def criar_conta():
    cliente_data = obter_cliente_por_documento()
    if not cliente_data:
        return
    
    tipo_conta = input('Digite o tipo de conta (corrente/poupança): ')
    while tipo_conta not in ['corrente', 'poupança']:
        print('Digite corrente ou poupança: ')
        tipo_conta = input('Digite o tipo de conta (corrente/poupança): ')

    numero_conta = db['controle'].find_one_and_update(
        {'tipo': 'numero_conta'},
        {'$inc': {'valor': 1}},
        return_document=ReturnDocument.AFTER
    )['valor']

    nova_conta = {
        'tipo': tipo_conta, 
        'agencia': '0001',
        'numero': str(numero_conta).zfill(6),
        'saldo': 0.0,
        'transacoes': []
    }

    clientes_collection.update_one({'_id': cliente_data['_id']}, {'$push': {'contas': nova_conta}})
    print(f'Conta {nova_conta["numero"]} criada com sucesso para {cliente_data["nome"]}!')


def exibir_conta(conta):
    print('=' * 80)
    print(f'Tipo de Conta: {conta["tipo"].capitalize()}')
    print(f'Agência: {conta["agencia"]}')
    print(f'Número: {conta["numero"]}')
    print(f'Saldo: R${conta["saldo"]:.2f}')
    print('=' * 80)

def consultar_contas_por_cliente():
    cliente_data = obter_cliente_por_documento()
    if not cliente_data:
        print('Cliente não encontrado!')
        return

    contas = cliente_data.get('contas', [])
    if not contas:
        print(f'Cliente {cliente_data["nome"]} não possui contas cadastradas!')


    print(f'\nContas associadas ao cliente {cliente_data["nome"]}: ')
    for conta in contas:
        exibir_conta(conta)


def listar_contas():
    todos_clientes = clientes_collection.find()
    for cliente in todos_clientes:
        exibir_dados(cliente)
        contas_cliente = cliente.get('contas', [])
        if not contas_cliente:
            print(f'Cliente {cliente["nome"]} não possui contas cadastradas!')
        else:
            for conta in contas_cliente:
                exibir_conta(conta)


def selecionar_conta_cliente(cliente_data):
    if 'contas' not in cliente_data or not cliente_data['contas']:
        print(f'Cliente {cliente_data["nome"]} não possui contas cadastradas!')
        return None

    for idx, conta in enumerate(cliente_data['contas']):
        print(f'{idx + 1}. Conta {conta["tipo"]} - Número: {conta["numero"]} - Saldo: {conta["saldo"]:.2f}')
    
    escolha = int(input('Escolha a conta para depositar: ')) - 1

    if escolha < 0 or escolha > len(cliente_data['contas']):
        print('Digite uma opção válida!')
        return None
    
    return cliente_data['contas'][escolha]
    

def depositar():
    cliente_data = obter_cliente_por_documento()
    if not cliente_data:
        return
    
    conta_selecionada = selecionar_conta_cliente(cliente_data)
    if not conta_selecionada:
        return
    
    valor_deposito = float(input('Digite o valor do depósito: '))
    if valor_deposito <= 0:
        print('Digite um valor válido')
        return
    
    index_conta = None
    for idx, conta in enumerate(cliente_data['contas']):
        if conta['numero'] == conta_selecionada['numero']:
            index_conta = idx
            break

    if index_conta is None:
        print('Conta não encontrada!')
        return
    
    path_saldo = f'contas.{index_conta}.saldo'
    path_transacoes = f'contas.{index_conta}.transacoes'

    clientes_collection.update_one(
        {'_id': cliente_data['_id']},
        {
            '$inc': {path_saldo: valor_deposito},
            '$push': {path_transacoes: {
                'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'tipo': 'deposito',
                'valor': valor_deposito
            }}
        }
    )

    print(f'Depósito de R$ {valor_deposito:.2f} realizado com sucesso na conta {conta_selecionada["numero"]}!!')


def sacar():
    cliente_data = obter_cliente_por_documento()
    if not cliente_data:
        return
    
    conta_selecionada = selecionar_conta_cliente(cliente_data)
    if not conta_selecionada:
        return
    
    valor_saque = float(input('Digite o valor do saque: '))
    if valor_saque <= 0:
        print('Digite um valor válido para sacar')
        return
    if valor_saque > 500:
        print('O valor digitado excede o limite por saque (R$500,00)')
        return
    if valor_saque > conta_selecionada['saldo']:
        print(f'Saldo insuficiente. Seu saldo é de R$ {conta_selecionada["saldo"]}.')
        return
    
    data_atual = datetime.now().strftime("%d-%m-%Y")
    saques_dia = sum(1 for transacao in conta_selecionada['transacoes'] if transacao['tipo'] == 'saque' and transacao['data'].startswith(data_atual))

    if saques_dia >= 3:
        print('Você já realizou 3 saques hoje. Volte amanhã.')
        return

    index_conta = None
    for idx, conta in enumerate(cliente_data['contas']):
        if conta['numero'] == conta_selecionada['numero']:
            index_conta = idx
            break

    if index_conta is None:
        print('Conta não encontrada!')
        return
    
    path_saldo = f'contas.{index_conta}.saldo'
    path_transacoes = f'contas.{index_conta}.transacoes'

    clientes_collection.update_one(
        {'_id': cliente_data['_id']},
        {
            '$inc': {path_saldo: -valor_saque},
            '$push': {path_transacoes: {
                'data': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'tipo':'saque',
                'valor': valor_saque
            }}
        }
    )

    print(f'Saque de R$ {valor_saque:.2f} realizado com sucesso na conta {conta_selecionada["numero"]}!!')


def exibir_transacoes(conta):
    print(f'Extrato da conta {conta["numero"]} - {conta["tipo"]}')
    print('-' * 80)
    if not conta.get('transacoes'):
        print('Não há transações nesta conta')
        return
    
    for transacao in conta['transacoes']:
        tipo = transacao['tipo']
        data = transacao['data']
        valor = transacao['valor']
        if tipo == 'saque':
            print(f'{data} - Saque de R$ {valor:.2f}')
        elif tipo == 'deposito':
            print(f'{data} - Deposito de R$ {valor:.2f}')
        else:
            print(f'{data} - {tipo.capitalize()} de R$ {valor:.2f}')

    print('-' * 80)
    print(f'Saldo atual: R$ {conta["saldo"]:.2f}')

def extrato():
    cliente_data = obter_cliente_por_documento()
    if not cliente_data:
        return
    conta_selecionada = selecionar_conta_cliente(cliente_data)
    if not conta_selecionada:
        return
    
    exibir_transacoes(conta_selecionada)


def listar_transacoes_do_dia():
    data_atual = datetime.now().strftime("%d/%m/%Y")

    todos_clientes = clientes_collection.find()

    for cliente in todos_clientes:
        exibir_dados(cliente)

        for conta in cliente["contas"]:
            transacoes_do_dia = [transacao for transacao in conta['transacoes'] if transacao["data"].startswith(data_atual)]

            if transacoes_do_dia:
                exibir_conta(conta)
                for transacao in transacoes_do_dia:
                    tipo = transacao['tipo']
                    data = transacao['data']
                    valor = transacao['valor']
                    if tipo == 'saque':
                        print(f'{data} - Saque de R$ {valor:.2f}')
                    elif tipo == 'deposito':
                        print(f'{data} - Deposito de R$ {valor:.2f}')
                    else:
                        print(f'{data} - {tipo.capitalize()} de R$ {valor:.2f}')
                print('-' * 80)
                print(f'Saldo atual: R$ {conta["saldo"]:.2f}')
                print('\n\n')
            else:
                exibir_conta(conta)
                print('-' * 80)
                print('Sem transações')
                print('-' * 80)
                continue


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
            listar_transacoes_do_dia()

        elif operacao == '11':
            break
        
        else:
            print('\033[1;43mDigite uma opção válida: \033[m')

main()