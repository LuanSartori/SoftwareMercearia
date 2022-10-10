from utils import *
from model import *
from controller import *
from dal import *
from time import sleep


# --------------------------------------------------
# --------------------------------------------------


def login() -> LoginFuncionario:
    titulo('Faça Login', comprimento=40, justificar=True)
    
    while True:
        try:
            usuario = str(input('Usuário: '))
            senha = str(input('Senha: '))
            match str(input('Logar como ADM? [S/N] ')).upper().strip():
                case 'S':
                    admin = True
                case 'N':
                    admin = False
                case other:
                    titulo('Resposta inválida!')
                    continue

            login_funcionario = LoginController.logar_funcionario(usuario, senha, admin)
            break
        except TypeError:
            titulo('Dados Inválidos!', '-')
            continue
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
        except Exception as arg:
            titulo(f'ERRO: {str(arg)}', '*')
            exit()
    
    titulo(f'Logado com Sucesso! Seja Bem Vindo {login_funcionario.nome}!', '=')
    return login_funcionario


# --------------------------------------------------
# --------------------------------------------------


def menu_adm(login_funcionario: LoginFuncionario) -> bool | None:
    acoes = ['Cadastrar ADM', 'Alterar ADM', 'Remover ADM', 'Ver um ADM', 'Voltar']
    listar_acoes(acoes)

    decisao = int(input('O que você quer fazer? '))
    print()
    match decisao:
        # Cadastrar ADM
        case 1:
            nome = str(input('Nome: ')).strip()
            telefone = str(input('Telefone [com DDD]: '))
            telefone = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            email = str(input('Email: ')).strip()
            cpf = str(input('CPF: ')).strip()
            cargo = str(input('Cargo: ')).strip()
            senha = str(input('Senha: ')).strip()
            posicao = int(input('Posição: '))
            FuncionarioController.cadastrar_funcionario(nome, telefone, email, cpf, cargo, senha,
                                                        True, posicao, login_funcionario)
            titulo('ADM Cadastrado com Sucesso!')

        # Alterar ADM
        case 2:
            ids = FuncionarioController.listar_funcionarios(True)
            if len(ids) == 0:
                titulo('Ops, sem nenhum ADM!')
                return False
            id = ids[int(input('ID: '))-1]

            acoes = ['CPF', 'Nome', 'Telefone', 'Email',
                        'Cargo', 'Senha', 'Posição', 'Pronto']
            alteracoes = {}
            posicao = None
            
            while True:
                print('-'*30)
                print('Você deseja alterar:')
                listar_acoes(acoes)
                decisao = int(input('Opção: '))
                print()
                match decisao:
                    case 1:
                        alteracoes.update(cpf=str(input('CPF: ').strip()))
                    case 2:
                        alteracoes.update(nome=str(input('Nome: ').strip()))
                    case 3:
                        telefone = str(input('Telefone [com DDD]: '))
                        telefone = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                        alteracoes.update(telefone=telefone)
                    case 4:
                        alteracoes.update(email=str(input('Email: ').strip()))
                    case 5:
                        alteracoes.update(cargo=str(input('Cargo: ').strip()))
                    case 6:
                        alteracoes.update(senha=str(input('Senha: ').strip()))
                    case 7:
                        alteracoes.update(posicao=int(input('Posição (Não pode ser maior do que a sua): ')))
                    case 8:
                        break
            
            FuncionarioController.alterar_funcionario(id, True, login_funcionario,
                                                      **alteracoes)
            titulo('ADM alterado com sucesso!')

        # Remover ADM                     
        case 3:
            ids = FuncionarioController.listar_funcionarios(True)
            if len(ids) == 0:
                titulo('Ops, sem nenhum ADM!')
                return False
            id = ids[int(input('ID: '))-1]

            print('-'*70)
            x = False
            while True:
                match str(input('Tem certeza que deseja remover este ADM? [S/N] ')).strip().upper():
                    case 'S':
                        print('-'*70)
                        break
                    case 'N':
                        x = True
                        print('-'*70)
                        break
                    case other:
                        titulo('Resposta inválida!')
            if x:
                return False
            
            print()
            FuncionarioController.remover_funcionario(id, True, login_funcionario)
            titulo('ADM removido com sucesso!')

        # Ver ADM
        case 4:
            titulo('Selecione o ADM')
            ids = FuncionarioController.listar_funcionarios(True)
            if len(ids) == 0:
                titulo('Ops, sem nenhum ADM!')
                return False
            id_funcionario = ids[int(input('ID: '))-1]

            FuncionarioController.ver_funcionario(id_funcionario, True)

        # Voltar
        case 5:
            print('-'*30)
            return False
        
        # Opção inválida
        case other:
            raise ValueError('Opção inválida!')


def menu_funcionarios() -> bool | None:
    acoes = ['Cadastrar Funcionário', 'Alterar Funcionário', 'Remover Funcionário', 'Ver Funcionário', 'Voltar']
    listar_acoes(acoes)

    decisao = int(input('O que você quer fazer? '))
    print()
    match decisao:
        # Cadastrar um funcionário
        case 1:
            nome = str(input('Nome: ')).strip()
            telefone = str(input('Telefone [com DDD]: '))
            telefone = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            email = str(input('Email: ')).strip()
            cpf = str(input('CPF: ')).strip()
            cargo = str(input('Cargo: ')).strip()
            senha = str(input('Senha: ')).strip()
            FuncionarioController.cadastrar_funcionario(nome, telefone, email, cpf, cargo, senha,
                                                        False, login_funcionario)
            titulo('Funcionário Cadastrado com Sucesso!')

        # Alterar um funcionário
        case 2:
            ids = FuncionarioController.listar_funcionarios(False)
            if len(ids) == 0:
                titulo('Ops, sem nenhum funcionário!')
                return False
            id = ids[int(input('ID: '))-1]

            acoes = ['CPF', 'Nome', 'Telefone', 'Email',
                        'Cargo', 'Senha', 'Pronto']
            alteracoes = {}
            
            while True:
                print('-'*30)
                print('Você deseja alterar:')
                listar_acoes(acoes)
                decisao = int(input('Opção: '))
                print()

                match decisao:
                    case 1:
                        alteracoes.update(cpf=str(input('CPF: ').strip()))
                    case 2:
                        alteracoes.update(nome=str(input('Nome: ').strip()))
                    case 3:
                        telefone = str(input('Telefone [com DDD]: '))
                        telefone = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                        alteracoes.update(telefone=telefone)
                    case 4:
                        alteracoes.update(email=str(input('Email: ').strip()))
                    case 5:
                        alteracoes.update(cargo=str(input('Cargo: ').strip()))
                    case 6:
                        alteracoes.update(senha=str(input('Senha: ').strip()))
                    case 7:
                        break
            
            FuncionarioController.alterar_funcionario(id, False, login_funcionario,
                                                        **alteracoes)
            titulo('Funcionário alterado com sucesso!')                          

        # Remover um funcionário
        case 3:
            ids = FuncionarioController.listar_funcionarios(False)
            if len(ids) == 0:
                titulo('Ops, sem nenhum funcionário!')
                return False
            id = ids[int(input('ID: '))-1]

            print('-'*70)
            x = False
            while True:
                match str(input('Tem certeza que deseja remover este funcionário? [S/N] ')).upper():
                    case 'S':
                        print('-'*70)
                        break
                    case 'N':
                        x = True
                        print('-'*70)
                        break
                    case other:
                        titulo('Resposta inválida!')
            if x:
                return False

            print()
            FuncionarioController.remover_funcionario(id, False, login_funcionario)
            titulo('Funcionário removido com sucesso!')

        # Ver funcionário
        case 4:
            titulo('Selecione o Funcionário')
            ids = FuncionarioController.listar_funcionarios(False)
            if len(ids) == 0:
                titulo('Ops, sem nenhum funcionário!')
                return False
            id_funcionario = ids[int(input('ID: '))-1]

            FuncionarioController.ver_funcionario(id_funcionario, False)

        # Voltar
        case 5:
            print('-'*30)
            return False
        
        # Opção Inválida
        case other:
            raise ValueError('Opção inválida!')


def menu_produtos(login_funcionario: LoginFuncionario) -> bool | None:
    acoes = ['Categorias', 'Cadastrar Produto', 'Alterar Produto', 'Remover Produto', 'Ver Produto',
            'Adicionar ao Estoque', 'Verificar as Validades', 'Retirar os Vencidos do Estoque', 'Voltar']
    listar_acoes(acoes)
    
    decisao = int(input('O que você quer fazer? '))
    print()
    match decisao:
        # Opções de categorias
        case 1:
            acoes = ['Cadastrar Categoria', 'Alterar Categoria', 'Remover Categoria', 'Voltar']
            listar_acoes(acoes)

            decisao = int(input('O que você quer fazer? '))
            print()
            match decisao:
                # Cadastrar categoria
                case 1:
                    nome = str(input('Nome da Categoria: ')).strip()
                    CategoriaController.cadastrar_categoria(nome)
                    titulo('Categoria Cadastrada com sucesso!')
                
                # Alterar categoria
                case 2:
                    ids = CategoriaController.listar_categorias()
                    id_categoria = ids[int(input('ID: '))-1]

                    nome = str(input('Novo nome: ')).strip()
                    CategoriaController.alterar_categoria(id_categoria, nome)
                    titulo('Categoria alterada com sucesso!')
                
                # Remover Categoria
                case 3:
                    ids = CategoriaController.listar_categorias()
                    id_categoria = ids[int(input('ID: '))-1]

                    print('-'*70)
                    x = False
                    while True:
                        match str(input('Tem certeza que deseja remover esta categoria? [S/N] ')).strip().upper():
                            case 'S':
                                print('-'*70)
                                break
                            case 'N':
                                x = True
                                print('-'*70)
                                break
                            case other:
                                titulo('Resposta inválida!')
                    if x:
                        return False

                    CategoriaController.remover_categoria(id_categoria)
                    titulo('Categoria removida com sucesso!')
                
                # Voltar
                case 4:
                    print('-'*30)
                    return False

                # Opção inválida
                case other:
                    raise ValueError('Opção inválida!')

        # Cadastrar um produto
        case 2:
            titulo('Selecione a Categoria:', '=')
            ids = EstoqueController.listar_categorias()
            id_categoria = ids[int(input('ID: '))-1]

            titulo('Dados do Produto', '-')

            nome = str(input('Nome: ')).strip()
            marca = str(input('Marca: ')).strip()
            preco = float(input('Preço: R$'))

            quantidade = []
            titulo('Quantidade dos Produtos:', '-')
            while True:
                quantidade.append([str(input('Data de Validade: ')).strip(),
                                    int(input('Quantidade: '))])
                if str(input('Mais? [S/N] ')).upper().strip() == 'N':
                    break
            
            titulo('Selecione o Fornecedor:', '=')
            ids = FornecedorController.listar_fornecedores()
            id_fornecedor = ids[int(input('ID: '))-1]

            EstoqueController.cadastrar_produto(id_categoria, nome, marca, preco, quantidade, id_fornecedor)
            titulo('Produto Cadastrado com Sucesso!')

        # Alterar um produto
        case 3:
            titulo('Selecione a Categoria:', '=')
            ids = EstoqueController.listar_categorias()
            id_categoria = ids[int(input('ID: '))-1]

            titulo('Selecione o Produto:', '=')
            ids = EstoqueController.listar_produtos(id_categoria)
            if len(ids) == 0:
                titulo('Ops, sem nenhum produto nessa categoria!', '*', comprimento=100, justificar=True)
                print('\n')
                return False
            id_produto = ids[int(input('ID: '))-1]

            acoes = ['Categoria', 'Nome', 'Marca', 'Preço',
                        'Quantidade', 'Fornecedor', 'Pronto']
            alteracoes = {}
            
            while True:
                print('-'*30)
                print('Você deseja alterar:')
                listar_acoes(acoes)
                decisao = int(input('Opção: '))
                print()
                match decisao:
                    case 1:
                        ids = CategoriaController.listar_categorias()
                        alteracoes.update(id_categoria=ids[int(input('ID: '))-1])
                    case 2:
                        alteracoes.update(nome=str(input('Nome: ').strip()))
                    case 3:
                        alteracoes.update(marca=str(input('Marca: ')).strip())
                    case 4:
                        alteracoes.update(preco=float(input('Preço: ').strip()))
                    case 5:
                        quantidade = []
                        while True:
                            quantidade.append([str(input('Data de Validade: ')).strip(),
                                                int(input('Quantidade: '))])
                            if str(input('Mais? [S/N] ')).upper().strip() == 'N':
                                break
                        alteracoes.update(quantidade=quantidade)
                    case 6:
                        titulo('Selecione o Fornecedor:', '=')
                        ids = FornecedorController.listar_fornecedores()
                        alteracoes.update(id_fornecedor=ids[int(input('ID: '))-1])
                    case 7:
                        break
            
            EstoqueController.alterar_produto(id_produto, id_categoria, **alteracoes)
            titulo('Produtos Alterado com Sucesso!')

        # Remover um produto
        case 4:
            titulo('Selecione a Categoria:', '=')
            ids = EstoqueController.listar_categorias()
            id_categoria = ids[int(input('ID: '))-1]

            titulo('Selecione o Produto:', '=')
            ids = EstoqueController.listar_produtos(id_categoria)
            if len(ids) == 0:
                titulo('Ops, sem nenhum produto nessa categoria!', '*', comprimento=100, justificar=True)
                print('\n')
                return False
            id_produto = ids[int(input('ID: '))-1]
            print()

            print('-'*70)
            x = False
            while True:
                match str(input('Tem certeza que deseja remover este Produto? [S/N] ')).strip().upper():
                    case 'S':
                        print('-'*70)
                        break
                    case 'N':
                        x = True
                        print('-'*70)
                        break
                    case other:
                        titulo('Resposta inválida!')
            if x:
                return False

            EstoqueController.remover_produto(id_categoria, id_produto)
            titulo('Produto Removido com Sucesso!')

        # Ver produto
        case 5:
            titulo('Selecione a Categoria:', '=')
            ids = EstoqueController.listar_categorias()
            id_categoria = ids[int(input('ID: '))-1]

            titulo('Selecione o Produto:', '=')
            ids = EstoqueController.listar_produtos(id_categoria)
            if len(ids) == 0:
                titulo('Ops, sem nenhum produto nessa categoria!', '*', comprimento=100, justificar=True)
                return False
            id_produto = ids[int(input('ID: '))-1]
            print()

            EstoqueController.ver_produto(id_categoria, id_produto)

        # Adicionar ao estoque
        case 6:
            titulo('Selecione a Categoria:', '=')
            ids = EstoqueController.listar_categorias()
            id_categoria = ids[int(input('ID: '))-1]

            titulo('Selecione o Produto:', '=')
            ids = EstoqueController.listar_produtos(id_categoria)
            if len(ids) == 0:
                titulo('Ops, sem nenhum produto nessa categoria!', '*', comprimento=100, justificar=True)
                print('\n')
                return False
            id_produto = ids[int(input('ID: '))-1]
            print()

            quantidade = []
            titulo('Informe as Datas de Validade')
            while True:
                quantidade.append([str(input('Data de Validade: ')).strip(),
                                int(input('Quantidade: '))])
                match str(input('Mais? [S/N]')).strip().upper():
                    case 'S':
                        continue
                    case 'N':
                        pass
                    case other:
                        titulo('Resposta Inválida!')
                break

            EstoqueController.adicionar_quantidade(id_categoria, id_produto, quantidade, None, False)
            titulo('Produtos adicionados ao estoque com sucesso!')

        # Verificar as validades
        case 7:
            titulo('Verificando os Produtos', '*')
            match EstoqueController.verificar_validade():
                case False:
                    print('Nenhum produto vencido encotrado!')
                case other:
                    print(f'{other} produtos vencidos encontrados... Gerando um relatório completo!')
                    sleep(3)
                    titulo(EstoqueController.gerar_relatorio_vencidos(), '-')
                    sleep(3)

        # Retirar os vencidos do estoque
        case 8:
            if not login_funcionario.admin:
                titulo('Somente um ADMIN pode fazer isso!', '*')
                return False
            
            while True:
                match str(input('Você tem certeza disto? [S/N] ')).strip().upper():
                    case 'S':
                        print('\n\nGerando um relório primeiro...')
                        sleep(3)
                        titulo(EstoqueController.gerar_relatorio_vencidos(), '-', comprimento=50, justificar=True)
                        sleep(3)

                        codigo = EstoqueDal.ler_arquivo()
                        EstoqueDal.remover_vencidos(codigo, None)
                        titulo('Produtos Vencidos Removidos do Estoque!', comprimento=50, justificar=True)
                    case 'N':
                        pass
                    case other:
                        titulo('Resposta Inválida!')
                        continue
                break

        # Voltar
        case 9:
            print('-'*30)
            return False
        
        # Opção Inválida
        case other:
            raise ValueError('Opção inválida!')


def menu_fornecedores() -> bool | None:
    acoes = ['Lotes', 'Cadastrar Fornecedor', 'Alterar Fornecedor', 'Remover Fornecedor', 'Ver Fornecedor', 'Voltar']
    listar_acoes(acoes)
    
    decisao = int(input('O que você quer fazer? '))
    print()
    match decisao:
        # Opções de lotes
        case 1:
            if not menu_lotes():
                return False

        # Cadastrar fornecedor
        case 2:
            titulo('Dados do Fornecedor:')

            nome = str(input('Nome: ')).strip()
            telefone = str(input('Telefone [com DDD]: '))
            telefone = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            email = str(input('Email: ')).strip()
            cnpj = str(input('CNPJ: ')).strip()
            cnpj = cnpj.replace(' ', '').replace('.', '').replace('/', '').replace('-', '')
            cnpj = "{}.{}.{}/{}-{}".format(cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])

            FornecedorController.cadastrar_fornecedor(nome, telefone, email, cnpj)
            titulo('Fornecedor cadastrado com sucesso!')
        
        # Alterar fornecedor
        case 3:
            titulo('Selecione o Fornecedor:', '=')
            ids = FornecedorController.listar_fornecedores()
            if len(ids) == 0:
                titulo('Ops, sem nenhum fornecedor!')
                return False
            id_fornecedor = ids[int(input('ID: '))-1]

            acoes = ['Nome', 'Telefone', 'Email', 'CNPJ', 'Pronto']
            alteracoes = {}
            
            while True:
                print('-'*30)
                print('Você deseja alterar:')
                listar_acoes(acoes)
                decisao = int(input('Opção: '))
                print()
                match decisao:
                    case 1:
                        alteracoes.update(nome=str(input('Nome: ').strip()))
                    case 2:
                        telefone = str(input('Telefone [com DDD]: '))
                        telefone = telefone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                        alteracoes.update(telefone=telefone)
                    case 3:
                        alteracoes.update(email=str(input('Email: ')).strip())
                    case 4:
                        cnpj = str(input('CNPJ: ')).strip()
                        cnpj = cnpj.replace(' ', '').replace('.', '').replace('/', '').replace('-', '')
                        cnpj = "{}.{}.{}/{}-{}".format(cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])
                        alteracoes.update(cnpj=cnpj)
                    case 5:
                        break
            
            FornecedorController.alterar_fornecedor(id_fornecedor, **alteracoes)
            titulo('Fornecedor alterado com sucesso!')

        # Remover fornecedor
        case 4:
            titulo('Selecione o Fornecedor:', '=')
            ids = FornecedorController.listar_fornecedores()
            if len(ids) == 0:
                titulo('Ops, sem nenhum fornecedor!')
                return False
            id_fornecedor = ids[int(input('ID: '))-1]

            print('-'*70)
            x = False
            while True:
                match str(input('Tem certeza que deseja remover este fornecedor? [S/N] ')).strip().upper():
                    case 'S':
                        print('-'*70)
                        break
                    case 'N':
                        x = True
                        print('-'*70)
                        break
                    case other:
                        titulo('Resposta inválida!')
            if x:
                return False
            
            FornecedorController.remover_fornecedor(id_fornecedor)
            titulo('Fornecedor removido com sucesso!')

        # Ver fornecedor
        case 5:
            titulo('Selecione o Fornecedor:', '=')
            ids = FornecedorController.listar_fornecedores()
            if len(ids) == 0:
                titulo('Ops, sem nenhum fornecedor!')
                return False
            id_fornecedor = ids[int(input('ID: '))-1]

            FornecedorController.ver_fornecedor(id_fornecedor)

        # Voltar
        case 6:
            print('-'*30)
            return False
        
        # Opção Inválida
        case other:
            raise ValueError('Opção inválida!')


def menu_lotes() -> bool | None:
    acoes = ['Lote Recebido', 'Cadastrar Lote', 'Alterar Lote', 'Remover Lote', 'Ver Lote', 'Voltar']
    listar_acoes(acoes)
    
    decisao = int(input('O que você quer fazer? '))
    print()
    match decisao:
        # Receber lote
        case 1:
            titulo('Selecione o Fornecedor')
            ids = FornecedorController.listar_fornecedores()
            id_fornecedor = ids[int(input('ID: '))-1]

            titulo('Selecione o Lote')
            ids = FornecedorController.listar_lotes(id_fornecedor)
            id_lote = ids[int(int(input('ID: '))-1)]

            quantidade = []
            titulo('Informe os Produtos pela Data de Validade')
            while True:
                quantidade.append([str(input('Data de Validade: ')).strip(),
                                int(input('Quantidade: '))])
                match str(input('Mais? [S/N]')).strip().upper():
                    case 'S':
                        continue
                    case 'N':
                        pass
                    case other:
                        titulo('Resposta Inválida!')
                break

            FornecedorController.lote_recebido(id_fornecedor, id_lote, quantidade)
            titulo('Lote Recebido com Sucesso!')

        # Cadastrar lote
        case 2:
            titulo('Selecione o Fornecedor')
            ids = FornecedorController.listar_fornecedores()
            id_fornecedor = ids[int(input('ID: '))-1]

            titulo('Dados do Lote')

            print('Selecione a categoria:\n')
            ids = EstoqueController.listar_categorias()
            id_categoria = ids[int(input('ID: '))-1]

            titulo('Selecione o produto:', '-', comprimento=100, justificar=True)
            print('* O produto que vai ser recebido no lote precisa estar cadastrado no sistema,\n',
            'você pode cadastra-lo com uma quantidade igual a zero ;)')
            print('-'*100)
            ids = EstoqueController.listar_produtos(id_categoria)
            id_produto = ids[int(input('ID: '))-1]
            print('-'*100)

            quantidade = int(input('Quantidade de Produtos: '))
            preco_lote = float(input('Preço total do lote: R$'))
            
            if str(input('Já existe uma data de entrega? [S/N] ')).strip().upper() == 'S':
                tempo = {
                    'intervalo': int(input('Intervalo entre os lotes: [em dias] ')),
                    'proximo':   str(input('Data da primeira entrega: '))
                }

            FornecedorController.cadastrar_lote(id_fornecedor, preco_lote, id_categoria, id_produto,
                                                quantidade, tempo)
            titulo('Lote cadastrado com sucesso!')

        # Alterar lote
        case 3:
            titulo('Selecione o Fornecedor:', '=')
            ids = FornecedorController.listar_fornecedores()
            if len(ids) == 0:
                titulo('Ops, sem nenhum fornecedor!')
                return False
            id_fornecedor = ids[int(input('ID: '))-1]
            
            ids = FornecedorController.listar_lotes(id_fornecedor)
            if len(ids) == 0:
                titulo('Ops, sem nenhum lote!')
                return False
            id_lote = ids[int(input('Selecione o Lote: '))-1]
            print('-'*100)

            acoes = ['Produto','Preço Lote', 'Quantidade de Produtos', 'Intervalo/Próximo Lote', 'Pronto']
            alteracoes = {}
            
            while True:
                print('-'*30)
                print('Você deseja alterar:')
                listar_acoes(acoes)
                decisao = int(input('Opção: '))
                print()
                match decisao:
                    # Produto
                    case 1:
                        titulo('Selecione a Categoria')
                        ids = EstoqueController.listar_categorias()
                        id_categoria = ids[int(input('ID: '))-1]

                        titulo('Selecione o Produto')
                        ids = EstoqueController.listar_produtos(id_categoria)
                        id_produto = ids[int(input('ID: '))-1]

                        alteracoes.update(id_categoria=id_categoria, id_produto=id_produto)
                    
                    # Preço lote
                    case 2:
                        alteracoes.update(preco_lote=float(input('Preço do Lote: R$')))
                    
                    # Quantidade de Produtos
                    case 3:
                        alteracoes.update(quantidade=int(input('Quantidade de Produtos: ')))
                    
                    # Intervalo/Próximo Lote
                    case 4:
                        if str(input('Valor nulo? [S/N] ')).strip().upper() == 'S':
                            alteracoes.update(tempo=None)
                            continue

                        alteracoes.update(tempo={
                            'intervalo': int(input('Intervalo entre os lotes: [em dias] ')),
                            'proximo':   str(input('Data da primeira entrega: '))
                        })

                    # Pronto
                    case 5:
                        break
            
            FornecedorController.alterar_lote(id_fornecedor, id_lote, **alteracoes)
            titulo('Lote alterado com sucesso!')

        # Remover lote
        case 4:
            titulo('Selecione o Fornecedor')
            ids = FornecedorController.listar_fornecedores()
            if len(ids) == 0:
                titulo('Ops, sem nenhum fornecedor!')
                return False
            id_fornecedor = ids[int(input('ID: '))-1]

            titulo('Selecione o Lote')
            ids = FornecedorController.listar_lotes(id_fornecedor)
            if len(ids) == 0:
                titulo('Ops, sem nenhum lote!')
                return False
            id_lote = ids[int(input('ID: '))-1]

            print('-'*100)
            x = False
            while True:
                match str(input('Tem certeza que deseja remover este Lote? [S/N] ')).strip().upper():
                    case 'S':
                        print('-'*70)
                        break
                    case 'N':
                        x = True
                        print('-'*70)
                        break
                    case other:
                        titulo('Resposta inválida!')
            if x:
                return False
            
            FornecedorController.remover_lote(id_fornecedor, id_lote)
            titulo('Lote removido com sucesso!')

        # Ver lote
        case 5:
            titulo('Selecione o Fornecedor:', '=')
            ids = FornecedorController.listar_fornecedores()
            if len(ids) == 0:
                titulo('Ops, sem nenhum fornecedor!')
                return False
            id_fornecedor = ids[int(input('ID: '))-1]
            
            ids = FornecedorController.listar_lotes(id_fornecedor)
            if len(ids) == 0:
                titulo('Ops, sem nenhum lote!')
                return False
            id_lote = ids[int(input('Selecione o Lote: '))-1]
            print('-'*100)

            FornecedorController.ver_lote(id_fornecedor, id_lote)

        # Voltar
        case 6:
            print('-'*30)
            return False
        
        # Opção Inválida
        case other:
            raise ValueError('Opção inválida!')


def menu_venda(login_funcionario: LoginFuncionario) -> bool | None:
    acoes = ['Caixas', 'Cadastrar Venda', 'Cancelar Venda', 'Ver Venda', 'Voltar']
    listar_acoes(acoes)

    decisao = int(input('O que você quer fazer? '))
    print()
    match decisao:
        # Opções de caixa
        case 1:
            acoes = ['Selecionar Caixa', 'Valor no Caixa', 'Cadastrar Caixa', 'Remover Caixa', 'Voltar']
            listar_acoes(acoes)

            decisao = int(input('O que você quer fazer? '))
            print()
            match decisao:
                # Selecionar caixa
                case 1:
                    titulo('Selecione o Caixa')
                    numeros = CaixaController.listar_caixas(False)
                    numero_caixa = numeros[int(input('ID: '))-1]

                    login_funcionario = CaixaController.definir_caixa(numero_caixa, login_funcionario, True)
                    titulo('Caixa Definido com Sucesso!')

                # Valor no caixa
                case 2:
                    titulo('Selecione o Caixa', comprimento=50, justificar=True)
                    ids = CaixaController.listar_caixas(True)
                    numero_caixa = ids[int(input('ID: '))-1]
                    print()

                    acoes = ['Sacar Valor', 'Depositar Valor', 'Definir Valor']
                    while True:
                        listar_acoes(acoes)
                        decisao = int(input('O que você quer fazer? '))
                        print('='*50)
                        match decisao:
                            case 1:
                                valor = float(input('Sacar R$'))
                                metodo = 'saque'
                            case 2:
                                valor = float(input('Depositar R$'))
                                metodo = 'deposito'
                            case 3:
                                valor = float(input('Valor no Caixa: R$'))
                                metodo = None
                            case other:
                                titulo('Resposta Inválida!')
                                continue
                        break
                        
                    CaixaController.alterar_caixa(numero_caixa, metodo, valor_no_caixa=valor)
                    titulo('Valor Alterado com Sucesso!')

                # Cadastrar caixa
                case 3:
                    numero_caixa = int(input('Número do Caixa: '))
                    valor_no_caixa = float(input('Valor no Caixa: R$'))

                    CaixaController.cadastrar_caixa(numero_caixa, valor_no_caixa)
                    titulo('Caixa Cadastrado com Sucesso!')
                
                # Remover caixa
                case 4:
                    titulo('Selecione o Caixa')
                    ids = CaixaController.listar_caixas(True)
                    numero_caixa = ids[int(input('ID: '))-1]
                    print()

                    print('-'*70)
                    x = False
                    while True:
                        match str(input('Tem certeza que deseja remover este Caixa? [S/N] ')).strip().upper():
                            case 'S':
                                print('-'*70)
                                break
                            case 'N':
                                x = True
                                print('-'*70)
                                break
                            case other:
                                titulo('Resposta inválida!')
                    if x:
                        return False

                    CaixaController.remover_caixa(numero_caixa)
                    titulo('Caixa removido com sucesso!')
                
                # Voltar
                case 5:
                    print('-'*30)
                    return False

                # Opção inválida
                case other:
                    raise ValueError('Opção inválida!')

        # Cadastrar venda
        case 2:
            if not login_funcionario.caixa:
                titulo('Nenhum Caixa Selecionado!')
                return False

            titulo(f'Cadastrar Venda | Caixa Nº{login_funcionario.caixa.numero_caixa} | Valor Caixa R${login_funcionario.caixa.valor_no_caixa:.2f}')
            print('Passar os produtos:\n')

            carrinho = Carrinho([], 0)
            while True:
                id_produto = int(input('ID do Produto: '))
                quantidade = int(input('Quantidade de Produtos: '))

                print('-'*30)
                match str(input('Mais produtos? [S/N] ')).strip().upper():
                    case 'S':
                        carrinho.produtos.append(CaixaController.passar_produto(id_produto, quantidade))
                        continue
                    case 'N':
                        carrinho.produtos.append(CaixaController.passar_produto(id_produto, quantidade))
                        break
                    case other:
                        titulo('Resposta Inválida!')
            carrinho.preco_total = preco_total(carrinho.produtos)
            print('-'*30)

            valor_recebido = float(input('Valor Recebido: R$'))

            print('-'*30)
            while True:
                match str(input('CPF do Cliente? [S/N] ')).strip().upper():
                    case 'S':
                        cpf = str(input('\nCPF: ')).replace('', ' ').replace('.', '').replace('-', '')
                        cpf = '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])
                        break
                    case 'N':
                        cpf = None
                        break
                    case other:
                        titulo('Resposta Inválida!')
            
            while True:
                try:
                    troco = VendaController.venda(login_funcionario, login_funcionario.caixa.numero_caixa,
                                                carrinho, valor_recebido, cpf)
                    break
                except ValueError as arg:
                    titulo(f'{arg.args[0]}{arg.args[1]}', '*')
                    match str(input('Receber outro valor: [S/N] ')).strip().upper():
                        case 'S':
                            valor_recebido = float(input('Valor Recebido: R$'))
                            continue
                        case 'N':
                            titulo('Não foi possível realizar a venda!')
                            return False
                        case other:
                            titulo('Resposta Inválida!')

            titulo(f'Venda Feita com Sucesso | Troco: R${troco:.2f}')

        # Cancelar venda
        case 3:
            acoes = ['Vendas Físicas', 'Vendas Online']
            listar_acoes(acoes)

            decisao = int(input('Tipo da Venda: '))
            while True:
                match decisao:
                    case 1:
                        tipo_venda = 'fisica'
                    case 2:
                        tipo_venda = 'online'
                    case other:
                        titulo('Resposta Inválida!')
                        continue
                break
            print()
            
            datas = None
            while True:
                match str(input('Data entre as vendas? [S/N] ')).strip().upper():
                    case 'S':
                        try:
                            datas = (
                                datetime.datetime.strptime(str(input('Início: [dia/mês/ano] ')), '%d/%m/%Y'),
                                datetime.datetime.strptime(str(input('Fim: [dia/mês/ano] ')), '%d/%m/%Y')
                            )
                        except:
                            continue
                    case 'N':
                        pass
                    case other:
                        titulo('Reposta Inválida!')
                        continue
                break

            ids = VendaController.listar_vendas(tipo_venda, datas)
            id_venda = ids[int(input('ID: '))-1]

            print('-'*70)
            x = False
            while True:
                match str(input('Tem certeza que deseja cancelar está venda? [S/N] ')).strip().upper():
                    case 'S':
                        print('-'*70)
                        break
                    case 'N':
                        x = True
                        print('-'*70)
                        break
                    case other:
                        titulo('Resposta inválida!')
            if x:
                return False
            
            print()
            codigo = VendaDal.ler_arquivo()
            VendaDal.remover_venda(id_venda, codigo, True if tipo_venda == 'online' else False)
            titulo('Venda cancelada com sucesso!')

        # Ver Venda
        case 4:
            acoes = ['Vendas Físicas', 'Vendas Online']
            listar_acoes(acoes)

            decisao = int(input('Tipo da Venda: '))
            while True:
                match decisao:
                    case 1:
                        tipo_venda = 'fisica'
                    case 2:
                        tipo_venda = 'online'
                    case other:
                        titulo('Resposta Inválida!')
                        continue
                break
            print()

            ids = VendaController.listar_vendas(tipo_venda)
            id_venda = ids[int(input('ID: '))-1]

            if tipo_venda == 'fisica':
                VendaController.ver_venda_fisica(id_venda)
            else:
                VendaController.ver_venda_online(id_venda)

        # Voltar
        case 5:
            print('-'*30)
            return False
        
        # Opção Inválida
        case other:
            raise ValueError('Opção inválida!')


def menu_relatorio():
    acoes = ['Relatório de Vendas', 'Relatório dos Produtos Vencidos', 'Voltar']
    listar_acoes(acoes)
    
    decisao = int(input('O que você quer fazer? '))
    print()
    match decisao:
        # Vendas
        case 1:
            while True:
                match str(input('Quer gerar um arquivo TXT? [S/N] ')).strip().upper():
                    case 'S':
                        gerar_txt = True
                    case 'N':
                        gerar_txt = False
                    case other:
                        titulo('Resposta Inválida1')
                        continue
                break
            
            titulo('Você quer um relatório de:')
            acoes = ['Todas vendas físicas', 'Todas vendas online', 'Todas vendas']
            
            while True:
                listar_acoes(acoes)
                decisao = int(input('R: '))
                print()
                match decisao:
                    case 1:
                        chave = 'fisica'
                    case 2:
                        chave = 'online'
                    case 3:
                        chave = None
                    case other:
                        titulo('Reposta Inválida!')
                        continue
                break

            while True:
                match str(input('Intervalo entre as vendas? [S/N] ')).strip().upper():
                    case 'S':
                        try:
                            datas = (
                                datetime.datetime.strptime(str(input('Início: [dia/mês/ano] ')), '%d/%m/%Y'),
                                datetime.datetime.strptime(str(input('Fim: [dia/mês/ano] ')), '%d/%m/%Y')
                            )
                        except:
                            continue
                    case 'N':
                        datas = None
                    case other:
                        continue
                break
            
            relatorio = VendaController.gerar_relatorio_vendas(chave, datas, gerar_txt)
            if gerar_txt:
                titulo(relatorio)
            else:
                titulo('Início do Relatório', '*', comprimento=100, justificar=True)
                print(relatorio)
                titulo('Fim do Relatório', '*', comprimento=100, justificar=True)

        # Produtos vencidos
        case 2:
            titulo(EstoqueController.gerar_relatorio_vencidos(), '*')
        
        # Voltar
        case 3:
            print('-'*30)
            return False
        
        # Opção Inválida
        case other:
            raise ValueError('Opção inválida!')


# --------------------------------------------------
# --------------------------------------------------


def menu_principal_adm(login_funcionario: LoginFuncionario):
    while True:
        acoes = ['Administradores', 'Funcionários', 'Fornecedores', 'Produtos', 'Vendas', 'Relatórios', 'Logout', 'Sair']
        listar_acoes(acoes)

        try:
            decisao = int(input('O que você quer fazer? '))
            print()
            match decisao:
                
                # Gerenciar ADMs
                case 1:
                    if not menu_adm(login_funcionario):
                        continue
                
                # Gerenciar funcionários
                case 2:
                    if not menu_funcionarios():
                        continue
                
                # Gerencias Fornecedores
                case 3:
                    if not menu_fornecedores():
                        continue

                # Gerenciar produtos
                case 4:
                    if not menu_produtos(login_funcionario):
                        continue
                
                # Gerenciar vendas
                case 5:
                    if not menu_venda(login_funcionario):
                        continue

                # Relatórios
                case 6:
                    if not menu_relatorio():
                        continue

                # Fazer logout
                case 7:
                    return 'LOGOUT'

                # Sair
                case 8:
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


def menu_principal_func(login_funcionario: LoginFuncionario):
    while True:
        acoes = ['Produtos', 'Vendas', 'Logout', 'Sair']
        listar_acoes(acoes)

        try:
            decisao = int(input('O que você quer fazer? '))
            print()
            match decisao:
                # Gerenciar produtos
                case 1:
                    if not menu_produtos(login_funcionario):
                        continue

                # Gerenciar vendas
                case 2:
                    if not menu_venda(login_funcionario):
                        continue

                # Fazer logout
                case 3:
                    return 'LOGOUT'

                # Sair
                case 4:
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
        login_funcionario = login()
        if login_funcionario.admin:
            if menu_principal_adm(login_funcionario) == 'LOGOUT':
                continue
        else:
            if menu_principal_func(login_funcionario) == 'LOGOUT':
                continue
        break
