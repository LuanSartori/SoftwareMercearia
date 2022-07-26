# recebe dados, os valida e passa para o dal.py

from model import Categoria, Produto
from dal import CategoriaDal, EstoqueDal


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
            
        i = CategoriaDal.pesquisar_arquivo(codigo, 'id', str(id_categoria) )
        if not i:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        

        return CategoriaDal.remover(id_categoria, i, codigo, codigo_estoque)


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
        
        id = EstoqueDal.gerar_id()
        
        produto = Produto(id, id_categoria, nome, marca, preco, quantidade, id_fornecedor)
        return EstoqueDal.cadastrar_produto(produto, codigo_estoque)


    @staticmethod
    def alterar_produto(id_produto:int, id_categoria_atual: int, id_categoria=None, nome=None, marca=None, preco=None, quantidade=None, id_fornecedor=None):
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')

        if not EstoqueDal.ler_produto(id_categoria_atual, id_produto, codigo_estoque, True):
            raise IdError('Não existe uma produto com esse ID', id_produto)
        if not CategoriaDal.pesquisar_arquivo('id', str(id_categoria_atual), codigo):
            raise IdError('Não existe uma categoria com esse ID', id_categoria_atual)
        
        if nome != None and len(nome) > 40 or marca != None and len(marca) > 30:
            raise ValueError('Este nome é grande demais')
        
        
        return EstoqueDal.alterar_produto(id_produto, id_categoria_atual, codigo_estoque, id_categoria=id_categoria, nome=nome, marca=marca, preco=preco, quantidade=quantidade, id_fornecedor=id_fornecedor)