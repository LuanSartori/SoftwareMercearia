from model import Categoria, Produto, Fornecedor
from dal import CategoriaDal, EstoqueDal, FornecedorDal

from utils import cnpj_valido, email_valido, telefone_valido


class IdError(Exception):
    def __init__(self, msg: str, valor: int):
        pass


class ServerError(Exception):
    def __init__(self, msg: str):
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


class FornecedorController:
    @staticmethod
    def cadastrar(nome: str, telefone: str, email: str, cnpj: str):
        codigo = FornecedorDal.ler_arquivo()
        if not codigo:
            raise ServerError('Não foi possível acessar o banco de dados!')

        if (not nome) or 5 > len(nome) > 50:
            raise ValueError('Nome inválido!')

        telefone = telefone_valido(telefone)
        if not telefone:
            raise ValueError('Telefone inválido!')

        if not email_valido(email):
            raise ValueError('Email inválido!')

        if not cnpj_valido(cnpj):
            raise ValueError('CNPJ inválido!')
        
        id = FornecedorDal.gerar_id()
        fornecedor = Fornecedor(id, nome, telefone, email, cnpj)
        return FornecedorDal.cadastrar(fornecedor, codigo)