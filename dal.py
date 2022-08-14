import json
from operator import itemgetter

from model import Categoria, Funcionario, Produto, Fornecedor, Lote, Cliente, Venda, VendaOnline
from utils import ServerError, IdError


class IdDal:
    @staticmethod
    def gerar_id(chave: str) -> int:
        try:
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                if len( codigo[chave]['ids_vazios'] ) == 0:
                    id_gerado = codigo[chave]['novo_id']
                    codigo[chave]['novo_id'] += 1
                else:
                    id_gerado = codigo[chave]['ids_vazios'][0]
                    codigo[chave]['ids_vazios'].pop(0)

                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
                    return id_gerado
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')


    @staticmethod
    def remover_id(chave: str, id: int):
        try:
            with open('banco_dados/ids.json', 'r') as arq:
                codigo = json.load(arq)
                codigo[chave]['ids_vazios'].append(id)
                codigo[chave]['ids_vazios'].sort()

                with open('banco_dados/ids.json', 'w') as arq:
                    json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possívela acessar o banco de dados!')


# --------------------------------------------------
# --------------------------------------------------


class CategoriaDal:
    @staticmethod
    def ler_arquivo() -> json:
        try:
            with open('banco_dados/categorias.json', 'r') as arq:
                return json.load(arq)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def salvar_arquivo(codigo: json) -> bool:
        try:
            with open('banco_dados/categorias.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')


    @staticmethod
    def pesquisar_arquivo(chave: str, valor: str, codigo: json) -> int:
        for index, c in enumerate(codigo):
            if str( c[chave] ) == str(valor):
                return index
        return False


    @staticmethod
    def salvar_categoria(categoria: Categoria, codigo: json, codigo_estoque: json) -> bool:
        nova_categoria = {'id': categoria.id, 'categoria': categoria.categoria}
        codigo.append(nova_categoria)
        codigo = sorted(codigo, key=itemgetter('id'))

        CategoriaDal.salvar_arquivo(codigo)
        EstoqueDal.salvar_categoria(categoria, codigo_estoque)
        return True


    @staticmethod
    def alterar_categoria(index_categoria: int, alteracao: Categoria,
                          codigo: json, codigo_estoque: json) -> bool:
        
        codigo[index_categoria] = {'id': alteracao.id, 'categoria': alteracao.categoria}

        CategoriaDal.salvar_arquivo(codigo)
        EstoqueDal.alterar_categoria(alteracao, codigo_estoque)
        return True
    

    @staticmethod
    def remover_categoria(id_categoria: int, index: int, codigo: json, codigo_estoque: json) -> bool:
        codigo.pop(index)
        CategoriaDal.salvar_arquivo(codigo)

        # adiciona o id removido ao banco de dados e remove a categoria do estoque
        IdDal.remover_id('id_categoria', id_categoria)
        EstoqueDal.remover_categoria(id_categoria, codigo_estoque)

        return True


# --------------------------------------------------
# --------------------------------------------------


class EstoqueDal:
    @staticmethod
    def ler_arquivo() -> json:
        try:
            with open('banco_dados/estoque.json', 'r') as arq:
                return json.load(arq)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def salvar_arquivo(codigo: json):
        try:
            with open('banco_dados/estoque.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def pesquisar_categoria(codigo: json, id_categoria: int) -> int:
        for i, c in enumerate(codigo):
            if c['id'] == id_categoria:
                return i
        return False
    

    @staticmethod
    def salvar_categoria(categoria: Categoria, codigo: json) -> bool:
        dado = {"id": categoria.id, "categoria": categoria.categoria, "produtos": []}
        codigo.append(dado)
        codigo = sorted(codigo, key=itemgetter('id'))

        EstoqueDal.salvar_arquivo(codigo)
        return True


    @staticmethod
    def alterar_categoria(alteracao: Categoria, codigo: json) -> bool:
        index = EstoqueDal.pesquisar_categoria(codigo, alteracao.id)
        codigo[index]['categoria'] = alteracao.categoria

        EstoqueDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def remover_categoria(id_categoria: int, codigo: json) -> bool:
        index = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
        for p in codigo[index]['produtos']:
            p['id_categoria'] = 0
            codigo[1]['produtos'].append(p)
        codigo.pop(index)

        EstoqueDal.salvar_arquivo(codigo)
        return True


    @staticmethod
    def ler_produto_por_categoria(id_categoria: int, id_produto: int, codigo: json, retorna_obj=True) -> tuple:
        index = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
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
    def ler_produto_por_id(id_produto: int, codigo: json, retorna_obj=True) -> tuple:
        for index_categoria, categoria in enumerate(codigo):
            if index_categoria == 0:
                continue

            for index_produto, produto in enumerate(categoria['produtos']):
                if produto['id'] == id_produto:
                    if retorna_obj:
                        return (index_categoria, index_produto, 
                        Produto(produto['id'],
                                produto['id_categoria'],
                                produto['nome'],
                                produto['marca'],
                                produto['preco'],
                                produto['quantidade'],
                                produto['id_fornecedor']))
                    else:
                        return (index_categoria, index_produto, produto)
        return False
                
                
    @staticmethod
    def cadastrar_produto(produto: Produto, codigo: json) -> bool:
        index = EstoqueDal.pesquisar_categoria(codigo, produto.id_categoria)
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

        EstoqueDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def alterar_produto(id_produto: int, id_categoria_atual: int, codigo: json, **kwargs) -> bool:
        index = EstoqueDal.pesquisar_categoria(codigo, id_categoria_atual)
        i, produto = EstoqueDal.ler_produto_por_categoria(id_categoria_atual, id_produto, codigo, False)

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


        EstoqueDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def remover_produto(id_produto: int, id_categoria: int, codigo: json) -> bool:
        i, p = EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo, False)
        codigo[id_categoria]['produtos'].pop(i)
        
        EstoqueDal.salvar_arquivo(codigo)
        IdDal.remover_id('id_produto', id_produto)
        return True


    @staticmethod
    def transferir_vencido(produto: dict, quantidade: list, codigo: json) -> json:
        dado = {
            'id':         produto['id'],
            'nome':       produto['nome'],
            'vencido_em': quantidade[0],
            'quantidade': quantidade[1]
        }
        
        # verifica se a data do produto vencido já não existe na categoria vencidos
        for i, v in enumerate(codigo[0]['produtos']):
            if v['vencido_em'] == dado['vencido_em']:
                codigo[0]['produtos'][i]['quantidade'] += dado['quantidade']
                return codigo
        
        # vai na categoria "vencidos" e adiciona o produto vencido
        codigo[0]['produtos'].append(dado)
        return codigo
    

    @staticmethod
    def remover_vencidos(codigo: json, id_produto=None) -> bool:
        if not id_produto:
            codigo[0]['produtos'] = []
        else:
            for i, p in enumerate(codigo[0]['produtos']):
                if p['id'] == id_produto:
                    codigo[0]['produtos'].pop(i)
        
        EstoqueDal.salvar_arquivo(codigo)
        return True


# --------------------------------------------------
# --------------------------------------------------


class FornecedorDal:
    @staticmethod
    def ler_arquivo() -> json:
        try:
            with open('banco_dados/fornecedores.json', 'r') as arq:
                return json.load(arq)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def salvar_arquivo(codigo: json):
        try:
            with open('banco_dados/fornecedores.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def ler_fornecedor(codigo: json, id_fornecedor: int, retorna_obj=True) -> tuple:
        for i, f in enumerate(codigo):
            if f['id'] == id_fornecedor:
                
                if retorna_obj:
                    return (i, Fornecedor(f['id'],
                                          f['nome'],
                                          f['telefone'],
                                          f['email'],
                                          f['cnpj'],
                                          f['lotes']
                                          ))
                else:
                    return (i, f)
        return False


    @staticmethod
    def cadastrar_fornecedor(fornecedor: Fornecedor, codigo: json) -> bool:
        dado = {
            "id":       fornecedor.id,
            "nome":     fornecedor.nome,
            "telefone": fornecedor.telefone,
            "email":    fornecedor.email,
            "cnpj":     fornecedor.cnpj,
            "lotes":    fornecedor.lotes
        }

        codigo.append(dado)
        codigo = sorted(codigo, key=itemgetter('id'))

        FornecedorDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def alterar_fornecedor(id_fornecedor: int, codigo: json, **kwargs) -> tuple:
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor)

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
            FornecedorDal.salvar_arquivo(codigo)
            return (True, 'Fornecedor alterado com sucesso!')
        except:
            return (False, 'Não foi possível alterar o fornecedor!')


    @staticmethod
    def remover_fornecedor(id_fornecedor: int, codigo: json) -> bool:
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor)
        codigo.pop(index)

        FornecedorDal.salvar_arquivo(codigo)
        IdDal.remover_id('id_fornecedor', id_fornecedor)
        return True


    @staticmethod
    def ler_lote(id_fornecedor: int, codigo: json, id_lote=None, retorna_obj=True) -> tuple:
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor, False)

        if not id_lote != None:
            return codigo[index]['lotes']
        
        for i, lote in enumerate(codigo[index]['lotes']):
            if lote['id_lote'] == id_lote:

                if retorna_obj:
                    return (i, Lote(lote['id_lote'],
                                    lote['preco_lote'],
                                    lote['id_produto'],
                                    lote['id_categoria'],
                                    lote['quantidade'],
                                    lote['tempo'])
                                    )
                else:
                    return (i, lote)
        return False


    @staticmethod
    def cadastrar_lote(id_fornecedor: int, lote: Lote, codigo: json) -> bool:
        index, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor)

        dado = {
                 'id_lote':    lote.id_lote,
              'preco_lote': lote.preco_lote,
              'id_produto': lote.id_produto,
            'id_categoria': lote.id_categoria,
              'quantidade': lote.quantidade,
                   'tempo':      lote.tempo
        }
        codigo[index]['lotes'].append(dado)
        codigo[index]['lotes'] = sorted(codigo[index]['lotes'], key=itemgetter('id_lote'))

        FornecedorDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def alterar_lote(id_fornecedor: int, id_lote: int, codigo: json, **kwargs) -> bool:
        index_fornecedor, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor)
        index_lote, lote = FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False)

        alteracao = {
            'preco_lote':   kwargs.get('preco_lote'),
            'id_produto':   kwargs.get('id_produto'),
            'id_categoria': kwargs.get('id_categoria'),
            'quantidade':   kwargs.get('quantidade'),
            'tempo':        kwargs.get('tempo')
        }

        for chave, valor in alteracao.items():
            if valor != None:
                lote[chave] = valor
        
        codigo[index_fornecedor]['lotes'][index_lote] = lote

        FornecedorDal.salvar_arquivo(codigo)
        return (True, 'Lote alterado com sucesso!')


    @staticmethod
    def remover_lote(id_fornecedor: int, id_lote: int, codigo: json) -> bool:
        index_fornecedor, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor, False)
        index_lote, lote = FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False)

        codigo[index_fornecedor]['lotes'].pop(index_lote)

        FornecedorDal.salvar_arquivo(codigo)
        IdDal.remover_id('id_lote', id_lote)
        return True
    

    @staticmethod
    def lote_recebido(codigo_fornecedor: json, codigo_estoque: json) -> bool:
        FornecedorDal.salvar_arquivo(codigo_fornecedor)
        EstoqueDal.salvar_arquivo(codigo_estoque)
        return True


# --------------------------------------------------
# --------------------------------------------------


class FuncionarioDal:
    @staticmethod
    def ler_arquivo() -> json:
        try:
            with open('banco_dados/funcionarios.json', 'r') as arq:
                return json.load(arq)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def salvar_arquivo(codigo: json):
        try:
            with open('banco_dados/funcionarios.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    
    
    @staticmethod
    def ler_funcionario(codigo: json, id_funcionario: int, admin=False, retorna_obj=True) -> tuple:
        if admin:
            for i, f in enumerate(codigo['admins']):
                if f['id'] == id_funcionario:
                    
                    if retorna_obj:
                        return (i, Funcionario(f['id'],
                                               f['nome'],
                                               f['cpf'],
                                               f['cargo'],
                                               f['senha'],
                                               f['telefone'],
                                               f['email']))
                    return (i, f)
        else:
            for i, f in enumerate(codigo['funcionarios']):
                if f['id'] == id_funcionario:

                    if retorna_obj:
                        return (i, Funcionario(f['id'],
                                               f['nome'],
                                               f['cpf'],
                                               f['cargo'],
                                               f['senha'],
                                               f['telefone'],
                                               f['email']))
                    return (i, f)
        
        return False
    

    @staticmethod
    def cadastrar_funcionario(funcionario: Funcionario, codigo: json, admin=False, posicao=None) -> bool:
        dado = {
            'id':       funcionario.id,
            'cpf':      funcionario.cpf,
            'nome':     funcionario.nome,
            'telefone': funcionario.telefone,
            'email':    funcionario.email,
            'cargo':    funcionario.cargo,
            'senha':    funcionario.senha
        }

        if admin:
            dado['posicao'] = posicao
            codigo['admins'].append(dado)
            codigo['admins'] = sorted(codigo['admins'], key=itemgetter('id'))
        else:
            codigo['funcionarios'].append(dado)
            codigo['funcionarios'] = sorted(codigo['funcionarios'], key=itemgetter('id'))
        
        FuncionarioDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def alterar_funcionario(id_funcionario: int, codigo: json, admin=False, posicao=None, **kwargs) -> bool:
        index, funcionario = FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=admin, retorna_obj=False)

        alteracao = {
            "cpf":      kwargs.get('cpf'),
            "nome":     kwargs.get('nome'),
            "telefone": kwargs.get('telefone'),
            "email":    kwargs.get('email'),
            "cargo":    kwargs.get('cargo'),
            "senha":    kwargs.get('senha')
        }
        if admin:
            alteracao['posicao'] = posicao
        for chave, valor in alteracao.items():
            if valor != None:
                funcionario[chave] = valor
        
        if admin:
            codigo['admins'][index] = funcionario
        else:
            codigo['funcionarios'][index] = funcionario

        
        FuncionarioDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def remover_funcionario(id_funcionario: int, codigo: json, admin=False) -> bool:
        index, funcionario = FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=admin, retorna_obj=False)

        if admin:
            codigo['admins'].pop(index)
        else:
            codigo['funcionarios'].pop(index)

        FuncionarioDal.salvar_arquivo(codigo)
        if admin:
            IdDal.remover_id('id_admin', id_funcionario)
        else:
            IdDal.remover_id('id_funcionario', id_funcionario)

        return True


# --------------------------------------------------
# --------------------------------------------------


class ClienteDal:
    @staticmethod
    def ler_arquivo() -> json:
        try:
            with open('banco_dados/clientes.json', 'r') as arq:
                return json.load(arq)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def salvar_arquivo(codigo: json):
        try:
            with open('banco_dados/clientes.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def ler_cliente(codigo: json, id: int, retorna_obj=True) -> tuple:
        for i, cliente in enumerate(codigo):
            if cliente['id'] == id:

                if retorna_obj:
                    return (i, Cliente(cliente['nome'],
                                       cliente['cpf'],
                                       cliente['id'],
                                       cliente['senha'],
                                       cliente['telefone'],
                                       cliente['email']))
                return(i, cliente)
        return False
    

    @staticmethod
    def cadastrar_cliente(cliente: Cliente, codigo: json) -> bool:
        dado = {
            'id': cliente.id,
            'nome': cliente.nome,
            'cpf': cliente.cpf,
            'telefone': cliente.telefone,
            'email': cliente.email,
            'senha': cliente.senha,
            'carrinho': cliente.carrinho
        }

        codigo.append(dado)
        codigo = sorted(codigo, key=itemgetter('id'))

        ClienteDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def alterar_cliente(id_cliente: int, codigo: json, **kwargs) -> bool:
        index, cliente = ClienteDal.ler_cliente(codigo, id_cliente, False)

        alteracao = {
            'nome': kwargs.get('nome'),
            'cpf': kwargs.get('cpf'),
            'telefone': kwargs.get('telefone'),
            'email': kwargs.get('email'),
            'senha': kwargs.get('senha')
        }
        for chave, valor in alteracao.items():
            if valor != None:
                cliente[chave] = valor
        
        codigo[index] = cliente
        ClienteDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def remover_cliente(id_cliente: int, codigo: json) -> bool:
        index, cliente = ClienteDal.ler_cliente(codigo, id_cliente)
        codigo.pop(index)

        ClienteDal.salvar_arquivo(codigo)
        IdDal.remover_id('id_cliente', id_cliente)
        return True


# --------------------------------------------------
# --------------------------------------------------


class VendaDal:
    @staticmethod
    def ler_arquivo() -> json:
        try:
            with open('banco_dados/vendas.json', 'r') as arq:
                return json.load(arq)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
	

    @staticmethod
    def salvar_arquivo(codigo: json):
        try:
            with open('banco_dados/vendas.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')

	
    @staticmethod
    def ler_venda(id_venda: int, codigo: json, online=False, retorna_obj=True) -> tuple:
        if online:
            for i, v in enumerate(codigo['online']):
                if v['id_venda'] == id_venda:
                    
                    if retorna_obj:
                        return (i, Venda(v['id_venda'],
                                        v['id_cliente'],
                                        v['id_produto'],
                                        v['quantidade'],
                                        v['preco_unitario']))
                    return (i, v)
        else:
            for i, v in enumerate(codigo['fisica']):
                if v['id_venda'] == id_venda:
                    
                    if retorna_obj:
                        return (i, Venda(v['id_venda'],
                                        v['id_cliente'],
                                        v['id_produto'],
                                        v['quantidade'],
                                        v['preco_unitario']))
                    return (i, v)
        return False


    @staticmethod
    def cadastrar_venda(venda: Venda, codigo: json) -> bool:
        dado = {
            "id_venda":       venda.id_venda,
            "id_funcionario": venda.id_funcionario,
            "produtos":       venda.lista_produtos,
            "preco_total":    venda.preco_total,
            "cpf_cliente":    venda.cpf_cliente
        }
	
        codigo['fisica'].append(dado)
        codigo['fisica'] = sorted(codigo['fisica'], key=itemgetter('id_venda'))
		
        VendaDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def cadastrar_venda_online(venda: VendaOnline, codigo: json) -> bool:
        dado = {
            "id_venda":    venda.id_venda,
            "produtos":    venda.lista_produtos,
            "preco_total": venda.preco_total,
            "id_cliente":  venda.id_cliente,
            "cpf_cliente": venda.cpf_cliente
        }
		
        codigo['online'].append(dado)
        codigo['online'] = sorted(codigo['online'], key=itemgetter('id_venda'))
		
        VendaDal.salvar_arquivo(codigo)
        return True
	
	
    @staticmethod
    def alterar_venda(id_venda: int, codigo: json, **kwargs) -> bool:
        index, venda = VendaDal.ler_venda(id_venda, codigo, online=False, retorna_obj=False)

        alteracao = {
			"produtos":       kwargs.get('produtos'),
			"preco_total":    kwargs.get('preco_total')
		}
        for chave, valor in alteracao.items():
            if valor != None:
                venda[chave] = valor
        
        codigo['fisica'][index] = venda

        VendaDal.salvar_arquivo(codigo)
        return True
    

    @staticmethod
    def alterar_venda_online(id_venda: int, codigo: json, **kwargs) -> bool:
        index, venda = VendaDal.ler_venda(id_venda, codigo, online=True, retorna_obj=False)

        alteracao = {
			"produtos":    kwargs.get('produtos'),
			"preco_total": kwargs.get('preco_total')
		}
        for chave, valor in alteracao.items():
            if valor != None:
                venda[chave] = valor
        
        codigo['online'][index] = venda

        VendaDal.salvar_arquivo(codigo)
        return True

	
    @staticmethod
    def remover_venda(id_venda: int, codigo: json, online=False) -> bool:
        index, venda = VendaDal.ler_venda(id_venda, codigo, online, retorna_obj=False)

        if online:
            codigo['online'].pop(index)
        else:
            codigo['fisica'].pop(index)

        VendaDal.salvar_arquivo(codigo)
        IdDal.remover_id('id_venda', id_venda)
        return True


# --------------------------------------------------
# --------------------------------------------------


class CaixaDal:
    @staticmethod
    def ler_arquivo() -> json:
        try:
            with open('banco_dados/caixas.json', 'r') as arq:
                return json.load(arq)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
	

    @staticmethod
    def salvar_arquivo(codigo: json):
        try:
            with open('banco_dados/caixas.json', 'w') as arq:
                json.dump(codigo, arq, indent=4)
        except:
            raise ServerError('Não foi possível acessar o banco de dados!')
    

    @staticmethod
    def ler_caixa(numero_caixa: int, codigo: json):
        for i, c in enumerate(codigo):
            if c['numero_caixa'] == numero_caixa:
                return (i, c)
        return False


    @staticmethod
    def cadastrar_caixa(numero_caixa: int, valor_no_caixa: float) -> bool:
        dado = {
            "numero_caixa":   numero_caixa,
            "valor_no_caixa": valor_no_caixa
        }
        
        CaixaDal.salvar_arquivo(dado)
        return True
    

    @staticmethod
    def alterar_caixa(numero_caixa: int, codigo: json, **kwargs) -> bool:
        index, caixa = CaixaDal.ler_caixa(numero_caixa, codigo)

        alteracao = {
			"numero_caixa":   kwargs.get('numero_caixa'),
			"valor_no_caixa": kwargs.get('valor_no_caixa')
		}
        for chave, valor in alteracao.items():
            if valor != None:
                caixa[chave] = valor
        
        codigo[index] = caixa

        CaixaDal.salvar_arquivo(codigo)
        return True


    @staticmethod
    def remover_caixa(numero_caixa: int, codigo: json) -> bool:
        index, caixa = CaixaDal.ler_caixa(numero_caixa, codigo)
        codigo.pop(index)

        CaixaDal.salvar_arquivo(codigo)
        return True


# --------------------------------------------------
# --------------------------------------------------
