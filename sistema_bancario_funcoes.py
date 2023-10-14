import textwrap


def menu():
    menu = '''\n
    Você pode:
    [ 1 ] Depositar
    [ 2 ] Sacar
    [ 3 ] Extrato
    [ 4 ] Nova conta
    [ 5 ] Listar contatos
    [ 6 ] Novo usuário
    [ 7 ] Sair
    '''
    return input(textwrap.dedent(menu))


def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saque = numero_saques >= limite_saques

    if excedeu_saldo:
        print('\n\033[1;41mOperação não realizada. Saldo insuficiente!!!\033[m')

    elif excedeu_limite:
        print('\n\033[1;41mOperação não realizada. Valor acima do limite!!!\033[m')

    elif excedeu_saque:
        print('\033[1;41mVocê atingiu o limite máximo de saques diário!!!\033[m')

    elif valor > 0:
        saldo -= valor
        extrato += f'Saque de R${valor:.2f}\n'
        numero_saques += 1

    else:
        print('\033[1;41mOperação não realizada. Valor inválido\033[m')
    return saldo, extrato, numero_saques


def depositar(saldo, valor, extrato, /):
    if valor > 0:
        saldo += valor
        extrato += f'Depósito de R${valor:.2f}\n'
    else:
        print(f'\033[1;41mOperação inválida. Depósito não efetuado\033[m')
    return saldo, extrato


def exibir_extrato(saldo, /, *, extrato):
    print('*'*30)
    print('Não foram realizadas movimentações.' if not extrato else extrato)
    print(f'Saldo: R${saldo:.2f}')
    print('*'*30)


def criar_usuario(usuarios):
    cpf = input('Digite o CPF (somente números): ')
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print('\033[1;43mUsuário já cadastrado\033[m')
        return

    nome = input('Digite o nome completo: ')
    data_nascimento = input('Informe a data de nascimento (dd-mm-aaaa): ')
    endereco = input('Informe o endereço com (rua, número, bairro, cidade/sigla do Estaso): ')

    usuarios.append({'Nome': nome, 'Data de Nascimento': data_nascimento, 'CPF': cpf, 'Endereço': endereco})

    print('\033[1;42mUsuário cadastrado com sucesso!\033[m')


def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario['CPF'] == cpf]
    return usuarios_filtrados [0] if usuarios_filtrados else None


def criar_conta_corrente(agencia, numero_conta, usuarios):
    cpf = input('Digite o CPF do titular: ')
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print('\033[1;42m Conta criada com sucesso!!!\033[m')
        return {'Agência': agencia, 'Conta Corrente': numero_conta, 'Cliente': usuario}
    
    print('\033[1;41mUsuário não encontrado, crie um usuário primeiro!!!\033[m')


def listar_contas(contas):
    for conta in contas:
        linha = f'''\
            Agência:\t{conta['Agência']}
            C/C:\t\t{conta['Conta Corrente']}
            Titular\t{conta['Cliente']['Nome']}
        '''
        print('*'*80)
        print(textwrap.dedent(linha))


def main():
    LIMITE_SAQUES = 3
    AGENCIA = '0001'

    saldo = 0
    limite = 500
    extrato = ''
    numero_saques = 0
    usuarios = []
    contas = []
    
    while True:

        operacao = menu()

        if operacao == '1':
            valor = float(input('Digite um valor a depositar: '))

            saldo, extrato = depositar(saldo, valor, extrato)


        elif operacao == '2':
            valor = float(input('Digite o valor do saque: '))

            saldo, extrato, numero_saques = sacar(
                saldo=saldo,
                valor=valor,
                extrato=extrato,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES,
            )


        elif operacao == '3':
            exibir_extrato(saldo, extrato=extrato)

        elif operacao == '4':
            numero_conta = len(contas) + 1
            conta = criar_conta_corrente(AGENCIA, numero_conta, usuarios)

            if conta:
                contas.append(conta)

        elif operacao == '5':
            listar_contas(contas)

        elif operacao == '6':
            criar_usuario(usuarios)

        elif operacao == '7':
            break

        
        else:
            print('\033[1;43mDigite uma opção válida: \033[m')

main()