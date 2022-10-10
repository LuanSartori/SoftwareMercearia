from operator import itemgetter
import datetime

from model import *
from dal import *
from utils import *


# --------------------------------------------------
# --------------------------------------------------


class CategoriaController():
    @staticmethod
    def cadastrar_categoria(categoria: str) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()

        if CategoriaDal.pesquisar_arquivo('categoria', categoria, codigo):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')
        categoria.lower()

        
        id = IdDal.gerar_id('id_categoria')
        categoria = Categoria(categoria, id)
        return CategoriaDal.salvar_categoria(categoria, codigo, codigo_estoque)


    @staticmethod
    def alterar_categoria(id_categoria: int, categoria: str) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()

        index_categoria = CategoriaDal.pesquisar_arquivo('id', id_categoria, codigo)
        if index_categoria == None:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)

        if CategoriaDal.pesquisar_arquivo('categoria', categoria, codigo):
            raise IdError(False, 'Já existe uma categoria com esse nome')
        if len(categoria) > 30:
            raise IdError(False, 'Esse nome é muito grande!')
        categoria.lower()


        categoria = Categoria(categoria, id_categoria)
        return CategoriaDal.alterar_categoria(index_categoria, categoria, codigo, codigo_estoque)


    @staticmethod
    def remover_categoria(id_categoria: int) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
            
        index = CategoriaDal.pesquisar_arquivo('id', str(id_categoria), codigo)
        if index == None:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)
        
        if id_categoria == 0:
            raise ValueError('RAISE', f'Não é possível remover a categoria "Nenhuma"')
        elif id_categoria == 1:
            raise ValueError('RAISE', f'Não é possível remover a categoria: "vencidos')

        return CategoriaDal.remover_categoria(id_categoria, index, codigo, codigo_estoque)


    @staticmethod
    def listar_categorias():
        """
        Lista todas as categorias e retorna uma lista com os seus ids::

            '''
            ID  | Nome
            ------------------------------
            001 | Vencidos
            002 | Nenhuma
            003 | Frutas
            '''
            # return [0, 1, 5]

        ---

        Returns:
            list: Lista com os ids das categorias listadas em ordem
        """
        codigo = CategoriaDal.ler_arquivo()

        ids_categoria = []

        print(f'{"ID":3} | Nome')
        print('-'*30)
        for i, categoria in enumerate(codigo):
            print(f'{str(i+1).zfill(3):<3} | {categoria["categoria"].capitalize()}')
            ids_categoria.append(categoria['id'])
        print()

        return ids_categoria


# --------------------------------------------------
# --------------------------------------------------


class EstoqueController:
    @staticmethod
    def cadastrar_produto(id_categoria: int, nome: str, marca: str, preco: float,
                          quantidade: list=[], id_fornecedor: int=None) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        if len(nome) > 40:
            raise ValueError('RAISE', 'Este nome é grande demais')
        if len(marca) > 20:
            raise ValueError('RAISE', 'O nome da marca é grande demais!')
        if CategoriaDal.pesquisar_arquivo('id', id_categoria, codigo) == None:
            raise IdError('Está categoria não existe!')
        
        index = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
        for p in codigo_estoque[index]['produtos']:
            if p['nome'] == nome:
                raise ValueError('RAISE', 'Já existe um produto com esse nome')

        try:
            for datas in quantidade:
                validade_obj = datetime.datetime.strptime(datas[0], '%d/%m/%Y')
                if validade_obj <= datetime.datetime.now():
                    raise ValueError('RAISE', 'O produto já está vencido!')
        except ValueError as arg:
            raise ValueError('RAISE', 'Data de validade inválida!', arg.args[1])

        id = IdDal.gerar_id('id_produto')            
        produto = Produto(id, id_categoria, nome, marca, preco, quantidade, id_fornecedor)
        return EstoqueDal.cadastrar_produto(produto, codigo_estoque)


    @staticmethod
    def alterar_produto(id_produto:int, id_categoria_atual: int, **kwargs) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()

        if not EstoqueDal.ler_produto_por_categoria(id_categoria_atual, id_produto, codigo_estoque, True):
            raise IdError('Não existe uma produto com esse ID', id_produto)
        if CategoriaDal.pesquisar_arquivo('id', str(id_categoria_atual), codigo) == None:
            raise IdError('Não existe uma categoria com esse ID', id_categoria_atual)
        
        if kwargs.get('nome') != None and len(kwargs.get('nome')) > 40:
            raise ValueError('RAISE', 'Este nome é grande demais!')
        if kwargs.get('marca') != None and len(kwargs.get('marca')) > 20:
            raise ValueError('RAISE', 'O nome da marca é grande demais!')
        
        return EstoqueDal.alterar_produto(id_produto, id_categoria_atual, codigo_estoque, **kwargs)


    @staticmethod
    def remover_produto(id_categoria: int, id_produto: int) -> bool:
        codigo = CategoriaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_fornecedores = FornecedorDal.ler_arquivo()
        
        if not EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo_estoque, True):
            raise IdError('Não existe uma produto com esse ID', id_produto)
        if CategoriaDal.pesquisar_arquivo('id', str(id_categoria), codigo) == None:
            raise IdError('Não existe uma categoria com esse ID', id_categoria)

        # validando se o produto está vinculado a um lote
        for i_f, fornecedor in enumerate(codigo_fornecedores):
            for i_l, lote in enumerate(fornecedor['lotes']):
                if lote['id_produto'] == id_produto:
                    raise Exception( {'id_fornecedor': fornecedor['id'], 'id_lote': lote['id_lote']} )
        
        return EstoqueDal.remover_produto(id_produto, id_categoria, codigo_estoque)


    @staticmethod
    def verificar_validade() -> bool:
        """
        Verifica todos os produtos do estoque em busca de algum vencido

        ---

        Returns:
            False (bool): Nenhum produto vencido encontrado
            pdts_vencidos (int): Número de produtos vencidos encontrados
        """
        codigo = EstoqueDal.ler_arquivo()

        data_hoje = datetime.datetime.now()
        pdts_vencidos = 0
        x = False

        for index_categoria, categoria in enumerate(codigo):

            # sem contar a categoria vencidos
            if index_categoria == 0:
                continue
            
            for index_produto, produto in enumerate(categoria['produtos']):

                # transforma todas as datas em objetos datetime e os ordena
                for i, q in enumerate(produto['quantidade']):
                    d = datetime.datetime.strptime(q[0], '%d/%m/%Y')
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d

                codigo[index_categoria]['produtos'][index_produto]['quantidade'] = sorted(
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'],
                    key=itemgetter(0))

                # faz a verificacao dos produtos vencidos
                for quantidade in produto['quantidade']:
                    if quantidade[0] <= data_hoje:
                        x = True
                        pdts_vencidos += quantidade[1]

                        quantidade[0] = datetime.datetime.strftime(quantidade[0], '%d/%m/%Y')
                        codigo = EstoqueDal.transferir_vencido(produto, quantidade, codigo)

                        codigo[index_categoria]['produtos'][index_produto]['quantidade'].pop(0)

                # transforma todos os objetos datetime em string para armazenar no banco de dados
                for i, q in enumerate(produto['quantidade']):
                    d = datetime.datetime.strftime(q[0], '%d/%m/%Y')
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d
        
        EstoqueDal.salvar_arquivo(codigo)
        return pdts_vencidos if x else False
    

    @staticmethod
    def gerar_relatorio_vencidos():
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_categoria = CategoriaDal.ler_arquivo()
        vencidos = codigo_estoque[0]['produtos']
        total_vencidos = 0
        # Cria um dicionário para contar quantas unidades venceram de cada produto
        pdt_vencido = {str(pdt['id']): [0, pdt['nome']] for pdt in vencidos}
        pdt_vencido = dict(sorted(pdt_vencido.items(), key=itemgetter(0)))

        relatorio = 'Relatório dos Produtos Vencidos:\n\n'
        relatorio += '-'*103 + '\n'
        
        # Transforma todas as datas str em objetos datetime, ordena, e retorna para str
        for i, v in enumerate(vencidos):
            v['vencido_em'] = datetime.datetime.strptime(v['vencido_em'], '%d/%m/%Y')
        vencidos = sorted(vencidos, key=itemgetter('vencido_em'))
        for i, v in enumerate(vencidos):
            v['vencido_em'] = datetime.datetime.strftime(v['vencido_em'], '%d/%m/%Y')

        relatorio += f'{"Categoria":30} | {"Produto":40} | {"Vencido em":14} | {"Quantidade":10}\n\n'
        for pdt in vencidos:
            categoria = codigo_categoria[CategoriaDal.pesquisar_arquivo('id', pdt['id_categoria'], codigo_categoria)]['categoria'].capitalize()
            total_vencidos += pdt['quantidade']
            pdt_vencido[str(pdt['id'])][0] += pdt['quantidade']

            relatorio += f'{categoria:30} | {pdt["nome"]:40} | {pdt["vencido_em"]:14} | {pdt["quantidade"]:10}\n'

        relatorio += '\n' + '-'*103
        relatorio += f'\n{"Produto":40} | {"Quantidade Total Vencida":24}\n\n'
        for k, v in pdt_vencido.items():
            relatorio += f'{v[1]:40} | {v[0]:24}\n'

        relatorio += '\n' + '-'*103
        relatorio += f'\nQuantidade Total de Produtos Vencidos: {total_vencidos}'

        return EstoqueDal.gerar_relatorio_txt(relatorio)


    @staticmethod
    def adicionar_quantidade(id_categoria: int, id_produto: int, quantidade: list, codigo: json=None,
                            devolver_codigo: bool=True) -> json:
        if not codigo:
            codigo = EstoqueDal.ler_arquivo()

        index_categoria = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
        index_produto, produto = EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo, retorna_obj=False)

        for v in quantidade:
            for i, q in enumerate(codigo[index_categoria]['produtos'][index_produto]['quantidade']):
                if v[0] == q[0]:
                    codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][1] += v[1]
                    break
            else:
                codigo[index_categoria]['produtos'][index_produto]['quantidade'].append(v)

        # transforma todas as datas em objetos datetime e os ordena
        for i, q in enumerate(produto['quantidade']):
            d = datetime.datetime.strptime(q[0], '%d/%m/%Y')
            codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d

        codigo[index_categoria]['produtos'][index_produto]['quantidade'] = sorted(
            codigo[index_categoria]['produtos'][index_produto]['quantidade'],
            key=itemgetter(0))
        
        # transforma todos os objetos datetime em string para armazenar no banco de dados
        for i, q in enumerate(produto['quantidade']):
            d = datetime.datetime.strftime(q[0], '%d/%m/%Y')
            codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][0] = d

        if devolver_codigo:
            return codigo
        
        EstoqueDal.salvar_arquivo(codigo)
        return True


    @staticmethod
    def remover_quantidade(id_categoria: int, id_produto: int, quantidade: int, codigo: json) -> json:
        index_categoria = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
        index_produto, produto = EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo, False)

        if contar_quantidade(produto) < quantidade:
            raise ValueError('RAISE', 'Faltam produtos no estoque!')

        pop_list = []
        for i, q in enumerate(codigo[index_categoria]['produtos'][index_produto]['quantidade']):
            if q[1] > quantidade:
                codigo[index_categoria]['produtos'][index_produto]['quantidade'][i][1] -= quantidade
                break
            if q[1] == quantidade:
                pop_list.append(i)
                break
            if q[1] < quantidade:
                quantidade -= q[1]
                pop_list.append(i)
        
        pop_list.sort(reverse=True)
        for p in pop_list:
            codigo[index_categoria]['produtos'][index_produto]['quantidade'].pop(p)
        
        return codigo


    @staticmethod
    def listar_categorias() -> list:
        """
        Lista todas as categorias e retorna uma lista com os seus ids::

            '''
            ID  | Nome
            ------------------------------
            001 | Vencidos
            002 | Nenhuma
            003 | Frutas
            '''
            # return [0, 1, 5]

        ---

        Returns:
            list: Lista com os ids das categorias listadas em ordem
        """
        codigo = EstoqueDal.ler_arquivo()
        codigo.pop(0) # Remove a categoria 'vencidos'
        ids_categoria = []

        print(f'{"ID":3} | Nome')
        print('-'*32)
        for i, categoria in enumerate(codigo):

            print(f'{str(i+1).zfill(3)} | {categoria["categoria"].capitalize()}')
            ids_categoria.append(categoria['id'])
        print()
        
        return ids_categoria


    @staticmethod
    def listar_produtos(id_categoria: int) -> list:
        """
        Lista todos os produtos de uma categoria e retorna uma lista com os seus ids::

            '''
            Categoria: Frutas

            ID  | Nome                           | Marca                | Preço  | Quantidade
            -------------------------------------------------------------------------------------
            001 | Maça                           | Aurora               |   5.99 | 89
            002 | Banana Nanica Cacho            | Sadia                |   3.99 | 294
            '''
            # return [0, 1]

        ---

        Args:
            int: categoria da qual os produtos seráo listados
        Returns:
            list: Lista com os ids dos produtos listados em ordem
        """
        codigo = EstoqueDal.ler_arquivo()
        id_categoria = EstoqueDal.pesquisar_categoria(codigo, id_categoria)
        codigo = codigo[id_categoria]

        ids_produto = []

        print(f'Categoria: {codigo["categoria"].capitalize()}\n')
        print(f'{"ID":3} | {"Nome":40} | {"Marca":20} | {"Preço":6} | Quantidade')
        print('-'*100)
        for i, pdt in enumerate(codigo['produtos']):
            print(f'{str(i+1).zfill(3):<3} | {pdt["nome"]:40} | {pdt["marca"]:20} | {pdt["preco"]:6.2f} | {contar_quantidade(pdt)}')
            ids_produto.append(pdt['id'])
        print()

        return ids_produto


    @staticmethod
    def ver_produto(id_categoria: id, id_produto: int):
        codigo = EstoqueDal.ler_arquivo()
        codigo_categoria = CategoriaDal.ler_arquivo()
        codigo_fornecedor = FornecedorDal.ler_arquivo()

        _, pdt = EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo, False)
        categoria = codigo[CategoriaDal.pesquisar_arquivo('id', id_categoria, codigo_categoria)]['categoria']
        _, fornecedor = FornecedorDal.ler_fornecedor(codigo_fornecedor, pdt['id_fornecedor'], True)

        titulo('Dados do Produto', comprimento=50, justificar=True)
        print(
f'''Categoria: {categoria.capitalize()}
    Nome: {pdt["nome"]}
    Marca: {pdt["marca"]}
    Preço: R${pdt["preco"]}
    Fornecedor: {fornecedor.nome}''')

        titulo('Estoque', '-', comprimento=50, justificar=True)
        for q in pdt["quantidade"]:
            print(f'Quantidade: {q[1]}')
            print(f'Vence em: {q[0]}')
            print()
        print(f'Quantidade Total no Estoque: {contar_quantidade(pdt)}')
        print('='*50)


# --------------------------------------------------
# --------------------------------------------------


class FornecedorController:
    @staticmethod
    def cadastrar_fornecedor(nome: str, telefone: str, email: str, cnpj: str=None) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if cnpj != None:
            for f in codigo:
                if f['cnpj'] == cnpj:
                    raise ValueError('RAISE', 'Já existe um fornecedor cadastrado com este CNPJ!')

        if (not nome) or 5 > len(nome) > 50:
            raise ValueError('RAISE', 'Nome inválido!')
        if nome.isnumeric():
            raise TypeError('O nome não pode ser um número!')

        telefone = formatar_telefone(telefone)
        if not telefone:
            raise ValueError('RAISE', 'Telefone inválido!')

        if not email_valido(email):
            raise ValueError('RAISE', 'Email inválido!')

        if not cnpj_valido(cnpj):
            raise ValueError('RAISE', 'CNPJ inválido!')
        
        id = IdDal.gerar_id('id_fornecedor')
        fornecedor = Fornecedor(id, nome, telefone, email, cnpj)
        return FornecedorDal.cadastrar_fornecedor(fornecedor, codigo)
    

    @staticmethod
    def alterar_fornecedor(id_fornecedor, **kwargs) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID')
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError('RAISE', 'Nome inválido!')

        if kwargs.get('telefone') != None:
            kwargs['telefone'] = formatar_telefone(kwargs.get('telefone'))
            if not kwargs['telefone']:
                raise ValueError('RAISE', 'Telefone inválido!')

        if kwargs.get('email') != None:
            if not email_valido(kwargs.get('email')):
                raise ValueError('RAISE', 'Email inválido!')

        if kwargs.get('cnpj') != None:
            if not cnpj_valido(kwargs.get('cnpj')):
                raise ValueError('RAISE', 'CNPJ inválido!')
        
        return FornecedorDal.alterar_fornecedor(id_fornecedor, codigo, **kwargs)
    

    @staticmethod
    def remover_fornecedor(id_fornecedor: int) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)

        return FornecedorDal.remover_fornecedor(id_fornecedor, codigo)
    

    @staticmethod
    def listar_fornecedores() -> list:
        """
        Lista todos os fornecedores e retorna uma lista com os seus ids::

            '''
            ID  | Nome
            ------------------------------
            001 | Nenhum
            002 | Peixonauta
            '''
            # return [0, 3]

        ---

        Returns:
            list: Lista com os ids das fornecedores listados em ordem
        """
        
        codigo = FornecedorDal.ler_arquivo()

        ids_fornecedor = []

        print(f'{"ID":3} | Nome')
        print('-'*30)
        for i, fornecedor in enumerate(codigo):
            print(f'{str(i+1).zfill(3):<3} | {fornecedor["nome"].capitalize()}')
            ids_fornecedor.append(fornecedor['id'])
        print()

        return ids_fornecedor


    @staticmethod
    def ver_fornecedor(id_fornecedor: int):
        codigo = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_categoria = CategoriaDal.ler_arquivo()

        _, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor, True)

        titulo('Dados do Fornecedor', comprimento=50, justificar=True)
        print(
f'''Nome: {fornecedor.nome}
Telefone: {fornecedor.telefone}
Email: {fornecedor.email}
CNPJ: {fornecedor.cnpj}''')

        titulo('Lotes', comprimento=50, justificar=True)
        for lote in fornecedor.lotes:
            _, pdt = EstoqueDal.ler_produto_por_categoria(lote['id_categoria'], lote['id_produto'],
                                                        codigo_estoque, True)
            categoria = codigo_estoque[CategoriaDal.pesquisar_arquivo('id',
                        lote['id_categoria'], codigo_categoria)]['categoria']
            print(
f'''Produto:
    Categoria: {categoria.capitalize()}
    Nome: {pdt.nome}
    Marca: {pdt.marca}

Quantidade de Produto: {lote["quantidade"]}
Preço Lote: R${lote["preco_lote"]}

Intervalo de Cargas: {lote["tempo"]["intervalo"]}
Data Próxima Entrega: {lote["tempo"]["proximo"]}''')
            print('-'*50)
        print('='*50)


    @staticmethod
    def cadastrar_lote(id_fornecedor: int, preco_lote: float, id_categoria: int,
                       id_produto: id, quantidade: int, tempo: dict=None) -> bool:
        # Na view vai perguntar se o produto do lote já existe no sistema ou se ele quer criar um !!!

        codigo = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        
        if not EstoqueDal.ler_produto_por_categoria(id_categoria, id_produto, codigo_estoque):
            raise IdError('Não existe um produto com este ID', id_produto)

        if tempo != None:
            if not validar_tempo(tempo):
                raise ValueError('RAISE', 'Data inválida')

        
        id = IdDal.gerar_id('id_lote')
        lote = Lote(id, preco_lote, id_produto, id_categoria, quantidade, tempo)
        return FornecedorDal.cadastrar_lote(id_fornecedor, lote, codigo)
    
    
    @staticmethod
    def alterar_lote(id_fornecedor: int, id_lote: int, **kwargs) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        if not FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False):
            raise IdError('Não existe um lote com esse ID neste fornecedor!')
        
        if kwargs.get('id_categoria') != None:
            codigo_estoque = EstoqueDal.ler_arquivo()
            if not codigo_estoque:
                raise ServerError('Não foi possível acessar o banco de dados!')
            
            if not EstoqueDal.ler_produto_por_categoria(kwargs.get('id_categoria'), kwargs.get('id_produto'), codigo_estoque):
                raise IdError('Não existe um produto com este ID', kwargs.get('id_produto'))
        
        return FornecedorDal.alterar_lote(id_fornecedor, id_lote, codigo, **kwargs)


    @staticmethod
    def remover_lote(id_fornecedor: int, id_lote: int) -> bool:
        codigo = FornecedorDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID', id_fornecedor)
        if not FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote=id_lote, retorna_obj=False):
            raise IdError('Não existe um lote com esse ID neste fornecedor!')
        
        return FornecedorDal.remover_lote(id_fornecedor, id_lote, codigo)
    

    @staticmethod
    def lote_recebido(id_fornecedor: int, id_lote: int, quantidade: list) -> bool:
        codigo_fornecedor = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        if not FornecedorDal.ler_fornecedor(codigo_fornecedor, id_fornecedor):
            raise IdError('Não existe um fornecedor com este ID!')
        if not FornecedorDal.ler_lote(id_fornecedor, codigo_fornecedor, id_lote):
            raise IdError('Não existe um lote com esse ID!')
        
        try:
            data_hoje = datetime.datetime.now()
            for v in quantidade:
                d = datetime.datetime.strptime(v[0], '%d/%m/%Y')
                if d <= data_hoje:
                    raise ValueError('RAISE', 'Os produtos já estão vencidos')
        except:
            raise ValueError('RAISE', 'Quantidade inválida!')
        
        index_f, fornecedor = FornecedorDal.ler_fornecedor(codigo_fornecedor, id_fornecedor, False)
        index_l, lote = FornecedorDal.ler_lote(id_fornecedor, codigo_fornecedor, id_lote, False)

        codigo_fornecedor[index_f]['lotes'][index_l]['tempo'] = proximo_lote(lote['tempo'])
        codigo_estoque = EstoqueController.adicionar_quantidade(lote['id_categoria'], lote['id_produto'], quantidade, codigo_estoque)

        return FornecedorDal.lote_recebido(codigo_fornecedor, codigo_estoque)


    @staticmethod
    def listar_lotes(id_fornecedor: int) -> list:
        """
        Lista todos os lotes de um fornecedor e retorna uma lista com os seus ids::

            '''
            =====================================================================================
                                  Fornecedor: Peixonauta | QNT de Lotes: 1                             
            =====================================================================================
            ID  | Produto              | QNT Produto | Preço Lote | Prox. Lote
            -------------------------------------------------------------------------------------
            001 | Maça                 |          70 |    1500.00 | 07/09/2022
            '''
            # return [2]

        ---

        Args:
            int: id do fornecedor a qual serão listados os lotes
        Returns:
            list: Lista com os ids dos lotes listados em ordem
        """
        
        codigo = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        index_fornecedor, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor, False)

        ids_lote = []
        titulo(f'Fornecedor: {fornecedor["nome"]} | QNT de Lotes: {len(fornecedor["lotes"])}',
            comprimento=100, justificar=True)
        print(f'{"ID":3} | {"Produto":40} | {"QNT Produto":11} | {"Preço Lote":10} | {"Prox. Lote":10}')
        print('-'*100)
        for i, lote in enumerate(fornecedor['lotes']):
            i_categoria, i_produto, pdt = EstoqueDal.ler_produto_por_id(lote['id_produto'], codigo_estoque, False)

            print(f'{str(i+1).zfill(3):<3} | {pdt["nome"]:40} | {lote["quantidade"]:11} | {lote["preco_lote"]:10.2f} | {lote["tempo"]["proximo"]:10}')
            ids_lote.append(lote['id_lote'])
        print()

        return ids_lote


    @staticmethod
    def ver_lote(id_fornecedor: int, id_lote: int):
        codigo = FornecedorDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_categoria = CategoriaDal.ler_arquivo()

        _, fornecedor = FornecedorDal.ler_fornecedor(codigo, id_fornecedor, True)
        _, lote = FornecedorDal.ler_lote(id_fornecedor, codigo, id_lote, False)
        _, pdt = EstoqueDal.ler_produto_por_categoria(lote['id_categoria'], lote['id_produto'], codigo_estoque, True)
        categoria = codigo_estoque[CategoriaDal.pesquisar_arquivo('id', lote['id_categoria'], codigo_categoria)]['categoria']


        titulo(f'Lote do Fornecedor: {fornecedor.nome}', comprimento=50, justificar=True)
        print(
f'''Produto:
    Categoria: {categoria.capitalize()}
    Nome: {pdt.nome}
    Marca: {pdt.marca}

Quantidade de Produto: {lote["quantidade"]}
Preço Lote: R${lote["preco_lote"]}

Intervalo de Cargas: {lote["tempo"]["intervalo"]}
Data Próxima Entrega: {lote["tempo"]["proximo"]}''')
        print('='*50)


# --------------------------------------------------
# --------------------------------------------------


class FuncionarioController:
    @staticmethod
    def cadastrar_funcionario(nome: str, telefone: str, email: str, cpf: str,
                              cargo: str, senha: str, admin=False, posicao=None,
                              login_funcionario: LoginFuncionario=None) -> bool:
        codigo = FuncionarioDal.ler_arquivo()
        
        valida_senha = senha_valida(senha)
        if valida_senha != True:
            raise ValueError('RAISE', valida_senha)

        if admin:
            if posicao > login_funcionario.posicao:
                raise ValueError('RAISE', 'Não é possível cadastrar um ADM com a posição maior que a sua!')
            elif posicao <= 0:
                raise ValueError('RAISE', 'Não é possível cadastrar um posição menor que 1')
        
        if (not nome) or 5 > len(nome) > 50:
            raise ValueError('RAISE', 'Nome inválido!')
        if nome.isnumeric():
            raise TypeError('O nome não pode ser um número!')

        telefone = formatar_telefone(telefone, False)
        if not telefone:
            raise ValueError('RAISE', 'Telefone inválido!')

        if not email_valido(email):
            raise ValueError('RAISE', 'Email inválido!')
        
        for f in codigo['funcionarios']:
            if f['cpf'] == cpf:
                raise ValueError('RAISE', 'Já existe um funcionário cadastrado com este CPF!')
        for f in codigo['admins']:
            if f['cpf'] == cpf:
                raise ValueError('RAISE', 'Já existe um ADM cadastrado com este CPF!')

        if not cpf_valido(cpf):
            raise ValueError('RAISE', 'CPF inválido!')
        
        if admin:
            id = IdDal.gerar_id('id_admin')
        else:
            id = IdDal.gerar_id('id_funcionario')

        senha = hash_senha(senha, decode=True)
        funcionario = Funcionario(id, nome, cpf, cargo, senha, telefone, email)
        if admin:
            return FuncionarioDal.cadastrar_funcionario(funcionario, codigo, admin=True, posicao=posicao)
        else:
            return FuncionarioDal.cadastrar_funcionario(funcionario, codigo)


    @staticmethod
    def alterar_funcionario(id_funcionario: int, admin=False,
                            login_funcionario: LoginFuncionario=None, **kwargs) -> bool:
        codigo = FuncionarioDal.ler_arquivo()
        
        if admin:
            if kwargs.get('posicao') != None:
                if kwargs.get('posicao') > login_funcionario.posicao:
                    raise ValueError('RAISE', 'Não é possível alterar um ADM com a posição maior que a sua!')
                elif kwargs.get('posicao') <= 0:
                    raise ValueError('RAISE', 'Não é possível alterar uma posição menor que 1')

            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=True):
                raise IdError('Não existe um funcionário com este ID!')
        else:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario):
                raise IdError('Não existe um funcionário com este ID!')
        
        if kwargs.get('senha') != None:
            valida_senha = senha_valida(kwargs.get('senha'))
            if valida_senha != True:
                raise ValueError('RAISE', valida_senha)
            
            kwargs['senha'] = hash_senha(kwargs.get('senha'), decode=True)
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError('RAISE', False, 'Nome inválido!')

        if kwargs.get('telefone') != None:
            kwargs['telefone'] = formatar_telefone(kwargs.get('telefone'))
            if not kwargs['telefone']:
                raise ValueError('RAISE', False, 'Telefone inválido!')

        if kwargs.get('email') != None:
            if not email_valido(kwargs.get('email')):
                raise ValueError('RAISE', False, 'Email inválido!')

        if kwargs.get('cpf') != None:
            if not cpf_valido(kwargs.get('cpf')):
                raise ValueError('RAISE', False, 'CPF inválido!')
        
        if admin:
            return FuncionarioDal.alterar_funcionario(id_funcionario, codigo, admin=True, **kwargs)
        else:
            return FuncionarioDal.alterar_funcionario(id_funcionario, codigo, **kwargs)

    
    @staticmethod
    def remover_funcionario(id_funcionario: int, admin=False,
                            login_funcionario: LoginFuncionario=None) -> bool:
        codigo = FuncionarioDal.ler_arquivo()
        
        if admin:
            adm = FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin=True)
            if not adm:
                raise IdError('Não existe um ADM com este ID')
            if adm[1].posicao > login_funcionario.posicao:
                raise ValueError('RAISE', 'Não é possível remover um ADM com a posição maior que a sua!')
        else:
            if not FuncionarioDal.ler_funcionario(codigo, id_funcionario):
                raise IdError('Não existe um funcionário com este ID')
        
        if admin:
            return FuncionarioDal.remover_funcionario(id_funcionario, codigo, admin=True)
        else:
            return FuncionarioDal.remover_funcionario(id_funcionario, codigo)


    @staticmethod
    def listar_funcionarios(admin: bool=False) -> list:
        """
        Lista todos os funcionários do tipo selecionado, e retorna uma lista com seus ids na ordem
        em que foram listados::

            '''
            ID  | Nome
            ------------------------------
            001 | Mateus
            002 | Jubileu
            '''
            # return [0, 3]

        ---

        Args:
            admin (bool): Tipo de funcionário a ser listado. default=False
        Returns:
            list: Lista com os ids dos funcionários listados em ordem
        """
        codigo = FuncionarioDal.ler_arquivo()

        lista_ids = []
        codigo = codigo['admins'] if admin else codigo['funcionarios']

        print(f'{"ID":3} | Nome')
        print('-'*30)
        for i, func in enumerate(codigo):
            print(f'{str(i+1).zfill(3):<3} | {func["nome"]}')
            lista_ids.append(func['id'])
        print()

        return lista_ids


    @staticmethod
    def ver_funcionario(id_funcionario: int, admin: bool):
        codigo = FuncionarioDal.ler_arquivo()

        i, func = FuncionarioDal.ler_funcionario(codigo, id_funcionario, admin, True)
        
        titulo(f'Dados do Funcionário')
        print(
f'''Nome: {func.nome}
CPF: {func.cpf}
Telefone: {func.telefone}
Email: {func.email}
Cargo: {func.cargo}''')

        if admin:
            print(f'Posição: {func.posicao}')
        
        print('='*50)

# --------------------------------------------------
# --------------------------------------------------


class ClienteController:
    @staticmethod
    def cadastrar_cliente(nome: str, cpf: str, senha: str, telefone: str=None, email: str=None) -> bool:
        codigo = ClienteDal.ler_arquivo()
        
        valida_senha = senha_valida(senha)
        if valida_senha != True:
            raise ValueError('RAISE', valida_senha)
        
        if (not nome) or 5 > len(nome) > 50:
            raise ValueError('RAISE', 'Nome inválido!')
        if nome.isnumeric():
            raise TypeError('O nome não pode ser um número!')

        if telefone != None:
            telefone = formatar_telefone(telefone)
            if not telefone:
                raise ValueError('RAISE', 'Telefone inválido!')

        if email != None:
            if not email_valido(email):
                raise ValueError('RAISE', 'Email inválido!')

        for c in codigo:
            if c['cpf'] == cpf:
                raise ValueError('RAISE', 'Já existe um cliente cadastrado com este CPF!')

        if not cpf_valido(cpf):
            raise ValueError('RAISE', 'CPF inválido!')
        
        senha = hash_senha(senha, decode=True)
        
        id = IdDal.gerar_id('id_cliente')
        cliente = Cliente(nome, cpf, id, senha, telefone, email)
        return ClienteDal.cadastrar_cliente(cliente, codigo)


    @staticmethod
    def alterar_cliente(id_cliente: int, **kwargs) -> bool:
        codigo = ClienteDal.ler_arquivo()
        
        if not ClienteDal.ler_cliente(codigo, id_cliente):
            raise IdError('Não existe uma cliente com esse ID!')
        
        if kwargs.get('senha') != None:
            valida_senha = senha_valida(kwargs.get('senha'))
            if valida_senha != True:
                raise ValueError('RAISE', valida_senha)
            
            kwargs['senha'] = hash_senha(kwargs.get('senha'), decode=True)
        
        if kwargs.get('nome') != None:
            if (not kwargs.get('nome')) or 5 > len(kwargs.get('nome')) > 50:
                raise ValueError('RAISE', False, 'Nome inválido!')

        if kwargs.get('telefone') != None:
            kwargs['telefone'] = formatar_telefone(kwargs.get('telefone'))
            if not kwargs['telefone']:
                raise ValueError('RAISE', False, 'Telefone inválido!')

        if kwargs.get('email') != None:
            if not email_valido(kwargs.get('email')):
                raise ValueError('RAISE', False, 'Email inválido!')

        if kwargs.get('cpf') != None:
            if not cpf_valido(kwargs.get('cpf')):
                raise ValueError('RAISE', False, 'CPF inválido!')
        
        return ClienteDal.alterar_cliente(id_cliente, codigo, **kwargs)
    

    @staticmethod
    def remover_cliente(id_cliente: int) -> bool:
        codigo = ClienteDal.ler_arquivo()
        
        if not ClienteDal.ler_cliente(codigo, id_cliente):
            raise IdError('Não existe um cliente com este ID')
        
        return ClienteDal.remover_cliente(id_cliente, codigo)


# --------------------------------------------------
# --------------------------------------------------


class LoginController:
    @staticmethod
    def logar_funcionario(nome: str, senha: str, admin=False) -> LoginFuncionario:
        codigo = FuncionarioDal.ler_arquivo()

        if admin:
            for i, f in enumerate(codigo['admins']):
                if f['nome'] == nome:
                    senha_2 = f['senha'].encode('utf-8')
                    break
            else:
                raise ValueError('RAISE', 'Nao existe um ADM com este nome!')
        else:
            for i, f in enumerate(codigo['funcionarios']):
                if f['nome'] == nome:
                    senha_2 = f['senha'].encode('utf-8')
                    break
            else:
                raise ValueError('RAISE', 'Nao existe um funcionário com este nome!')
        
        senha = senha.encode('utf-8')
        if not comparar_senha(senha, senha_2):
            raise ValueError('RAISE', 'Senha incorreta!')
        
        if admin:
            return LoginFuncionario(f['id'], f['cpf'], f['nome'], admin, f['posicao'])
        return LoginFuncionario(f['id'], f['cpf'], f['nome'], admin, None)
    

    @staticmethod
    def logar_cliente(nome: str, senha: str) -> LoginCliente:
        codigo = ClienteDal.ler_arquivo()

        for i, c in enumerate(codigo):
            if c['nome'] == nome:
                senha_2 = c['senha'].encode('utf-8')
                break
        else:
            raise ValueError('RAISE', 'Não existe um usuário com este nome!')
        
        senha = senha.encode('utf-8')
        if not comparar_senha(senha, senha_2):
            raise ValueError('RAISE', 'Senha incorreta!')
        
        return LoginCliente(c['id'], c['cpf'], c['nome'], c['telefone'], c['email'])


# --------------------------------------------------
# --------------------------------------------------


class CaixaController:
    @staticmethod
    def cadastrar_caixa(numero_caixa: int, valor_no_caixa: float) -> bool:
        codigo = CaixaDal.ler_arquivo()

        if CaixaDal.ler_caixa(numero_caixa, codigo):
            raise ValueError('RAISE', 'Já existe um caixa com este número!')
        
        if valor_no_caixa < 0:
            raise ValueError('RAISE', 'O valor no caixa não pode ser negativo!')
        
        return CaixaDal.cadastrar_caixa(numero_caixa, valor_no_caixa, codigo)
    

    @staticmethod
    def alterar_caixa(numero_caixa: int, metodo: str=None, **kwargs) -> bool:
        """
        `metodo` pode receber duas strings:
            * 'saque'    | Remove o valor recebido do caixa
            * 'deposito' | Adiciona o valor recebido ao caixa
            * `None`       | Altera o valor do caixa para o valor recebido
        
        ---

        Args:
            numero_caixa (int): Número do caixa que será alterado
            metodo (str): Tipo de movimentação. default=None
            **kwargs: Valores alterados
        """
        codigo = CaixaDal.ler_arquivo()
        
        caixa = CaixaDal.ler_caixa(numero_caixa, codigo)
        if not caixa:
            raise ValueError('RAISE', 'Não existe um caixa com esse número!')
        
        if kwargs.get('numero_caixa') != None:
            if CaixaDal.ler_caixa(numero_caixa, codigo):
                raise ValueError('RAISE', 'Já existe um caixa com este número!')
        
        if kwargs.get('valor_no_caixa') != None:
            match metodo:
                case 'saque':
                    kwargs['valor_no_caixa'] = caixa[1]['valor_no_caixa'] - kwargs['valor_no_caixa']
                case 'deposito':
                    kwargs['valor_no_caixa'] += caixa[1]['valor_no_caixa']

            if kwargs.get('valor_no_caixa') < 0:
                raise ValueError('RAISE', 'O valor no caixa não pode ser negativo!')
        
        return CaixaDal.alterar_caixa(numero_caixa, codigo, **kwargs)


    @staticmethod
    def remover_caixa(numero_caixa: int) -> bool:
        codigo = CaixaDal.ler_arquivo()
        
        caixa = CaixaDal.ler_caixa(numero_caixa, codigo)
        if not caixa:
            raise IdError('Não existe uma caixa com esse número!')
        if caixa[1]['valor_no_caixa'] > 0:
            raise ValueError('RAISE', 'Você não pode remover um caixa com dinheiro dentro!')
        
        return CaixaDal.remover_caixa(numero_caixa, codigo)
    

    @staticmethod
    def definir_caixa(numero_caixa: int, login: LoginFuncionario, admin: False) -> LoginFuncionario:
        codigo_caixa = CaixaDal.ler_arquivo()
        codigo_funcionario = FuncionarioDal.ler_arquivo()
        
        if not CaixaDal.ler_caixa(numero_caixa, codigo_caixa):
            raise ValueError('RAISE', 'Não existe um caixa com esse número!')

        if admin:
            for i, f in enumerate(codigo_funcionario['admins']):
                if f['id'] == login.id_funcionario:
                    break
            else:
                raise ValueError('RAISE', 'Não existe um funcionário com este ID')
        else:
            for i, f in enumerate(codigo_funcionario['funcionarios']):
                if f['id'] == login.id_funcionario:
                    break
            else:
                raise ValueError('RAISE', 'Não existe um funcionário com este ID')
        
        
        index, caixa = CaixaDal.ler_caixa(numero_caixa, codigo_caixa)
        login.caixa = Caixa(caixa['numero_caixa'], caixa['valor_no_caixa'])
        return login


    @staticmethod
    def passar_produto(id_produto: int, quantidade: int) -> ProdutoNoCarrinho:
        codigo_caixa = CaixaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        produto = EstoqueDal.ler_produto_por_id(id_produto, codigo_estoque, retorna_obj=False)
        if not produto:
            raise IdError('Não existe um produto com este ID!')
        index_categoria, index_produto, produto = produto
        
        qnt = contar_quantidade(produto)
        if qnt < quantidade:
            raise ValueError('RAISE', 'Não temos está quantidade de produtos!')
        
        preco_total = quantidade * produto['preco']        
        return ProdutoNoCarrinho(codigo_estoque[index_categoria]['id'],
                                 codigo_estoque[index_categoria]['categoria'],
                                 produto['id'], produto['nome'], produto['marca'],
                                 quantidade, produto['preco'], preco_total)


    @staticmethod
    def listar_caixas(valor_no_caixa: bool=False) -> list:
        """
        Lista todos os caixas e retorna uma lista com os seus ids::

            '''
            ID  | Número do Caixa | Valor no Caixa (R$)
            ----------------------------------------
            001 |               1 | 819.30
            002 |               2 | 682.94
            003 |               3 | 95.89
            '''
            # return [0, 1, 5]

        ---
        Args:
            valor_no_caixa (bool): Exibe o dinheiro dentro do caixa
        Returns:
            list: Lista com os ids dos caixas listados em ordem
        """

        codigo = CaixaDal.ler_arquivo()
        numeros_caixa = []

        if valor_no_caixa:
            print(f'{"ID":3} | {"Caixa":10} | {"Valor no Caixa (R$)":19}')
        else:
            print(f'{"ID":3} | {"Caixa":10}')
        print('-'*50)
        for i, caixa in enumerate(codigo):
            if valor_no_caixa:
                print(f'{str(i+1).zfill(3)} | Caixa {caixa["numero_caixa"]:<10} | R${caixa["valor_no_caixa"]:.2f}')    
            else:
                print(f'{str(i+1).zfill(3)} | Caixa {caixa["numero_caixa"]:<10}')
            numeros_caixa.append(caixa['numero_caixa'])
        print()

        return numeros_caixa


    @staticmethod
    def dados_da_compra(carrinho: Carrinho):
        titulo('Dados da Compra', comprimento=100, justificar=True)
        print(f'{len(carrinho.produtos)} produto(s) no total:\n')
        
        print(f'{"Nome":40} | {"Marca":20} | {"Quantidade":10} | {"Preço Unitário":14} | {"Preço Total":14}')
        print('-'*100)
        for i, pdt in enumerate(carrinho.produtos):
            print(f'{pdt.nome_produto:40} | {pdt.marca:20} | {pdt.quantidade:<10} | R${pdt.preco_unidade:<12.2f} | R${pdt.preco_total:<12.2f}')
        print()
        print(f'Preço Total da Compra: R${carrinho.preco_total:.2f}')


# --------------------------------------------------
# --------------------------------------------------


class VendaController:
    @staticmethod
    def retirar_do_estoque(carrinho: Carrinho):
        codigo_estoque = EstoqueDal.ler_arquivo()
        
        for i, p in enumerate(carrinho.produtos):
            codigo_estoque = EstoqueController.remover_quantidade(p.id_categoria, p.id_produto, 
                                                                p.quantidade, codigo_estoque)
        
        EstoqueDal.salvar_arquivo(codigo_estoque)


    @staticmethod
    def venda(login: LoginFuncionario, numero_caixa: int, carrinho: Carrinho,
            valor_recebido: float, cpf_cliente=None) -> float:
        codigo_caixa = CaixaDal.ler_arquivo()
        codigo_venda = VendaDal.ler_arquivo()
        
        caixa = CaixaDal.ler_caixa(numero_caixa, codigo_caixa)
        if not caixa:
            raise ValueError('RAISE', 'Não existe um caixa com esse número!')
        index, caixa = caixa

        if cpf_cliente != None:
            if not cpf_valido(cpf_cliente):
                raise ValueError('RAISE', 'CPF inválido!')
        
        if valor_recebido < carrinho.preco_total:
            raise ValueError('RAISE', 'Dinheiro insuficiente!', carrinho.preco_total - valor_recebido)
        
        troco = valor_recebido - carrinho.preco_total
        if troco > caixa['valor_no_caixa']:
            raise ValueError('RAISE', 'Caixa sem troco de R$', troco - caixa['valor_no_caixa'])
        print('Não deveria ter passado daqui!')
        valor_no_caixa = caixa['valor_no_caixa'] + carrinho.preco_total
        CaixaDal.alterar_caixa(numero_caixa, codigo_caixa, valor_no_caixa=valor_no_caixa)

        produtos = []
        for i, p in enumerate(carrinho.produtos):
            produtos.append({
                'id_categoria':   p.id_categoria,
                'nome_categoria': p.nome_categoria,
                'id_produto':     p.id_produto,
                'nome_produto':   p.nome_produto,
                'marca':          p.marca,
                'quantidade':     p.quantidade,
                'preco_unidade':  p.preco_unidade,
                'preco_total':    p.preco_total
            })
        
        VendaController.retirar_do_estoque(carrinho)

        tipo_func = 'admins' if login.admin else 'funcionarios'

        id = IdDal.gerar_id('id_venda')
        data = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        venda = Venda(id, data, login.id_funcionario, tipo_func, produtos, carrinho.preco_total,
                      cpf_cliente, produtos)
        VendaDal.cadastrar_venda(venda, codigo_venda)
        return troco
    

    @staticmethod
    def venda_online(login: LoginCliente, carrinho: Carrinho, valor_recebido: float) -> float:
        codigo_venda = VendaDal.ler_arquivo()

        if valor_recebido < carrinho.preco_total:
            raise ValueError('RAISE', 'Dinheiro insuficiente!', carrinho.preco_total - valor_recebido)
        
        troco = valor_recebido - carrinho.preco_total
        
        produtos = []
        for i, p in enumerate(carrinho.produtos):
            produtos.append({
                'id_categoria':   p.id_categoria,
                'nome_categoria': p.nome_categoria,
                'id_produto':     p.id_produto,
                'nome_produto':   p.nome_produto,
                'quantidade':     p.quantidade,
                'preco_unidade':  p.preco_unidade,
                'preco_total':    p.preco_total
            })
        
        VendaController.retirar_do_estoque(carrinho)
        
        id = IdDal.gerar_id('id_venda')
        data = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        venda = VendaOnline(id, data, produtos, carrinho.preco_total,
                            login.id_cliente, login.cpf, carrinho.produtos)
        VendaDal.cadastrar_venda_online(venda, codigo_venda)
        return troco
    

    @staticmethod
    def gerar_relatorio_vendas(chave=None, datas: tuple=None, gerar_txt=False):
        """
        Gera um relatório das vendas, use o parâmetro `chave` para especificar o tipo de venda:
            * chave=None: relatório de todas as vendas
            * chave='fisica': relatório das vendas fisicas
            * chave='online': relatório das vendas online
        
        O parâmetro `datas` é opcional, caso passado ele deverá conter duas instâncias de
        `datetime.datetime`, que serão o intervalo das datas na qual será procurada a venda.
        Se nada for passado, ele irá pegar as vendas de todas as datas.
        
        ---

        Args:
            chave (str): pedir as vendas fisicas/online somente. default=None
            datas (tuple): 2 instâncias de datetime.datetime . default=None
            gerar_txt (bool): default=False
        Returns:
            gerar_txt=False: retorna o relatório em formato de str
            gerar_txt=True: None
        """
        codigo_venda = VendaDal.ler_arquivo()
        codigo_estoque = EstoqueDal.ler_arquivo()
        codigo_funcionario = FuncionarioDal.ler_arquivo()

        pdt, func, lucros = VendaDal.coletar_dados(codigo_venda, codigo_estoque.copy(),
                                                   codigo_funcionario, chave, datas)

        if datas:
            d1 = datetime.datetime.strftime(datas[0], '%d/%m/%Y')
            d2 = datetime.datetime.strftime(datas[1], '%d/%m/%Y') 
            titulo = f'Relatório das Vendas entre {d1} e {d2}:\n\n{"="*100}\n\n'
        else:
            titulo = f'Relatório das Vendas:\n\n{"="*100}\n\n'

        relatorio = ''
        relatorio += titulo
        relatorio += 'Produtos Vendidos:\n'

        for k, v in pdt.items():
            # caso a categoria não tiver nenhuma venda, pula para próxima
            if not v:
                relatorio += f'\n    Nenhuma venda na Categoria: {k.capitalize()}\n\n'
                continue

            relatorio += f'\n{"-"*50}\n'
            relatorio += f'\n    Categoria: {k.capitalize()}\n\n'
            relatorio += f'{"ID":4} | {"Nome":40} | {"Marca":20} | {"Unidades Vendidas":17}\n\n'
            for key, value in v.items():
                index_categoria, index_produto, p = EstoqueDal.ler_produto_por_id(int(key), codigo_estoque)
                
                relatorio += f'{str(p.id).zfill(4)} | {p.nome:40} | {p.marca:20} | {value:17}\n'
            
        relatorio += f'\n\n{"="*100}\n\n'
        relatorio += 'Funcionários que Mais Venderam:\n'

        for k, v in func.items():
            relatorio += f'\n{"-"*50}\n'
            relatorio += f'\n    {k.capitalize()}:\n\n'
            for key, value in v.items():
                index, f = FuncionarioDal.ler_funcionario(
                    codigo_funcionario, int(key),
                    admin=True if k == 'admins' else False, retorna_obj=True
                    )
                
                relatorio += f'{"ID":4} | {"Nome":50} | {"Vendas":6}\n\n'
                relatorio += f'{str(f.id).zfill(4)} | {f.nome:50} | {str(value).zfill(6):6}\n'
        
        relatorio += f'\n\n{"="*100}\n\n'
        relatorio += 'Lucros:\n'

        for k, v in lucros.items():
            relatorio += f'\n{"-"*50}\n'
            relatorio += f'\n    Lucro da Loja {k.split("_")[2].capitalize()}:\n\n'
            relatorio += f'    R${v:.2f}\n'

        return VendaDal.gerar_relatorio_txt(relatorio) if gerar_txt else relatorio


    @staticmethod
    def listar_vendas(tipo_venda: str, datas: tuple=None) -> list:
        """
        Lista todas as vendas de um tipo, entre as datas passadas e retorna uma lista com os seus ids::

            '''
            ======================================================================================
                                            Todas as Vendas Físicas
            ======================================================================================
            ID  | Data Venda          | CPF Cliente    | Nome Funcionário | Valor da Venda
            --------------------------------------------------------------------------------------
            001 | 31/08/2022 00:00:00 | Sem CPF        | Einsten          |         319.30
            001 | 11/09/2022 00:00:00 | 49046554007    | Mateus           |         428.95
            '''
            # return [2]

        ---

        Args:
            tuple: uma tupla com duas instâncias datetime entre um intervalo de tempo. default=None
        Returns:
            list: Lista com os ids das vendas listadas em ordem
        """
        
        codigo = VendaDal.ler_arquivo()
        codigo_funcionario = FuncionarioDal.ler_arquivo()
        codigo_cliente = ClienteDal.ler_arquivo()
        ids_venda_fisica = []
        ids_venda_online = []

        if tipo_venda == 'fisica':
            if datas:
                titulo(f'Vendas Físicas entre {datetime.datetime.strftime(datas[0], "%d/%m/%Y")} e '
                       f'{datetime.datetime.strftime(datas[1], "%d/%m/%Y")}',
                       comprimento=120, justificar=True)
            else:
                titulo('Todas as Vendas Físicas', comprimento=120, justificar=True)
            print(f'{"ID":3} | {"Data Venda":19} | {"CPF Cliente":14} | {"Nome Funcionário":50} |',
            f'{"Valor da Venda":14}')
            print('-'*120)
            for i, venda in enumerate(codigo['fisica']):
                admin = True if venda['tipo_funcionario'] == 'admins' else False
                _, func = FuncionarioDal.ler_funcionario(codigo_funcionario, venda['id_funcionario'],
                admin, True)

                if datas:
                    data_venda = datetime.datetime.strptime(venda['data'], '%d/%m/%Y %H:%M:%S')
                    if not datas[0] <= data_venda <= datas[1]:
                        continue
                
                cpf_cliente = venda["cpf_cliente"] if venda["cpf_cliente"] else "Sem CPF"
                print(f'{str(i+1).zfill(3)} | {venda["data"]:19} | {cpf_cliente:14} |',
                f'{func.nome:50} | {venda["preco_total"]:14.2f}')
                ids_venda_fisica.append(venda['id_venda'])
            print()
        
        elif tipo_venda == 'online':
            if datas:
                titulo(f'Vendas Online entre {datetime.datetime.strftime(datas[0], "%d/%m/%Y")} e '
                       f'{datetime.datetime.strftime(datas[1], "%d/%m/%Y")}',
                       comprimento=120, justificar=True)
            else:
                titulo('Todas as Vendas Online', comprimento=120, justificar=True)
            print(f'{"ID":3} | {"Data Venda":19} | {"CPF Cliente":14} | {"Nome Cliente":50} |',
            f'{"Valor da Venda":14}')
            print('-'*100)
            for i, venda in enumerate(codigo['online']):
                index, cliente = ClienteDal.ler_cliente(codigo_cliente, venda['id_cliente'], True)


                data_venda = datetime.datetime.strptime(venda['data'], '%d/%m/%Y %H:%M:%S')
                if datas:
                    if not datas[0] <= data_venda <= datas[1]:
                        continue
                print(f'{str(i+1).zfill(3)} | {venda["data"]:19} | {venda["cpf_cliente"]:14} |',
                f'{cliente.nome:50} | {venda["preco_total"]:14.2f}')
                ids_venda_online.append(venda['id_venda'])
            print()

        return ids_venda_fisica if tipo_venda == 'fisica' else ids_venda_online


    @staticmethod
    def ver_venda_fisica(id_venda: int):
        codigo = VendaDal.ler_arquivo()
        codigo_funcionario = FuncionarioDal.ler_arquivo()

        i, venda = VendaDal.ler_venda(id_venda, codigo, False, True)

        admin = True if venda.tipo_funcionario == 'admins' else False
        i, func = FuncionarioDal.ler_funcionario(codigo_funcionario, venda.id_funcionario, admin, True)

        cpf_cliente = venda.cpf_cliente if venda.cpf_cliente else "CPF Não Informado"
        
        titulo(f'Venda Física realizada em: {venda.data}')
        print(f'Funcionário: {func.nome}')
        print(f'CPF cliente: {cpf_cliente}')

        titulo(f'Produtos | {len(venda.produtos_dict)} Produtos ao Total', '-', 100, justificar=True)
        for i, pdt in enumerate(venda.produtos_dict):
            print(f"""Categoria: {pdt["nome_categoria"].capitalize()}
    Produto: {pdt["nome_produto"]}
    Marca: {pdt["marca"]}
    Unidades Vendidas: {pdt["quantidade"]}
    Preço Unidade: R${pdt["preco_unidade"]:.2f}
    Preço Total: R${pdt["preco_total"]:.2f}""")
            print('-'*100)

        print(f'Preço Total da Compra: R${venda.preco_total}')
        print('='*100)
    

    @staticmethod
    def ver_venda_online(id_venda: int):
        codigo = VendaDal.ler_arquivo()
        codigo_funcionario = FuncionarioDal.ler_arquivo()
        codigo_cliente = ClienteDal.ler_arquivo()

        i, venda = VendaDal.ler_venda(id_venda, codigo, True, True)
        i, cliente = ClienteDal.ler_cliente(codigo_cliente, venda.id_cliente, True)
        
        titulo(f'Venda Online realizada em: {venda.data}')
        print(f'Cliente: {cliente.nome}')
        print(f'CPF cliente: {cliente.cpf}')

        titulo(f'Produtos | {len(venda.produtos_dict)} Produtos ao Total', '-', 100, justificar=True)
        for i, pdt in enumerate(venda.produtos_dict):
            print(f"""Categoria: {pdt["nome_categoria"].capitalize()}
    Produto: {pdt["nome_produto"]}
    Marca: {pdt["marca"]}
    Unidades Vendidas: {pdt["quantidade"]}
    Preço Unidade: R${pdt["preco_unidade"]:.2f}
    Preço Total: R${pdt["preco_total"]:.2f}""")
            print('-'*100)

        print(f'Preço Total da Compra: R${venda.preco_total}')
        print('='*100)


# --------------------------------------------------
# --------------------------------------------------
