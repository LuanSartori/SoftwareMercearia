from utils import *
from model import *
from controller import *
from dal import *
from time import sleep


# --------------------------------------------------
# --------------------------------------------------


def cadastrar():
    titulo('Cadastre-se!', comprimento=40, justificar=True)

    while True:
        try:
            usuario = str(input('Usuário: ')).strip()
            telefone = str(input('Telefone [com DDD]: '))
            telefone = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            email = str(input('Email: ')).strip()
            cpf = str(input('CPF: ')).strip()
            senha = str(input('Senha: ')).strip()

            ClienteController.cadastrar_cliente(usuario, cpf, senha, telefone, email)
            break
        except TypeError:
            titulo('Dados Inválidos!', '-')
            continue
        except ValueError as arg:
            titulo(str(arg), '-')
            continue
        except Exception as arg:
            titulo(f'ERRO: {str(arg)}', '*')
            exit()
    
    titulo(f'Cadastrado com Sucesso! Seja Bem Vindo {usuario}!', '=')


def login():
    match str(input('Você já tem cadastro? [S/N] ')).strip().upper():
        case 'S':
            pass
        case 'N':
            cadastrar()
            sleep(5)
        case other:
            titulo('Resposta Inválida!')

    titulo('Faça Login', comprimento=40, justificar=True)
    
    while True:
        try:
            usuario = str(input('Usuário: '))
            senha = str(input('Senha: '))

            login_cliente = LoginController.logar_cliente(usuario, senha)
            break
        except TypeError:
            titulo('Dados Inválidos!', '-')
            continue
        except ValueError as arg:
            titulo(str(arg), '-')
            continue
        except Exception as arg:
            titulo(f'ERRO: {str(arg)}', '*')
            exit()
    
    titulo(f'Logado com Sucesso! Seja Bem Vindo {login_cliente.nome}!', '=')
    return login_cliente


# --------------------------------------------------
# --------------------------------------------------


def menu_produtos(login_cliente: LoginCliente):
    produtos = []

    while True:
        titulo('Selecione uma Categoria:', '=')
        ids = EstoqueController.listar_categorias()
        id_categoria = ids[int(input('ID: '))-1]

        titulo('Selecione o Produto:', '=', comprimento=100, justificar=True)
        ids = EstoqueController.listar_produtos(id_categoria)
        if len(ids) == 0:
            titulo('Ops, sem nenhum produto nessa categoria!', '*', comprimento=100, justificar=True)
            print('\n')
            continue
        id_produto = ids[int(input('ID: '))-1]
        print()

        print('-'*50)
        produtos.append((id_produto, int(input('Quantidade: '))))
        print('-'*50, '\n')
        
        x = False
        while True:
            match str(input('Mais alguma coisa? [S/N] ')).strip().upper():
                case 'S':
                    x = True
                case 'N':
                    pass
                case other:
                    titulo('Resposta Inválida!', comprimento=50, justificar=True)
                    continue
            break
        if x:
            continue

    carrinho = []
    for pdt, qnt in produtos:
        carrinho.append(CaixaController.passar_produto(pdt, qnt))
    carrinho = Carrinho(carrinho, preco_total(carrinho))

    CaixaController.dados_da_compra(carrinho)
    print()

    while True:
        print('-'*50)
        match str(input('Confirmar Compra: [S/N] ')).strip().upper():
            case 'S':
                break
            case 'N':
                return False
            case other:
                continue
    
    print('-'*50)
    valor_pago = float(input('\nPagar: R$'))
    troco = VendaController.venda_online(login_cliente, carrinho, valor_pago)

    titulo('Obrigado pela Preferência ;)', comprimento=50, justificar=True)
    print(f'Seu Troco: R${troco:.2f}\n\n\n')


# --------------------------------------------------
# --------------------------------------------------


def menu_principal(login_cliente: LoginCliente):
    while True:
        acoes = ['Produtos', 'Logout', 'Sair']
        listar_acoes(acoes)

        try:
            decisao = int(input('O que você quer fazer? '))
            print()
            match decisao:
                # Menu produtos
                case 1:
                    if not menu_produtos(login_cliente):
                        continue

                # Fazer logout
                case 2:
                    return 'LOGOUT'

                # Sair
                case 3:
                    exit()

                # Opção inválida
                case other:
                    raise ValueError('Opção inválida!')

        except ValueError as arg:
            if arg.args[0] == 'RAISE':
                erro = ''
                for i, e in enumerate(arg.args):
                    if i == 0:
                        continue
                    erro += str(e) + ' | '
                titulo(erro, '*')
            else:
                titulo('Valor Inválido!', '*')
            continue
        except IndexError as arg:
            titulo('Este valor não é válido!')
            continue
        except ServerError as arg:
            titulo(f'Erro de conexão com o servidor: {str(arg)}')
            exit()
        except IdError as arg:
            titulo(f'Estamos com um problema interno do sistema, tente outra hora por favor!')
            exit()
        except Exception as arg:
            titulo(f'ERRO: {type(arg)} | {str(arg)}', '*')
            exit()



# --------------------------------------------------
# --------------------------------------------------


if __name__ == '__main__':
    while True:
        login_cliente = login()
        if not login_cliente:
            continue

        if menu_principal(login_cliente) == 'LOGOUT':
            continue
        break