menu = '''

        Qual operação você quer realizar?
        [ 1 ] Deposito
        [ 2 ] Saque
        [ 3 ] Ver extrato
        [ 4 ] Sair
        
        '''

conta = 0
limite = 500
extrato = ''
numero_saques = 0
LIMITE_SAQUES = 3

while True:

    operacao = input(menu)

    if operacao == '1':
        print('Depósito')
        valor = float(input('Digite um valor para depositar: '))
        if valor > 0:
            conta += valor
            extrato += f'Depósito de R${valor:.2f}\n'
        else:
            print(f'Operação inválida. Depósito não efetuado')


    elif operacao == '2':
        valor = float(input('Digite o valor do saque: '))
        excedeu_saldo = valor > conta

        excedeu_limite = valor > limite

        excedeu_saque = numero_saques >= LIMITE_SAQUES

        if excedeu_saldo:
            print('Operação não realizada. Saldo insuficiente')

        elif excedeu_limite:
            print('Operação não realizada. Valor acima do limite')

        elif excedeu_saque:
            print('Você atingiu o limite máximo de saques diário')

        elif valor > 0:
            conta -= valor
            extrato += f'Saque de R${valor:.2f}\n'
            numero_saques += 1

        else:
            print('Operação não realizada. Valor inválido')

    elif operacao == '3':
        print('-='*30)
        print('Não foi realizada nenhuma operação' if not extrato else extrato)
        print(f'\nSaldo: R$ {conta:.2f}')
        print('-='*30)

    elif operacao == '4':
        break

    
    else:
        print('Digite uma opção válida: ')
        