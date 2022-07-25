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
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        if not codigo or not codigo_estoque:
            raise ServerError('Não foi possível acessar o banco de dados!')

        if CategoriaDal.pesquisar_arquivo(codigo, 'categoria', categoria):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 20:
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


categoria = str(input('Nome da categoria: ')).lower()
id = int(input('ID da categoria: '))
CategoriaController.alterar(id, categoria)