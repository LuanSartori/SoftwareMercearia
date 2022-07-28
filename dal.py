import json
from operator import itemgetter
from model import Categoria, Produto, Fornecedor, Lote


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
        for index, c in enumerate(codigo):
            if str( c[chave] ) == str(valor):
                return index
        return False


    @staticmethod
    def salvar(categoria: Categoria, codigo: json, codigo_estoque: json) -> tuple:
        try:
            nova_categoria = {'id': categoria.id, 'categoria': categoria.categoria}
            codigo.append(nova_categoria)
            codigo = sorted(codigo, key=itemgetter('id'))

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
    def remover(id_categoria: int, index: int, codigo: json, codigo_estoque: json):
        try:
            with open('banco_dados/categorias.json', 'w') as arq:
                codigo.pop(index)
                json.dump(codigo, arq, indent=4)

            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                codigo['id_categoria']['ids_vazios'].append(id_categoria)
                codigo['id_categoria']['ids_vazios'].sort()
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
        codigo.append(dado)
        codigo = sorted(codigo, key=itemgetter('id'))

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
    def ler_produto(id_categoria: int, id_produto: int, codigo: json, retorna_obj=True) -> tuple:
        index = EstoqueDal.pesquisar_arquivo(codigo, id_categoria)
        produtos = codigo[index]['produtos']
        
        for i, p in enumerate(produtos):
            if p['id'] == id_produto:
                if retorna_obj:
                    return (i, Produto(p['id'],
                                   p['id_categoria'],
                                   p['nome'],
                                   p['marca'],
                                   p['preco'],
                                   p['quantidade'],
                                   p['id_fornecedor']))
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
        codigo[index]['produtos'] = sorted(codigo[index]['produtos'], key=itemgetter('id'))
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
            'id_categoria':  kwargs.get('id_categoria'),
            'nome':          kwargs.get('nome'),
            'marca':         kwargs.get('marca'),
            'preco':         kwargs.get('preco'),
            'quantidade':    kwargs.get('quantidade'),
            'id_fornecedor': kwargs.get('id_fornecedor')
        }

        for chave, valor in alteracao.items():
            if valor != None:
                produto[chave] = valor
        
        if alteracao['id_categoria'] != None:
            codigo[index]['produtos'].pop(i)
            index = alteracao['id_categoria']
            codigo[index]['produtos'].append(produto)
            codigo[index]['produtos'] = sorted(codigo[index]['produtos'], key=itemgetter('id'))
        else:
            codigo[index]['produtos'][i] = produto


        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Produto alterado com sucesso!')
        except:
            return (False, 'Não foi possível alterar o produto!')
    

    @staticmethod
    def remover_produto(id_produto: int, id_categoria: int, codigo: json) -> tuple:
        i, p = EstoqueDal.ler_produto(id_categoria, id_produto, codigo, False)
        codigo[id_categoria]['produtos'].pop(i)
        
        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
            
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                codigo['id_produto']['ids_vazios'].append(id_produto)
                codigo['id_produto']['ids_vazios'].sort()
                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return (True, 'Produto removido com sucesso!')
        except:
            return (False, 'Não foi possível remover o produto!')


# --------------------------------------------------
# --------------------------------------------------


class FornecedorDal:
    @staticmethod
    def ler_arquivo():
        try:
            with open('banco_dados/fornecedores.json', 'r') as arq:
                return json.load(arq)
        except:
            return False
    

    @staticmethod
    def ler_fornecedor(codigo, id, retorna_obj=True):
        for i, f in enumerate(codigo):
            if f['id'] == id:
                
                if retorna_obj:
                    return (i, Fornecedor(f['id'],
                                          f['nome'],
                                          f['telefone'],
                                          f['email'],
                                          f['cnpj']))
                else:
                    return (i, f)
        return False
    

    @staticmethod
    def gerar_id_fornecedor():
        try:
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                if len( codigo['id_fornecedor']['ids_vazios'] ) == 0:
                    id = codigo['id_fornecedor']['novo_id']
                    codigo['id_fornecedor']['novo_id'] += 1
                else:
                    id = codigo['id_fornecedor']['ids_vazios'][0]
                    codigo['id_fornecedor']['ids_vazios'].pop(0)

                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return id
        except:
            return (False, 'Erro interno do sistema')


    @staticmethod
    def cadastrar_fornecedor(fornecedor: Fornecedor, codigo: json) -> tuple:
        dado = {
            "id": fornecedor.id,
            "nome": fornecedor.nome,
            "telefone": fornecedor.telefone,
            "email": fornecedor.email,
            "cnpj": fornecedor.cnpj
        }

        codigo.append(dado)
        codigo = sorted(codigo, key=itemgetter('id'))
        try:
            with open('banco_dados/fornecedores.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Fornecedor cadastrado com sucesso!')
        except:
            return (False, 'Não foi possível cadastrar o fornecedor')
    

    @staticmethod
    def alterar_fornecedor(id: int, codigo: json, **kwargs):
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id)

        alteracao = {
            "nome":     kwargs.get('nome'),
            "telefone": kwargs.get('telefone'),
            "email":    kwargs.get('email'),
            "cnpj":     kwargs.get('cnpj')
        }

        for chave, valor in alteracao.items():
            if valor != None:
                fornecedor[chave] = valor
        
        codigo[index] = fornecedor
        try:
            with open('banco_dados/fornecedores.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Fornecedor alterado com sucesso!')
        except:
            return (False, 'Não foi possível alterar o fornecedor!')


    @staticmethod
    def remover_fornecedor(id_fornecedor: int, codigo: json):
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor)
        codigo.pop(index)

        try:
            with open('banco_dados/fornecedores.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
            
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                codigo['id_fornecedor']['ids_vazios'].append(id)
                codigo['id_fornecedor']['ids_vazios'].sort()
                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return (True, 'Fornecedor removido com sucesso!')
        except:
            return (False, 'Não foi possível remover este fornecedor!')


    @staticmethod
    def ler_lote(id_fornecedor: int, codigo: json, id_lote=None, retorna_obj=True):
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor, False)

        if not id_lote != None:
            return codigo[index]['lotes']
        
        for i, lote in enumerate(codigo[index]['lotes']):
            if lote['id_lote'] == id_lote:

                if retorna_obj:
                    return (i, Lote(lote['id_lote'],
                                    lote['preco_lote'],
                                    lote['id_produto'],
                                    lote['quantidade'],
                                    lote['tempo'])
                                    )
                else:
                    return (i, lote)
        return False

    
    @staticmethod
    def gerar_id_lote():
        try:
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                if len( codigo['id_lote']['ids_vazios'] ) == 0:
                    id = codigo['id_lote']['novo_id']
                    codigo['id_lote']['novo_id'] += 1
                else:
                    id = codigo['id_lote']['ids_vazios'][0]
                    codigo['id_lote']['ids_vazios'].pop(0)

                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return id
        except:
            return (False, 'Erro interno do sistema')


    @staticmethod
    def cadastrar_lote(id_fornecedor: int, lote: Lote, codigo: json):
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor)

        dado = {
            'id_lote':    lote.id_lote,
            'preco_lote': lote.preco_lote,
            'id_produto': lote.id_produto,
            'quantidade': lote.quantidade,
            'tempo':      lote.tempo
        }
        codigo[index]['lotes'].append(dado)
        codigo[index]['lotes'] = sorted(codigo[index]['lotes'], key=itemgetter('id_lote'))
        try:
            with open('banco_dados/fornecedores.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Lote cadastrado com sucesso!')
        except:
            return (False, 'Não foi possível cadastrar o lote!')
    

    @staticmethod
    def alterar_lote(id_fornecedor: int, id_lote: int, codigo: json, **kwargs):
        index_fornecedor, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor)
        index_lote, lote = FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False)

        alteracao = {
            'preco_lote':   kwargs.get('preco_lote'),
            'id_produto':   kwargs.get('id_produto'),
            'quantidade':   kwargs.get('quantidade'),
            'tempo':        kwargs.get('tempo')
        }

        for chave, valor in alteracao.items():
            if valor != None:
                lote[chave] = valor
        
        codigo[index_fornecedor]['lotes'][index_lote] = lote
        try:
            with open('banco_dados/fornecedores.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
                return (True, 'Lote alterado com sucesso!')
        except:
            return (False, 'Não foi possível alterar o lote!')


    @staticmethod
    def remover_lote(id_fornecedor: int, id_lote: int, codigo: json):
        print('Tá executando!')
        index_fornecedor, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor, False)
        index_lote, lote = FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False)

        codigo[index_fornecedor]['lotes'].pop(index_lote)

        try:
            with open('banco_dados/fornecedores.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
            
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                codigo['id_lote']['ids_vazios'].append(id_lote)
                codigo['id_lote']['ids_vazios'].sort()

                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return (True, 'Lote removido com sucesso!')
        except:
            return (False, 'Não foi possível remover o lote!')