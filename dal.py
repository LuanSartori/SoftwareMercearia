import json
from model import Categoria, Produto


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
    def pesquisar_arquivo(chave: str, valor: str, codigo: json):
        for i, c in enumerate(codigo):
            if str( c[chave] ) == str(valor):
                return i
        return False


    @staticmethod
    def salvar(categoria: Categoria, codigo: json, codigo_estoque: json) -> tuple:
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
    def alterar(id_categoria: int, alteracao: Categoria, i: int, codigo: json, codigo_estoque: json):
        try:
            with open('banco_dados/categorias.json', 'w') as arq:
                codigo[i] = {'id': alteracao.id, 'categoria': alteracao.categoria}
                json.dump(codigo, arq, indent=4)
                EstoqueDal.alterar_categoria(alteracao, codigo_estoque)

                return (True, 'Categoria alterada com sucesso!')
        except:
            return (False, 'Erro interno do sistema')
    

    @staticmethod
    def remover(id_categoria: int, i: int, codigo: json, codigo_estoque: json):
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
    def pesquisar_arquivo(codigo: json, id_categoria: int):
        for i, c in enumerate(codigo):
            if c['id'] == id_categoria:
                return i
    

    @staticmethod
    def salvar_categoria(categoria: Categoria, codigo: json):
        dado = {"id": categoria.id, "categoria": categoria.categoria, "produtos": []}
        codigo.insert(categoria.id, dado)

        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Categoria salva com sucesso!')
        except:
            return (False, 'Não foi possível salvar a categoria!')


    @staticmethod
    def alterar_categoria(alteracao: Categoria, codigo: json):
        index = EstoqueDal.pesquisar_arquivo(codigo, alteracao.id)
        codigo[index]['categoria'] = alteracao.categoria

        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Categoria alterada com sucesso!')
        except:
            return (False, 'Não foi possível alterar a categoria!')
    

    @staticmethod
    def remover_categoria(id_categoria: int, codigo: json):
        index = EstoqueDal.pesquisar_arquivo(codigo, id_categoria)
        for p in codigo[index]['produtos']:
            p['id_categoria'] = 0
            codigo[0]['produtos'].append(p)
        codigo.pop(index)

        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Categoria Removida com sucesso')
        except:
            return (False, 'Não foi possível remover a categoria!')
     

    @staticmethod
    def ler_produto(id_categoria: int, id_produto: int, codigo: json, retorna_obj=True) -> Produto:
        index = EstoqueDal.pesquisar_arquivo(codigo, id_categoria)
        produtos = codigo[index]['produtos']
        
        for i, p in enumerate(produtos):
            if p['id'] == id_produto:
                if retorna_obj:
                    return Produto(p['id'],
                                   p['id_categoria'],
                                   p['nome'],
                                   p['marca'],
                                   p['preco'],
                                   p['quantidade'],
                                   p['id_fornecedor'])
                else:
                    return (i, p)
        return False
    

    @staticmethod
    def gerar_id():
        try:
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                if len( codigo['id_produto']['ids_vazios'] ) == 0:
                    id = codigo['id_produto']['novo_id']
                    codigo['id_produto']['novo_id'] += 1
                else:
                    id = codigo['id_produto']['ids_vazios'][0]
                    codigo['id_produto']['ids_vazios'].pop(0)

                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return id
        except:
            return (False, 'Erro interno do sistema')


    @staticmethod
    def cadastrar_produto(produto: Produto, codigo: json):
        index = EstoqueDal.pesquisar_arquivo(codigo, produto.id_categoria)
        dado = {
            'id':            produto.id,
            'id_categoria':  produto.id_categoria,
            'nome':          produto.nome,
            'marca':         produto.marca,
            'preco':         produto.preco,
            'quantidade':    produto.quantidade,
            'id_fornecedor': produto.id_fornecedor
        }

        codigo[index]['produtos'].append(dado)
        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Produto cadastrado com sucesso!')
        except:
            return (False, 'Não foi possível cadastrar o produto!')
    

    @staticmethod
    def alterar_produto(id_produto: int, id_categoria_atual: int, codigo: json, **kwargs):
        index = EstoqueDal.pesquisar_arquivo(codigo, id_categoria_atual)
        i, produto = EstoqueDal.ler_produto(id_categoria_atual, id_produto, codigo, False)

        alteracao = {
            'id_categoria': kwargs.get('id_categoria'),
            'nome': kwargs.get('nome'),
            'marca': kwargs.get('marca'),
            'preco': kwargs.get('preco'),
            'quantidade': kwargs.get('quantidade'),
            'id_fornecedor': kwargs.get('id_fornecedor')
        }

        for chave, valor in alteracao.items():
            if valor != None:
                produto[chave] = valor
        
        if alteracao['id_categoria'] != None:
            codigo[index]['produtos'].pop(i)
            index = alteracao['id_categoria']
            codigo[index]['produtos'].insert( produto['id'], produto )
        else:
            codigo[index]['produtos'][i] = produto


        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Produto alterado com sucesso!')
        except:
            return (False, 'Não foi possível alterar o produto!')
