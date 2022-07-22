# lê e armazena dados no banco de dados

import json
from model import Categoria


class CategoriaDal:
    @staticmethod
    def gerar_id() -> int:
        try:
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                if len( codigo['id_categoria']['ids_vazios'] ) == 0:
                    id = codigo['id_categoria']['novo_id']
                    codigo['id_categoria']['novo_id'] += 1
                else:
                    id = codigo['id_categoria']['ids_vazios'][0]
                    codigo['id_categoria']['ids_vazios'].pop(0)

                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return id
        except:
            return (False, 'Erro interno do sistema')


    @staticmethod
    def ler(chave: str, valor: str) -> tuple:
        try:
            with open('banco_dados/categorias.json', 'r') as arq:
                codigo = json.load(arq)
                for i, c in enumerate(codigo):
                    if str( c[chave] ) == str(valor):
                        return (i, c, codigo)
                return False
        except:
            return False


    @staticmethod
    def salvar(categoria: Categoria):
        try:
            with open('banco_dados/categorias.json', 'r') as arq:
                codigo = json.load(arq)
                with open('banco_dados/categorias.json', 'w') as arq:
                    nova_categoria = {'id': categoria.id, 'categoria': categoria.categoria}
                    codigo.insert(categoria.id, nova_categoria)
                    json.dump(codigo, arq, indent=4)
                    return (True, 'Categoria cadastrada com sucesso!')
        except:
            return (False, 'Erro interno do sistema')


    @staticmethod
    def alterar(id_categoria: int, alteracao: Categoria, i, codigo):
        try:
            with open('banco_dados/categorias.json', 'w') as arq:
                codigo[i] = {'id': alteracao.id, 'categoria': alteracao.categoria}
                json.dump(codigo, arq, indent=4)
                return (True, 'Categoria alterada com sucesso!')
        except:
            return (False, 'Erro interno do sistema')
    

    @staticmethod
    def remover(id_categoria: int, i, codigo):
        try:
            with open('banco_dados/categorias.json', 'w') as arq:
                codigo.pop(i)
                json.dump(codigo, arq, indent=4)

            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                codigo['id_categoria']['ids_vazios'].append(id_categoria)
                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return (True, 'Categoria removida com sucesso!')
        except:
            return (False, 'Erro interno do sistema')