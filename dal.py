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
    def ler_arquivo(chave: str, valor: str):
        try:
            with open('banco_dados/categorias.json', 'r') as arq:
                codigo = json.load(arq)
                for i, c in enumerate(codigo):
                    if str( c[chave] ) == str(valor):
                        return (i, codigo)
                return False
        except:
            return False


    @staticmethod
    def ler_categoria(id: int) -> Categoria:
        c = CategoriaDal.ler_arquivo('id', id)
        
        return Categoria(c['categoria'], c['id'])


    @staticmethod
    def salvar(categoria: Categoria, codigo_estoque) -> tuple:
        try:
            with open('banco_dados/categorias.json', 'r') as arq:
                codigo = json.load(arq)
                with open('banco_dados/categorias.json', 'w') as arq:
                    nova_categoria = {'id': categoria.id, 'categoria': categoria.categoria}
                    codigo.insert(categoria.id, nova_categoria)
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
                codigo['index_categoria']['index_vazios'].insert(0, id_categoria+1)
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
                codigo = json.load(arq)
                return codigo
        except:
            return False


    @staticmethod
    def gerar_index():
        with open('banco_dados/ids.json', 'r') as arq:
            codigo = json.load(arq)
            if len( codigo['index_categoria']['index_vazios'] ) == 0:
                index = codigo['index_categoria']['novo_index']
                codigo['index_categoria']['novo_index'] += 1
            else:
                index = codigo['index_categoria']['index_vazios'][0]
                codigo['index_categoria']['index_vazios'].pop(0)

            with open('banco_dados/ids.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return index


    @staticmethod
    def ler_index(id_categoria: int) -> int:
        """
        Retorna um index da lista a partir do id de uma categoria
        """

        with open('banco_dados/estoque.json', 'r') as arq:
            codigo = json.load(arq)

            for c in codigo[0]:
                if c['id_categoria'] == id_categoria:
                    index = c['index']
                    return index
            return False
    

    @staticmethod
    def salvar_categoria(categoria: Categoria, codigo: list):
        index = EstoqueDal.gerar_index()
        dado_1 = {"index": index, "id_categoria": categoria.id, "categoria": categoria.categoria}
        dado_2 = {"categoria": categoria.categoria, "produtos": []}

        codigo[0].insert(index-1, dado_1)
        codigo.insert(index, dado_2)

        with open('banco_dados/estoque.json', 'w') as arq:
            json.dump(codigo, arq, indent=4)


    @staticmethod
    def alterar_categoria(alteracao: Categoria, codigo: list):
        index = EstoqueDal.ler_index(alteracao.id)
        
        for c in codigo[0]:
            if c['index'] == index:
                c['categoria'] = alteracao.categoria

        codigo[index]['categoria'] = alteracao.categoria

        with open('banco_dados/estoque.json', 'w') as arq:
            json.dump(codigo, arq, indent=4)
    

    @staticmethod
    def remover_categoria(id_categoria: int, codigo: list):
        index = EstoqueDal.ler_index(id_categoria)

        for p in codigo[index]['produtos']:
            p['id_categoria'] = 0
            codigo[1]['produtos'].append(p)
        
        for i, c in enumerate(codigo[0]):
            if c['index'] == index:
                codigo[0].pop(i)
        codigo.pop(index)
        with open('banco_dados/estoque.json', 'w') as arq:
            json.dump(codigo, arq, indent=4)
     

    @staticmethod
    def ler_produto(index_categoria: int, id_produto: int, codigo: list) -> Produto:
        with open('banco_dados/estoque.json', 'r') as arq:
            produtos = codigo[index_categoria]['produtos']
            
            for p in produtos:
                if p['id'] == id_produto:
                    return Produto(p['id'],
                                   p['id_categoria'],
                                   p['nome'],
                                   p['marca'],
                                   p['preco'],
                                   p['id_fornecedor'])
            return False
