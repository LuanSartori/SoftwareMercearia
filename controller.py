import re
from model import Categoria, Funcionario, Produto, Fornecedor, Lote
from dal import CategoriaDal, EstoqueDal, FornecedorDal, FuncionarioDal

from utils import cnpj_valido, cpf_valido, email_valido, telefone_valido


class IdError(Exception):
    def __init__(self, *objects):
        pass


class ServerError(Exception):
    def __init__(self, *objects):
        pass


class CategoriaController():
    @staticmethod
    def cadastrar(categoria: str):
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')

        if CategoriaDal.pesquisar_arquivo(codigo, 'categoria', categoria):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')
        
        
        id = CategoriaDal.gerar_id()
        categoria = Categoria(categoria, id)
        return CategoriaDal.salvar(categoria, codigo, codigo_estoque)


    @staticmethod
    def alterar(id_categoria: int, categoria: str):
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')

        i = CategoriaDal.pesquisar_arquivo(codigo, 'id', str(id_categoria) )
        if not i:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)

        if CategoriaDal.pesquisar_arquivo(codigo, 'categoria', categoria):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')


        categoria = Categoria(categoria, id_categoria)
        return CategoriaDal.alterar(id_categoria, categoria, i, codigo, codigo_estoque)


    @staticmethod
    def remover(id_categoria: int):
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')
            
        index = CategoriaDal.pesquisar_arquivo(codigo, 'id', str(id_categoria) )
        if not index:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        
        if id_categoria == 0:
            raise ValueError(f'Não é possível remover a categoria "Nenhuma"')

        return CategoriaDal.remover(id_categoria, index, codigo, codigo_estoque)


# --------------------------------------------------
# --------------------------------------------------


class EstoqueController:
    @staticmethod
    def cadastrar_produto(id_categoria: int, nome: str, marca: str, preco: float, quantidade: int=None, id_fornecedor: int=None):
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if len(nome) > 40 or len(marca) > 30:
            raise ValueError('Este nome é grande demais')
        elif not CategoriaDal.pesquisar_arquivo('id', id_categoria, codigo):
            raise IdError('Está categoria não existe!')
        
        index = EstoqueDal.pesquisar_arquivo(codigo, produto.id_categoria)
        for p in codigo[index]['produtos']:
            if p['nome'] == nome:
                raise ValueError('Já existe um produto com esse nome')

        id = EstoqueDal.gerar_id()
        
        produto = Produto(id, id_categoria, nome, marca, preco, quantidade, id_fornecedor)
        return EstoqueDal.cadastrar_produto(produto, codigo_estoque)


    @staticmethod
    def alterar_produto(id_produto:int, id_categoria_atual: int, **kwargs):
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')

        if not EstoqueDal.ler_produto(id_categoria_atual, id_produto, codigo_estoque, True):
            raise IdError('Não existe uma produto com esse ID', id_produto)
        if not CategoriaDal.pesquisar_arquivo('id', str(id_categoria_atual), codigo):
            raise IdError('Não existe uma categoria com esse ID', id_categoria_atual)
        
        if kwargs.get('nome') != None and len(kwargs.get('nome')) > 40 or kwargs.get('marca') != None and len(kwargs.get('marca')) > 30:
            raise ValueError('Este nome é grande demais')
        
        
        return EstoqueDal.alterar_produto(id_produto, id_categoria_atual, codigo_estoque, **kwargs)


    @staticmethod
    def remover_produto(id_produto: int, id_categoria: int):
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if not EstoqueDal.ler_produto(id_categoria, id_produto, codigo_estoque, True):
            raise IdError('Não existe uma produto com esse ID', id_produto)
        if not CategoriaDal.pesquisar_arquivo('id', str(id_categoria), codigo):
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        
        return EstoqueDal.remover_produto(id_produto, id_categoria, codigo_estoque)


# --------------------------------------------------
# --------------------------------------------------


class FornecedorController:
    @staticmethod
    def cadastrar_fornecedor(nome: str, telefone: str, email: str, cnpj: str=None):
        codigo = FornecedorDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if cnpj != None:
            for f in codigo:
                if f['cnpj'] == cnpj:
                    raise ValueError('Já existe um fornecedor cadastrado com este CNPJ!')

        if (not nome) or 5 > len(nome) > 50 or not nome.isnumeric():
            raise ValueError('Nome inválido!')

        telefone = telefone_valido(telefone)
        if not telefone:
            raise ValueError('Telefone inválido!')

        if not email_valido(email):
            raise ValueError('Email inválido!')

        if not cnpj_valido(cnpj):
            raise ValueError('CNPJ inválido!')
        
        id = FornecedorDal.gerar_id_fornecedor()
        fornecedor = Fornecedor(id, nome, telefone, email, cnpj)
        return FornecedorDal.cadastrar_fornecedor(fornecedor, codigo)
    

    @staticmethod
    def alterar_fornecedor(id_fornecedor, **kwargs):
        codigo = FornecedorDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID')
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError('Nome inválido!')

        if kwargs.get('telefone') != None:
            telefone = telefone_valido(kwargs.get('telefone'))
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
    def remover_fornecedor(id_fornecedor: int):
        codigo = FornecedorDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)

        return FornecedorDal.remover_fornecedor(id_fornecedor, codigo)
    

    @staticmethod
    def cadastrar_lote(id_fornecedor: int, preco_lote: float, id_categoria: int, id_produto: id, quantidade: int, tempo: list=None):
        # Na view vai perguntar se o produto do lote já existe no sistema ou se ele quer criar um !!!

        codigo = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        
        if not EstoqueDal.ler_produto(id_categoria, id_produto, codigo_estoque):
            raise IdError('Não existe um produto com este ID', id_produto)

        if tempo != None:
            valida = ['dia', 'semana', 'mês']
            if not tempo[1] in valida:
                raise ValueError('Tempo inválido!', tempo[1])
        
        
        id = FornecedorDal.gerar_id_lote()
        lote = Lote(id, preco_lote, id_produto, quantidade, tempo)
        return FornecedorDal.cadastrar_lote(id_fornecedor, lote, codigo)
    
    
    @staticmethod
    def alterar_lote(id_fornecedor: int, id_lote: int, **kwargs):
        codigo = FornecedorDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        if not FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False):
            raise IdError('Não existe um lote com esse ID neste fornecedor!')
        
        if kwargs.get('id_categoria') != None:
            codigo_estoque = EstoqueDal.ler_arquivo()
            if not codigo_estoque:
                raise ServerError('Não foi possível acessar o banco de dados!')
            
            if not EstoqueDal.ler_produto(kwargs.get('id_categoria'), kwargs.get('id_produto'), codigo_estoque):
                raise IdError('Não existe um produto com este ID', kwargs.get('id_produto'))
        
        return FornecedorDal.alterar_lote(id_fornecedor, id_lote, codigo, **kwargs)


    @staticmethod
    def remover_lote(id_fornecedor: int, id_lote: int):
        codigo = FornecedorDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        if not FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False):
            raise IdError('Não existe um lote com esse ID neste fornecedor!')
        
        return FornecedorDal.remover_lote(id_fornecedor, id_lote, codigo)


# --------------------------------------------------
# --------------------------------------------------


class FuncionarioController:
    @staticmethod
    def cadastrar_funcionario(nome: str, telefone: str, email: str, cpf: str, cargo: str, senha: str, admin=False, posicao=None):
        codigo = FuncionarioDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        # aqui vamos verificar se a posicao do ADM que está logado não é menor do que a do ADM que ele quer cadastrar, para isso vamos receber um parâmetro a mais !!!

        for f in codigo['funcionarios']:
            if f['cpf'] == cpf:
                raise ValueError('Já existe um funcionário cadastrado com este CPF!')
        for f in codigo['admins']:
            if f['cpf'] == cpf:
                raise ValueError('Já existe um ADM cadastrado com este CPF!')
        
        if (not nome) or 5 > len(nome) > 50 or nome.isnumeric():
            raise ValueError('Nome inválido!')

        telefone = telefone_valido(telefone)
        print(telefone)
        if not telefone:
            raise ValueError('Telefone inválido!')

        if not email_valido(email):
            raise ValueError('Email inválido!')

        if not cpf_valido:
            raise ValueError('CPF inválido!')
        
        if admin:
            id = FuncionarioDal.gerar_id_admin()
        else:
            id = FuncionarioDal.gerar_id_funcionario()

        funcionario = Funcionario(id, nome, cpf, cargo, senha, telefone, email)
        if admin:
            return FuncionarioDal.cadastrar_funcionario(funcionario, codigo, admin=True, posicao=posicao)
        else:
            return FuncionarioDal.cadastrar_funcionario(funcionario, codigo)


    @staticmethod
    def alterar_funcionario(id_funcionario, admin=False, posicao=None, **kwargs):
        codigo = FuncionarioDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')

        # aqui vamos verificar se a posicao do ADM que está logado não é menor do que a do ADM que ele quer alteracao, para isso vamos receber um parâmetro a mais !!!
        
        if admin:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=True):
                raise IdError('Não existe um funcionário com este ID!')
        else:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario):
                raise IdError('Não existe um funcionário com este ID!')
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError('Nome inválido!')

        if kwargs.get('telefone') != None:
            telefone = telefone_valido(kwargs.get('telefone'))
            if not telefone:
                raise ValueError('Telefone inválido!')

        if kwargs.get('email') != None:
            if not email_valido(kwargs.get('email')):
                raise ValueError('Email inválido!')

        if kwargs.get('cpf') != None:
            if not cpf_valido(kwargs.get('cpf')):
                raise ValueError('CPF inválido!')
        
        if admin:
            return FuncionarioDal.alterar_funcionario(id_funcionario, codigo, admin=True, posicao=posicao, **kwargs)
        else:
            return FuncionarioDal.alterar_funcionario(id_funcionario, codigo, **kwargs)

    
    @staticmethod
    def remover_funcionario(id_funcionario: int, admin=False):
        codigo = FuncionarioDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        if admin:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=True):
                raise IdError('Não existe um ADM com este ID')
        else:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario):
                raise IdError('Não existe um funcionário com este ID')
        
        if admin:
            return FuncionarioDal.remover_funcionario(id_funcionario, codigo, admin=True)
        else:
            return FuncionarioDal.remover_funcionario(id_funcionario, codigo)
