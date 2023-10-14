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


def usuario():
    nome = 
    data_nascimento = 
    cpf = único
    endereco = (logradouro, bairro, cidade/sigla_estado)


def conta_corrente():
    agencia = '0001'
    numero_conta = sequencial, iniciando em '0001'
    

def main():
    LIMITE_SAQUES = 3
    AGENCIA = '0001'

    saldo = 0
    limite = 500
    extrato = ''
    numero_saques = 0
    
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
            break

        
        else:
            print('\033[1;43mDigite uma opção válida: \033[m')

main()