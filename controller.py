# recebe dados, os valida e passa para o dal.py

from model import Categoria, Estoque
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
        if CategoriaDal.ler_arquivo('categoria', categoria):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 20:
            raise IdError(False, 'Esse nome é muito grande!')
        
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')
        
        id = CategoriaDal.gerar_id()
        categoria = Categoria(categoria, id)
        return CategoriaDal.salvar(categoria, codigo_estoque)


    @staticmethod
    def alterar(id_categoria: int, categoria: str):
        validacao = CategoriaDal.ler_arquivo('id', str(id_categoria) )
        if not validacao:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        i, codigo = validacao

        if CategoriaDal.ler_arquivo('categoria', categoria):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')

        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')

        categoria = Categoria(categoria, id_categoria)
        return CategoriaDal.alterar(int(id_categoria), categoria, i, codigo, codigo_estoque)


    @staticmethod
    def remover(id_categoria: int):
        validacao = CategoriaDal.ler_arquivo('id', str(id_categoria) )
        if not validacao:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        i, codigo = validacao
        
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')

        return CategoriaDal.remover(id_categoria, i, codigo, codigo_estoque)