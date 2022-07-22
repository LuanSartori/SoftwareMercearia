# recebe dados, os valida e passa para o dal.py

from model import Categoria
from dal import CategoriaDal


class IdError(Exception):
    def __init__(self, msg: str, valor: int):
        pass


class CategoriaController():
    @staticmethod
    def cadastrar(categoria: str):
        if CategoriaDal.ler('categoria', categoria):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 20:
            raise IdError(False, 'Esse nome é muito grande!')
        
        id = CategoriaDal.gerar_id()
        categoria = Categoria(categoria, id)

        return CategoriaDal.salvar(categoria)


    @staticmethod
    def alterar(id_categoria: int, categoria: str):
        validacao = CategoriaDal.ler('id', str(id_categoria) )
        if not validacao:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        i, c, codigo = validacao

        if CategoriaDal.ler('categoria', categoria):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')

        categoria = Categoria(categoria, id_categoria)
        return CategoriaDal.alterar(int(id_categoria), categoria, i, codigo)


    @staticmethod
    def remover(id_categoria: int):
        validacao = CategoriaDal.ler('id', str(id_categoria) )
        if not validacao:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        i, c, codigo = validacao
        
        return CategoriaDal.remover(id_categoria, i, codigo)
