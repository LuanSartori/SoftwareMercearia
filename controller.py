from operator import itemgetter
import datetime

from model import *
from dal import *
from utils import *


# --------------------------------------------------
# --------------------------------------------------


class CategoriaController():
    @staticmethod
    def cadastrar_categoria(categoria: str) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()

        if CategoriaDal.pesquisar_arquivo('categoria', categoria, codigo):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')
        
        
        id = IdDal.gerar_id('id_categoria')
        categoria = Categoria(categoria, id)
        return CategoriaDal.salvar_categoria(categoria, codigo, codigo_estoque)


    @staticmethod
    def alterar_categoria(id_categoria: int, categoria: str) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()

        index_categoria = CategoriaDal.pesquisar_arquivo('id', str(id_categoria), codigo)
        if not index_categoria:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)

        if CategoriaDal.pesquisar_arquivo('categoria', categoria, codigo):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')


        categoria = Categoria(categoria, id_categoria)
        return CategoriaDal.alterar_categoria(index_categoria, categoria, codigo, codigo_estoque)


    @staticmethod
    def remover_categoria(id_categoria: int) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
            
        index = CategoriaDal.pesquisar_arquivo('id', str(id_categoria), codigo)
        if not index:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        
        if id_categoria == 0:
            raise ValueError(f'Não é possível remover a categoria "Nenhuma"')
        elif id_categoria == 1:
            raise ValueError(f'Não é possível remover a categoria: "vencidos')

        return CategoriaDal.remover_categoria(id_categoria, index, codigo, codigo_estoque)


# --------------------------------------------------
# --------------------------------------------------


class EstoqueController:
    @staticmethod
    def cadastrar_produto(id_categoria: int, nome: str, marca: str, preco: float, validade: str,
                          quantidade: int=None, id_fornecedor: int=None) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        if len(nome) > 40:
            raise ValueError('Este nome é grande demais')
        if len(marca) > 20:
            raise ValueError('O nome da marca é grande demais!')
        if not CategoriaDal.pesquisar_arquivo('id', id_categoria, codigo):
            raise IdError('Está categoria não existe!')
        
        index = EstoqueDal.pesquisar_categoria(codigo, produto.id_categoria)
        for p in codigo[index]['produtos']:
            if p['nome'] == nome:
                raise ValueError('Já existe um produto com esse nome')

        try:
            validade_obj = datetime.datetime.strptime(validade, '%d/%m/%Y')
            if validade_obj <= datetime.datetime.now():
                raise ValueError('O produto já está vencido!')
        except ValueError as arg:
            raise ValueError('Data de validade inválida!', arg)

        id = IdDal.gerar_id('id_produto')            
        produto = Produto(id, id_categoria, nome, marca, preco, validade, quantidade, id_fornecedor)
        return EstoqueDal.cadastrar_produto(produto, codigo_estoque)


    @staticmethod
    def alterar_produto(id_produto:int, id_categoria_atual: int, **kwargs) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()

        if not EstoqueDal.ler_produto_por_categoria(id_categoria_atual, id_produto, codigo_estoque, True):
            raise IdError('Não existe uma produto com esse ID', id_produto)
        if not CategoriaDal.pesquisar_arquivo('id', str(id_categoria_atual), codigo):
            raise IdError('Não existe uma categoria com esse ID', id_categoria_atual)
        
        if kwargs.get('nome') != None and len(kwargs.get('nome')) > 40:
            raise ValueError('Este nome é grande demais!')
        if kwargs.get('marca') != None and len(kwargs.get('marca')) > 20:
            raise ValueError('O nome da marca é grande demais!')
        
        return EstoqueDal.alterar_produto(id_produto, id_categoria_atual, codigo_estoque, **kwargs)


    @staticmethod
    def remover_produto(id_categoria: int, id_produto: int) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_fornecedores = FornecedorDal.ler_arquivo()
        
        if not EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo_estoque, True):
            raise IdError('Não existe uma produto com esse ID', id_produto)
        if not CategoriaDal.pesquisar_arquivo('id', str(id_categoria), codigo):
            raise IdError('Não existe uma categoria com esse ID', id_categoria)

        # validando se o produto está vinculado a um lote
        for i_f, fornecedor in enumerate(codigo_fornecedores):
            for i_l, lote in enumerate(fornecedor['lotes']):
                if lote['id_produto'] == id_produto:
                    raise Exception( {'id_fornecedor': fornecedor['id'], 'id_lote': lote['id_lote']} )
        
        return EstoqueDal.remover_produto(id_produto, id_categoria, codigo_estoque)


    @staticmethod
    def verificar_validade() -> str:
        codigo = EstoqueDal.ler_arquivo()

        data_hoje = datetime.datetime.now()
        x = False

        for index_categoria, categoria in enumerate(codigo):

            # sem contar a categoria vencidos
            if index_categoria == 1:
                continue
            
            for index_produto, produto in enumerate(categoria['produtos']):

                # transforma todas as datas em objetos datetime e os ordena
                for i, q in enumerate(produto['quantidade']):
                    d = datetime.datetime.strptime(q[0], '%d/%m/%Y')
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d

                codigo[index_categoria]['produtos'][index_produto]['quantidade'] = sorted(
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'],
                    key=itemgetter(0))

                # faz a verificacao dos produtos vencidos
                for quantidade in produto['quantidade']:
                    if quantidade[0] <= data_hoje:
                        x = True

                        quantidade[0] = datetime.datetime.strftime(quantidade[0], '%d/%m/%Y')
                        codigo = EstoqueDal.transferir_vencido(produto, quantidade, codigo)

                        codigo[index_categoria]['produtos'][index_produto]['quantidade'].pop(0)

                # transforma todos os objetos datetime em string para armazenar no banco de dados
                for i, q in enumerate(produto['quantidade']):
                    d = datetime.datetime.strftime(q[0], '%d/%m/%Y')
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d
        
        EstoqueDal.salvar_arquivo(codigo)
        return 'Produtos vencidos removidos!' if x else 'Sem produtos vencidos ;)'


    @staticmethod
    def adicionar_quantidade(id_categoria: int, id_produto: int, quantidade: list, codigo: json) -> json:
        index_categoria = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
        index_produto, produto = EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo, retorna_obj=False)

        for v in quantidade:
            for i, q in enumerate(codigo[index_categoria]['produtos'][index_produto]['quantidade']):
                if v[0] == q[0]:
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][1] += v[1]
                    break
            else:
                codigo[index_categoria]['produtos'][index_produto]['quantidade'].append(v)

        # transforma todas as datas em objetos datetime e os ordena
        for i, q in enumerate(produto['quantidade']):
            d = datetime.datetime.strptime(q[0], '%d/%m/%Y')
            codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d

        codigo[index_categoria]['produtos'][index_produto]['quantidade'] = sorted(
            codigo[index_categoria]['produtos'][index_produto]['quantidade'],
            key=itemgetter(0))
        
        # transforma todos os objetos datetime em string para armazenar no banco de dados
        for i, q in enumerate(produto['quantidade']):
            d = datetime.datetime.strftime(q[0], '%d/%m/%Y')
            codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d

        return codigo


    @staticmethod
    def remover_quantidade(id_categoria: int, id_produto: int, quantidade: int, codigo: json) -> json:
        index_categoria = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
        index_produto, produto = EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo, False)

        if contar_quantidade(produto) < quantidade:
            raise ValueError('Faltam produtos no estoque!')

        pop_list = []
        for i, q in enumerate(codigo[index_categoria]['produtos'][index_produto]['quantidade']):
            if q[1] > quantidade:
                codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][1] -= quantidade
                break
            if q[1] == quantidade:
                pop_list.append(i)
                break
            if q[1] < quantidade:
                quantidade -= q[1]
                pop_list.append(i)
        
        pop_list.sort(reverse=True)
        for p in pop_list:
            codigo[index_categoria]['produtos'][index_produto]['quantidade'].pop(p)
        
        return codigo
# --------------------------------------------------
# --------------------------------------------------


class FornecedorController:
    @staticmethod
    def cadastrar_fornecedor(nome: str, telefone: str, email: str, cnpj: str=None) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        # !!! no caso de CNPJ duplicado enviar um alerta para o chefe
        if cnpj != None:
            for f in codigo:
                if f['cnpj'] == cnpj:
                    raise ValueError('Já existe um fornecedor cadastrado com este CNPJ!')

        if (not nome) or 5 > len(nome) > 50:
            raise ValueError('Nome inválido!')
        if nome.isnumeric():
            raise TypeError('O nome não pode ser um número!')

        telefone = formatar_telefone(telefone)
        if not telefone:
            raise ValueError('Telefone inválido!')

        if not email_valido(email):
            raise ValueError('Email inválido!')

        if not cnpj_valido(cnpj):
            raise ValueError('CNPJ inválido!')
        
        id = IdDal.gerar_id('id_fornecedor')
        fornecedor = Fornecedor(id, nome, telefone, email, cnpj)
        return FornecedorDal.cadastrar_fornecedor(fornecedor, codigo)
    

    @staticmethod
    def alterar_fornecedor(id_fornecedor, **kwargs) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID')
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError('Nome inválido!')

        if kwargs.get('telefone') != None:
            telefone = formatar_telefone(kwargs.get('telefone'))
            if not telefone:
                raise ValueError('Telefone inválido!')

        if kwargs.get('email') != None:
            if not email_valido(kwargs.get('email')):
                raise ValueError('Email inválido!')

        if kwargs.get('cnpj') != None:
            if not cnpj_valido(kwargs.get('cnpj')):
                raise ValueError('CNPJ inválido!')
        
        return FornecedorDal.alterar_fornecedor(id, codigo, **kwargs)
    

    @staticmethod
    def remover_fornecedor(id_fornecedor: int) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)

        return FornecedorDal.remover_fornecedor(id_fornecedor, codigo)
    

    @staticmethod
    def cadastrar_lote(id_fornecedor: int, preco_lote: float, id_categoria: int,
                       id_produto: id, quantidade: int, tempo: dict=None) -> bool:
        # Na view vai perguntar se o produto do lote já existe no sistema ou se ele quer criar um !!!

        codigo = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        
        if not EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo_estoque):
            raise IdError('Não existe um produto com este ID', id_produto)

        if tempo != None:
            try:
                validar_tempo(tempo)
            except:
                raise ValueError('Tempo inválido!')

        
        id = IdDal.gerar_id('id_lote')
        lote = Lote(id, preco_lote, id_produto, id_categoria, quantidade, tempo)
        return FornecedorDal.cadastrar_lote(id_fornecedor, lote, codigo)
    
    
    @staticmethod
    def alterar_lote(id_fornecedor: int, id_lote: int, **kwargs) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        if not FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False):
            raise IdError('Não existe um lote com esse ID neste fornecedor!')
        
        if kwargs.get('id_categoria') != None:
            codigo_estoque = EstoqueDal.ler_arquivo()
            if not codigo_estoque:
                raise ServerError('Não foi possível acessar o banco de dados!')
            
            if not EstoqueDal.ler_produto_por_categoria(kwargs.get('id_categoria'), kwargs.get('id_produto'), codigo_estoque):
                raise IdError('Não existe um produto com este ID', kwargs.get('id_produto'))
        
        return FornecedorDal.alterar_lote(id_fornecedor, id_lote, codigo, **kwargs)


    @staticmethod
    def remover_lote(id_fornecedor: int, id_lote: int) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        if not FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False):
            raise IdError('Não existe um lote com esse ID neste fornecedor!')
        
        return FornecedorDal.remover_lote(id_fornecedor, id_lote, codigo)
    

    @staticmethod
    def lote_recebido(id_fornecedor: int, id_lote: int, quantidade: list) -> bool:
        codigo_fornecedor = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo_fornecedor, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID!')
        if not FornecedorDal.ler_lote(id_fornecedor, codigo_fornecedor, id_lote):
            raise IdError('Não existe um lote com esse ID!')
        
        try:
            data_hoje = datetime.datetime.now()
            for v in quantidade:
                d = datetime.datetime.strptime(v[0], '%d/%m/%Y')
                if d <= data_hoje:
                    raise ValueError('Os produtos já estão vencidos')
        except:
            raise ValueError('Quantidade inválida!')
        
        index_f, fornecedor = FornecedorDal.ler_fornecedor(codigo_fornecedor, id_fornecedor, False)
        index_l, lote = FornecedorDal.ler_lote(id_fornecedor, codigo_fornecedor, id_lote, False)

        codigo_fornecedor[index_f]['lotes'][index_l]['tempo'] = proximo_lote(lote['tempo'])
        codigo_estoque = EstoqueController.adicionar_quantidade(lote['id_categoria'], lote['id_produto'], quantidade, codigo_estoque)

        return FornecedorDal.lote_recebido(codigo_fornecedor, codigo_estoque)


# --------------------------------------------------
# --------------------------------------------------


class FuncionarioController:
    @staticmethod
    def cadastrar_funcionario(nome: str, telefone: str, email: str, cpf: str,
                              cargo: str, senha: str, admin=False, posicao=None,
                              login: LoginFuncionario=None) -> bool:
        codigo = FuncionarioDal.ler_arquivo()
        
        valida_senha = senha_valida(senha)
        if valida_senha != True:
            raise ValueError(valida_senha)

        if admin:
            if posicao > login.posicao:
                raise ValueError('Não é possível cadastrar um ADM com a posição maior que a sua!')
            elif posicao <= 0:
                raise ValueError('Não é possível cadastrar um posição menor que 1')
        
        if (not nome) or 5 > len(nome) > 50:
            raise ValueError('Nome inválido!')
        if nome.isnumeric():
            raise TypeError('O nome não pode ser um número!')

        telefone = formatar_telefone(telefone)
        if not telefone:
            raise ValueError('Telefone inválido!')

        if not email_valido(email):
            raise ValueError('Email inválido!')
        
        # !!! no caso de CPF duplicado enviar um alerta para o chefe
        for f in codigo['funcionarios']:
            if f['cpf'] == cpf:
                raise ValueError('Já existe um funcionário cadastrado com este CPF!')
        for f in codigo['admins']:
            if f['cpf'] == cpf:
                raise ValueError('Já existe um ADM cadastrado com este CPF!')

        if not cpf_valido(cpf):
            raise ValueError('CPF inválido!')
        
        if admin:
            id = IdDal.gerar_id('id_admin')
        else:
            id = IdDal.gerar_id('id_funcionario')

        senha = hash_senha(senha, decode=True)
        funcionario = Funcionario(id, nome, cpf, cargo, senha, telefone, email)
        if admin:
            return FuncionarioDal.cadastrar_funcionario(funcionario, codigo, admin=True, posicao=posicao)
        else:
            return FuncionarioDal.cadastrar_funcionario(funcionario, codigo)


    @staticmethod
    def alterar_funcionario(id_funcionario: int, admin=False, posicao=None,
                            login: LoginFuncionario=None, **kwargs) -> bool:
        codigo = FuncionarioDal.ler_arquivo()

        if admin:
            if posicao > login.posicao:
                raise ValueError('Não é possível cadastrar um ADM com a posição maior que a sua!')
            elif posicao <= 0:
                raise ValueError('Não é possível cadastrar um posição menor que 1')
        
        if admin:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=True):
                raise IdError('Não existe um funcionário com este ID!')
        else:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario):
                raise IdError('Não existe um funcionário com este ID!')
        
        if kwargs.get('senha') != None:
            valida_senha = senha_valida(kwargs.get('senha'))
            if valida_senha != True:
                raise ValueError(valida_senha)
            
            kwargs['senha'] = hash_senha(kwargs.get('senha'), decode=True)
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError(False, 'Nome inválido!')

        if kwargs.get('telefone') != None:
            telefone = formatar_telefone(kwargs.get('telefone'))
            if not telefone:
                raise ValueError(False, 'Telefone inválido!')

        if kwargs.get('email') != None:
            if not email_valido(kwargs.get('email')):
                raise ValueError(False, 'Email inválido!')

        if kwargs.get('cpf') != None:
            if not cpf_valido(kwargs.get('cpf')):
                raise ValueError(False, 'CPF inválido!')
        
        if admin:
            return FuncionarioDal.alterar_funcionario(id_funcionario, codigo, admin=True, posicao=posicao, **kwargs)
        else:
            return FuncionarioDal.alterar_funcionario(id_funcionario, codigo, **kwargs)

    
    @staticmethod
    def remover_funcionario(id_funcionario: int, admin=False, login: LoginFuncionario=None) -> bool:
        codigo = FuncionarioDal.ler_arquivo()
        
        if admin:
            adm = FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=True)
            if not adm:
                raise IdError('Não existe um ADM com este ID')
            
            if adm[1]['posicao'] > login.posicao:
                raise ValueError('Não é possível remover um ADM com a posição maior que a sua!')
        else:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario):
                raise IdError('Não existe um funcionário com este ID')
        
        if admin:
            return FuncionarioDal.remover_funcionario(id_funcionario, codigo, admin=True)
        else:
            return FuncionarioDal.remover_funcionario(id_funcionario, codigo)


# --------------------------------------------------
# --------------------------------------------------


class ClienteController:
    @staticmethod
    def cadastrar_cliente(nome: str, cpf: str, senha: str, telefone: str=None, email: str=None) -> bool:
        codigo = ClienteDal.ler_arquivo()
        
        valida_senha = senha_valida(senha)
        if valida_senha != True:
            raise ValueError(valida_senha)
        
        if (not nome) or 5 > len(nome) > 50:
            raise ValueError('Nome inválido!')
        if nome.isnumeric():
            raise TypeError('O nome não pode ser um número!')

        if telefone != None:
            telefone = formatar_telefone(telefone)
            if not telefone:
                raise ValueError('Telefone inválido!')

        if email != None:
            if not email_valido(email):
                raise ValueError('Email inválido!')

        # !!! no caso de CPF duplicado enviar um alerta para o chefe
        for c in codigo:
            if c['cpf'] == cpf:
                raise ValueError('Já existe um cliente cadastrado com este CPF!')

        if not cpf_valido(cpf):
            raise ValueError('CPF inválido!')
        
        senha = hash_senha(senha, decode=True)
        
        id = IdDal.gerar_id('id_cliente')
        cliente = Cliente(nome, cpf, id, senha, telefone, email)
        return ClienteDal.cadastrar_cliente(cliente, codigo)


    @staticmethod
    def alterar_cliente(id_cliente: int, **kwargs) -> bool:
        codigo = ClienteDal.ler_arquivo()
        
        if not ClienteDal.ler_cliente(codigo, id_cliente):
            raise IdError('Não existe uma cliente com esse ID!')
        
        if kwargs.get('senha') != None:
            valida_senha = senha_valida(kwargs.get('senha'))
            if valida_senha != True:
                raise ValueError(valida_senha)
            
            kwargs['senha'] = hash_senha(kwargs.get('senha'), decode=True)
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError(False, 'Nome inválido!')

        if kwargs.get('telefone') != None:
            telefone = formatar_telefone(kwargs.get('telefone'))
            if not telefone:
                raise ValueError(False, 'Telefone inválido!')

        if kwargs.get('email') != None:
            if not email_valido(kwargs.get('email')):
                raise ValueError(False, 'Email inválido!')

        if kwargs.get('cpf') != None:
            if not cpf_valido(kwargs.get('cpf')):
                raise ValueError(False, 'CPF inválido!')
        
        return ClienteDal.alterar_cliente(id_cliente, codigo, **kwargs)
    

    @staticmethod
    def remover_cliente(id_cliente: int) -> bool:
        codigo = ClienteDal.ler_arquivo()
        
        if not ClienteDal.ler_cliente(codigo, id_cliente):
            raise IdError('Não existe um cliente com este ID')
        
        return ClienteDal.remover_cliente(id_cliente, codigo)


# --------------------------------------------------
# --------------------------------------------------


class Login:
    @staticmethod
    def logar_funcionario(nome: str, senha: str, admin=False) -> LoginFuncionario:
        codigo = FuncionarioDal.ler_arquivo()

        if admin:
            for i, f in enumerate(codigo['admins']):
                if f['nome'] == nome:
                    senha_2 = f['senha'].encode('utf-8')
                    break
            else:
                raise ValueError('Nao existe um ADM com este nome!')
        else:
            for i, f in enumerate(codigo['funcionarios']):
                if f['nome'] == nome:
                    senha_2 = f['senha'].encode('utf-8')
                    break
            else:
                raise ValueError('Nao existe um funcionário com este nome!')
        
        senha = senha.encode('utf-8')
        if not comparar_senha(senha, senha_2):
            raise ValueError('Senha incorreta!')
        
        return LoginFuncionario(f['id'], f['cpf'], f['nome'])
    

    @staticmethod
    def logar_cliente(nome: str, senha: str) -> LoginCliente:
        codigo = ClienteDal.ler_arquivo()

        for i, c in enumerate(codigo):
            if c['nome'] == nome:
                senha_2 = c['senha'].encode('utf-8')
                break
        else:
            raise ValueError('Não existe um usuário com este nome!')
        
        senha = senha.encode('utf-8')
        if not comparar_senha(senha, senha_2):
            raise ValueError('Senha incorreta!')
        
        return LoginCliente(c['id'], c['cpf'], c['nome'], c['telefone'], c['email'])


# --------------------------------------------------
# --------------------------------------------------


class CaixaController:
    @staticmethod
    def cadastrar_caixa(numero_caixa: int, valor_no_caixa: float) -> bool:
        codigo = CaixaDal.ler_arquivo()

        if CaixaDal.ler_caixa(numero_caixa, codigo):
            raise ValueError('Já existe um caixa com este número!')
        
        if not valor_no_caixa.isnumeric():
            raise TypeError('O valor no caixa deve ser um número!')
        if valor_no_caixa < 0:
            raise ValueError('O valor no caixa não pode ser negativo!')
        
        return CaixaDal.cadastrar_caixa(numero_caixa, valor_no_caixa)
    

    @staticmethod
    def alterar_caixa(numero_caixa: int, **kwargs) -> bool:
        codigo = CaixaDal.ler_arquivo()
        
        if not CaixaDal.ler_caixa(numero_caixa, codigo):
            raise ValueError('Não existe um caixa com esse número!')
        
        if kwargs.get('numero_caixa') != None:
            if CaixaDal.ler_caixa(numero_caixa, codigo):
                raise ValueError('Já existe um caixa com este número!')
        
        if kwargs.get('valor_no_caixa') != None:
            if kwargs.get('valor_no_caixa') < 0:
                raise ValueError('O valor no caixa não pode ser negativo!')
        
        return CaixaDal.alterar_caixa(numero_caixa, codigo, **kwargs)


    @staticmethod
    def remover_caixa(numero_caixa: int) -> bool:
        codigo = CaixaDal.ler_arquivo()
        
        caixa = CaixaDal.ler_caixa(numero_caixa, codigo)
        if not caixa:
            raise IdError('Não existe uma caixa com esse número!')
        if caixa[1]['valor_no_caixa'] > 0:
            raise Exception('Você não pode remover um caixa com dinheiro dentro!')
        
        return CaixaDal.remover_caixa(numero_caixa, codigo)
    

    @staticmethod
    def definir_caixa(numero_caixa: int, login: LoginFuncionario, admin: False) -> Caixa:
        codigo_caixa = CaixaDal.ler_arquivo()
        codigo_funcionario = FuncionarioDal.ler_arquivo()
        
        if not CaixaDal.ler_caixa(numero_caixa, codigo_caixa):
            raise ValueError('Não existe um caixa com esse número!')

        if admin:
            for i, f in enumerate(codigo_funcionario['admins']):
                if f['id'] == login.id_funcionario:
                    break
            else:
                raise ValueError('Não existe um funcionário com este ID')
        else:
            for i, f in enumerate(codigo_funcionario['funcionarios']):
                if f['id'] == login.id_funcionario:
                    break
            else:
                raise ValueError('Não existe um funcionário com este ID')
        
        index, caixa = CaixaDal.ler_caixa(numero_caixa, codigo_caixa)
        return Caixa(caixa['numero_caixa'], caixa['valor_no_caixa'], f['id'], f['nome'])


    @staticmethod
    def passar_produto(id_produto: int, quantidade: int) -> ProdutoNoCarrinho:
        codigo_caixa = CaixaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        produto = EstoqueDal.ler_produto_por_id(id_produto, codigo_estoque, retorna_obj=False)
        if not produto:
            raise IdError('Não existe um produto com este ID!')
        index_categoria, index_produto, produto = produto
        
        qnt = contar_quantidade(produto)
        if qnt < quantidade:
            raise ValueError('Não temos está quantidade de produtos!')
        
        preco_total = qnt * produto['preco']        
        return ProdutoNoCarrinho(codigo_estoque[index_categoria]['id'],
                                 codigo_estoque[index_categoria]['categoria'],
                                 produto['id'], produto['nome'], quantidade, produto['preco'], preco_total)


# --------------------------------------------------
# --------------------------------------------------


class VendaController:
    @staticmethod
    def retirar_do_estoque(carrinho: Carrinho):
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        for i, p in enumerate(carrinho.produtos):
            codigo_estoque = EstoqueController.remover_quantidade(p.id_categoria, p.id_produto, 
                                                                  p.quantidade, codigo_estoque)
        
        EstoqueDal.salvar_arquivo(codigo_estoque)


    @staticmethod
    def venda(login: LoginFuncionario, numero_caixa: int, carrinho: Carrinho,
              valor_recebido: float, cpf_cliente=None) -> tuple:
        codigo_caixa = CaixaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_venda = VendaDal.ler_arquivo()
        
        caixa = CaixaDal.ler_caixa(numero_caixa, codigo_caixa)
        if not caixa:
            raise ValueError('Não existe um caixa com esse número!')
        index, caixa = caixa

        if cpf_cliente != None:
            if not cpf_valido(cpf_cliente):
                raise ValueError('CPF inválido!')
        
        if valor_recebido < carrinho.preco_total:
            raise ValueError('Dinheiro insuficiente!')
        
        troco = valor_recebido - carrinho.preco_total
        if troco > caixa['valor_no_caixa']:
            raise ValueError('Caixa sem troco!')
        
        valor_no_caixa = caixa['valor_no_caixa'] + carrinho.preco_total
        CaixaDal.alterar_caixa(numero_caixa, codigo_caixa, valor_no_caixa=valor_no_caixa)

        produtos = []
        for i, p in enumerate(carrinho.produtos):
            produtos.append({
                'id_categoria':   p.id_categoria,
                'nome_categoria': p.nome_categoria,
                'id_produto':     p.id_produto,
                'nome_produto':   p.nome_produto,
                'quantidade':     p.quantidade,
                'preco_unidade':  p.preco_unidade,
                'preco_total':    p.preco_total
            })
        
        VendaController.retirar_do_estoque(carrinho)

        tipo_func = 'admins' if login.admin else 'funcionarios'

        id = IdDal.gerar_id('id_venda')
        data = datetime.date.today().strftime('%d/%m/%Y')
        venda = Venda(id, data, login.id_funcionario, tipo_func, carrinho,
                      cpf_cliente=cpf_cliente, lista_produtos=produtos)
        return (VendaDal.cadastrar_venda(venda, codigo_venda), troco)
    

    @staticmethod
    def venda_online(login: LoginCliente, carrinho: Carrinho, valor_recebido: float) -> tuple:
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_venda = VendaDal.ler_arquivo()

        if valor_recebido < carrinho.preco_total:
            raise ValueError('Dinheiro insuficiente!')
        
        troco = valor_recebido - carrinho.preco_total
        
        produtos = []
        for i, p in enumerate(carrinho.produtos):
            produtos.append({
                'id_categoria':   p.id_categoria,
                'nome_categoria': p.nome_categoria,
                'id_produto':     p.id_produto,
                'nome_produto':   p.nome_produto,
                'quantidade':     p.quantidade,
                'preco_unidade':  p.preco_unidade,
                'preco_total':    p.preco_total
            })
        
        VendaController.retirar_do_estoque(carrinho)
        
        id = IdDal.gerar_id('id_venda')
        data = datetime.date.today().strftime('%d/%m/%Y')
        venda = VendaOnline(id, data, carrinho, login.id_cliente, login.cpf, lista_produtos=produtos)
        return (VendaDal.cadastrar_venda_online(venda, codigo_venda), troco)
    

    @staticmethod
    def gerar_relatorio(chave=None, datas: tuple=None, gerar_txt=False):
        """
        Gera um relatório das vendas, use o parâmetro `chave` para especificar o tipo de venda:
            * chave=None: relatório de todas as vendas
            * chave='fisica': relatório das vendas fisicas
            * chave='online': relatório das vendas online
        
        O parâmetro `datas` é opcional, caso passado ele deverá conter duas instâncias de
        `datetime.datetime`, que serão o intervalo das datas na qual será procurada a venda.
        Se nada for passado, ele irá pegar as vendas de todas as datas.
        
        ---

        Args:
            chave (str): pedir as vendas fisicas/online somente. default=None
            datas (tuple): 2 instâncias de datetime.datetime . default=None
            gerar_txt (bool): default=False
        Returns:
            gerar_txt=False: retorna o relatório em formato de str
            gerar_txt=True: None
        """
        codigo_venda = VendaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_funcionario = FuncionarioDal.ler_arquivo()

        pdt, func, lucros = VendaDal.coletar_dados(codigo_venda, codigo_estoque.copy(),
                                                   codigo_funcionario, chave, datas)

        if datas:
            d1 = datetime.datetime.strftime(datas[0], '%d/%m/%Y')
            d2 = datetime.datetime.strftime(datas[1], '%d/%m/%Y') 
            titulo = f'Relatório das Vendas entre {d1} e {d2}:\n\n{"="*100}\n\n'
        else:
            titulo = f'Relatório das Vendas:\n\n{"="*100}\n\n'

        relatorio = ''
        relatorio += titulo
        relatorio += 'Vendas dos produtos:\n'

        for k, v in pdt.items():
            relatorio += f'\n{"-"*50}\n'
            relatorio += f'\n    Categoria: {k.capitalize()}\n\n'
            for key, value in v.items():
                index_categoria, index_produto, p = EstoqueDal.ler_produto_por_id(
                    int(key), codigo_estoque
                    )
                
                relatorio += f'{"ID":4} | {"Nome":40} | {"Marca":20} | {"Quantidade Vendida"}\n\n'
                relatorio += f'{str(p.id).zfill(4)} | {p.nome:40} | {p.marca:20} | {value:4}\n'
            
        relatorio += f'\n\n{"="*100}\n\n'
        relatorio += 'Funcionários que Mais Venderam:\n'

        for k, v in func.items():
            relatorio += f'\n{"-"*50}\n'
            relatorio += f'\n    {k.capitalize()}:\n\n'
            for key, value in v.items():
                index, f = FuncionarioDal.ler_funcionario(
                    codigo_funcionario, int(key),
                    admin=True if k == 'admins' else False, retorna_obj=True
                    )
                
                relatorio += f'{"ID":4} | {"Nome":50} | {"Vendas":6}\n\n'
                relatorio += f'{str(f.id).zfill(4)} | {f.nome:50} | {str(value).zfill(6):6}\n'
        
        relatorio += f'\n\n{"="*100}\n\n'
        relatorio += 'Lucros:\n'

        for k, v in lucros.items():
            relatorio += f'\n{"-"*50}\n'
            relatorio += f'\n    Lucro da Loja {k.split("_")[2].capitalize()}:\n\n'
            relatorio += f'    R${v:.2f}\n'

        return VendaDal.gerar_txt(relatorio) if gerar_txt else relatorio


# --------------------------------------------------
# --------------------------------------------------
