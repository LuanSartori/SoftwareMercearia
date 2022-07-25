# lê e armazena dados no banco de dados

import json
from model import Categoria, Estoque, Produto


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
    def ler_arquivo():
        try:
            with open('banco_dados/categorias.json', 'r') as arq:
                return json.load(arq)
        except:
            return False


    @staticmethod
    def pesquisar_arquivo(codigo, chave: str, valor: str):
        for i, c in enumerate(codigo):
            if str( c[chave] ) == str(valor):
                return i
        return False


    @staticmethod
    def salvar(categoria: Categoria, codigo, codigo_estoque) -> tuple:
        try:
            nova_categoria = {'id': categoria.id, 'categoria': categoria.categoria}
            codigo.insert(categoria.id, nova_categoria)

            with open('banco_dados/categorias.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                EstoqueDal.salvar_categoria(categoria, codigo_estoque)

                return (True, 'Categoria cadastrada com sucesso!')
        except:
            return (False, 'Erro interno do sistema')


    @staticmethod
    def alterar(id_categoria: int, alteracao: Categoria, i, codigo, codigo_estoque):
        try:
            with open('banco_dados/categorias.json', 'w') as arq:
                codigo[i] = {'id': alteracao.id, 'categoria': alteracao.categoria}
                json.dump(codigo, arq, indent=4)
                EstoqueDal.alterar_categoria(alteracao, codigo_estoque)

                return (True, 'Categoria alterada com sucesso!')
        except:
            return (False, 'Erro interno do sistema')
    

    @staticmethod
    def remover(id_categoria: int, i, codigo, codigo_estoque):
        try:
            with open('banco_dados/categorias.json', 'w') as arq:
                codigo.pop(i)
                json.dump(codigo, arq, indent=4)

            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                codigo['id_categoria']['ids_vazios'].insert(0, id_categoria)
                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    EstoqueDal.remover_categoria(id_categoria, codigo_estoque)

                    return (True, 'Categoria removida com sucesso!')
        except:
            return (False, 'Erro interno do sistema')

# --------------------------------------------------
# --------------------------------------------------

class EstoqueDal:
    @staticmethod
    def ler_arquivo():
        try:
            with open('banco_dados/estoque.json', 'r') as arq:
                return json.load(arq)
        except:
            return False
    

    @staticmethod
    def pesquisar_arquivo(codigo, id_categoria):
        for i, c in enumerate(codigo):
            if c['id'] == id_categoria:
                return i
    

    @staticmethod
    def salvar_categoria(categoria: Categoria, codigo: list):
        dado = {"id": categoria.id, "categoria": categoria.categoria, "produtos": []}
        codigo.insert(categoria.id, dado)

        with open('banco_dados/estoque.json', 'w') as arq:
            json.dump(codigo, arq, indent=4)


    @staticmethod
    def alterar_categoria(alteracao: Categoria, codigo: list):
        index = EstoqueDal.pesquisar_arquivo(codigo, alteracao.id)

        codigo[index]['categoria'] = alteracao.categoria
        with open('banco_dados/estoque.json', 'w') as arq:
            json.dump(codigo, arq, indent=4)
    

    @staticmethod
    def remover_categoria(id_categoria: int, codigo: list):
        index = EstoqueDal.pesquisar_arquivo(codigo, id_categoria)
        
        for p in codigo[index]['produtos']:
            p['id_categoria'] = 0
            codigo[0]['produtos'].append(p)
        codigo.pop(index)

        with open('banco_dados/estoque.json', 'w') as arq:
            json.dump(codigo, arq, indent=4)
     

    @staticmethod
    def ler_produto(id_categoria: int, id_produto: int, codigo: list) -> Produto:
        index = EstoqueDal.pesquisar_arquivo(codigo, id_categoria)
        produtos = codigo[index]['produtos']
        
        for p in produtos:
            if p['id'] == id_produto:
                return Produto(p['id'],
                                p['id_categoria'],
                                p['nome'],
                                p['marca'],
                                p['preco'],
                                p['id_fornecedor'])
        return False
