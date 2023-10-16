from abc import ABC, abstractclassmethod, abstractproperty
import textwrap
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, usuario):
        self._saldo = 0
        self._numero = numero
        self._agencia = '0001'
        self._usuario = usuario
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, usuario, numero):
        return cls(numero, usuario)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def usuario(self):
        return self._usuario
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print('\n\033[1;41mSaque não realizado por falta de saldo\033[m')

        elif valor > 0:
            self._saldo -= valor
            print('\n\033[1;42mSaque realizado com sucesso!!!\033[m')
            return True
        
        else:
            print('\n\033[1;41mSaque não realizado, valor inválido\033[m')

        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print('\n\033[1;42mDepósito realizado com sucesso\033[m')
        else:
            print('\n\033[1;41mOperação não realizada. Informe um valor válido\033[m')
            return False
        
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, usuario, limite=500, limite_saques=3):
        super().__init__(numero, usuario)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao['tipo'] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print('\n\033[1;41mValor do saque maior que R$500,00. Operação não efetuada!!\033[m')

        elif excedeu_saques:
            print('\n\033[1;41mNúmero de saques diário atingido. Volte amanhã!!\033[m')

        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f'''\
            Agência: \t{self.agencia}
            C/C:\t\t{self.numero}
            Titular\t{self.usuario.nome}
        '''


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor,
                'data': datetime.now().strftime('%d-%m-%Y %H:%M:%s'),
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


def menu():
    menu = '''\n
    Você pode:
    [ 1 ] Depositar
    [ 2 ] Sacar
    [ 3 ] Extrato
    [ 4 ] Nova conta
    [ 5 ] Listar contas
    [ 6 ] Novo usuário
    [ 7 ] Sair
    '''
    return input(textwrap.dedent(menu))


def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados [0] if usuarios_filtrados else None


def recuperar_conta_usuario(usuario):
    if not usuario.contas:
        print('\n\033[1;43mO cliente não possui conta!!!\033[m')

    return usuario.contas[0]


def depositar(usuarios):
    cpf = input('Informe o CPF do cliente: ')
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print('\n\033[1;41mCliente não encontrado\033[m')
        return
    
    valor = float(input('Digite o valor do depósito: '))
    transacao = Deposito(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    usuario.realizar_transacao(conta, transacao)


def sacar(usuarios):
    cpf = input('Informe o CPF do cliente: ')
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print('\n\033[1;43mCliente não encontrado na base de dados!!\033[m')
        return

    valor = float(input('Informe o valor do saque: '))
    transacao = Saque(valor)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    usuario.realizar_transacao(conta, transacao)


def exibir_extrato(usuarios):
    cpf = input('Informe o CPF do cliente: ')
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print('\n\033[1;43mCliente não encontrado na base de dados!!\033[m')
        return
    
    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    print('*'*100)
    transacoes = conta.historico.transacoes

    extrato = ''
    if not transacoes:
        extrato = 'Não foram realizadas movimentações.'
    else:
        for transacao in transacoes:
            extrato += f'\n{transacao["tipo"]}:\n\tR$ {transacao["valor"]:.2f}'
    

    print(extrato)
    print(f'\nSaldo:\n\tR$ {conta.saldo:.2f}')
    print('*'*100)


def criar_usuario(usuarios):
    cpf = input('Digite o CPF (somente números): ')
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print('\033[1;43mUsuário já cadastrado\033[m')
        return

    nome = input('Digite o nome completo: ')
    data_nascimento = input('Informe a data de nascimento (dd-mm-aaaa): ')
    endereco = input('Informe o endereço com (rua, número, bairro, cidade/sigla do Estaso): ')

    usuario = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    
    usuarios.append(usuario)

    print('\033[1;42mUsuário cadastrado com sucesso!\033[m')




def criar_conta_corrente(numero_conta, usuarios, contas):
    cpf = input('Digite o CPF do titular: ')
    usuario = filtrar_usuario(cpf, usuarios)

    if not usuario:
        print('\033[1;41mUsuário não encontrado, crie um usuário primeiro!!!\033[m')
        return
    
    conta = ContaCorrente.nova_conta(usuario=usuario, numero=numero_conta)
    contas.append(conta)
    usuario.contas.append(conta)

    print('\033[1;42m Conta criada com sucesso!!!\033[m')


def listar_contas(contas):
    for conta in contas:
        print('*'*80)
        print(textwrap.dedent(str(conta)))


def main():
    usuarios = []
    contas = []
    
    while True:
        operacao = menu()

        if operacao == '1':
            depositar(usuarios)

        elif operacao == '2':
            sacar(usuarios)

        elif operacao == '3':
            exibir_extrato(usuarios)

        elif operacao == '4':
            numero_conta = len(contas) + 1
            criar_conta_corrente(numero_conta, usuarios, contas)

        elif operacao == '5':
            listar_contas(usuarios)

        elif operacao == '6':
            criar_usuario(usuarios)

        elif operacao == '7':
            break
        
        else:
            print('\033[1;43mDigite uma opção válida: \033[m')


main()