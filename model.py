class Categoria:
    def __init__(self, categoria: str, id: int):
        self.categoria = categoria
        self.id = id


class Produto:
    def __init__(self, id: int, id_categoria: int, nome: str, marca: str, preco: float, quantidade: list=[], id_fornecedor: int=None):
        self.id = id
        self.id_categoria = id_categoria
        self.nome = nome
        self.marca = marca
        self.preco = preco
        self.quantidade = quantidade
        self.id_fornecedor = id_fornecedor


class Pessoa:
    def __init__(self, nome: str, cpf: str=None, telefone: str=None, email: str=None):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email


class Fornecedor(Pessoa):
    def __init__(self, id: int, nome: str, telefone: str = None, email: str = None, cnpj: str=None, lotes: list=[]):
        super().__init__(nome, telefone=telefone, email=email)
        self.id = id
        self.cnpj = cnpj
        self.lotes = lotes



class Lote():
    def __init__(self, id_lote: int, preco_lote: float, id_produto: int, id_categoria: int, quantidade: int, tempo: dict):
        self.id_lote = id_lote
        self.preco_lote = preco_lote
        self.id_produto = id_produto
        self.id_categoria = id_categoria
        self.quantidade = quantidade
        self.tempo = tempo


class Funcionario(Pessoa):
    def __init__(self, id: int, nome: str, cpf: str, cargo: str, senha: str, telefone: str = None, email: str = None):
        super().__init__(nome, cpf, telefone, email)
        self.id = id
        self.cargo = cargo
        self.senha = senha


class Cliente(Pessoa):
    def __init__(self, nome: str, cpf: str, id: int, senha: str, telefone: str = None, email: str = None):
        super().__init__(nome, cpf, telefone, email)
        self.id = id
        self.senha = senha
        self.carrinho = []


class LoginFuncionario:
    def __init__(self, id_funcionario: int, cpf: str, nome: str, admin=False, posicao=None):
        self.id_funcionario = id_funcionario
        self.cpf = cpf
        self.nome = nome
        self.admin = admin
        self.posicao = posicao


class LoginCliente:
    def __init__(self, id_cliente: int, cpf: str, nome: str, telefone: str = None, email: str = None):
        self.id_cliente = id_cliente
        self.cpf = cpf
        self.nome = nome
        self.telefone = telefone
        self.email = email


class Caixa:
    def __init__(self, numero_caixa: int, valor_no_caixa: float, id_funcionario: int, nome_funcionario: str):
        self.numero_caixa = numero_caixa
        self.valor_no_caixa = valor_no_caixa
        self.id_funcionario = id_funcionario
        self.nome_funcionario = nome_funcionario


class ProdutoNoCarrinho:
    def __init__(self, id_categoria: int, nome_categoria, id_produto: int, nome_produto: str,
                 quantidade: int, preco_unidade: float, preco_total: float):
        self.id_categoria = id_categoria
        self.nome_categoria = nome_categoria
        self.id_produto = id_produto
        self.nome_produto = nome_produto
        self.quantidade = quantidade
        self.preco_unidade = preco_unidade
        self.preco_total = preco_total


class Carrinho:
    def __init__(self, produtos: list, preco_total: float):
        self.produtos = produtos
        self.preco_total = preco_total


class Venda:
    def __init__(self, id_venda: int, data: str, id_funcionario: int, tipo_funcionario: str,
                 carrinho: Carrinho, cpf_cliente: str=None, lista_produtos :list=None):
        self.id_venda = id_venda
        self.data = data
        self.id_funcionario = id_funcionario
        self.tipo_funcionario = tipo_funcionario
        self.produtos = carrinho.produtos
        self.preco_total = carrinho.preco_total
        self.cpf_cliente = cpf_cliente

        # opcional: lista dos produtos (para armazenamento em json)
        self.lista_produtos = lista_produtos


class VendaOnline:
    def __init__(self, id_venda: int, data: str, carrinho: Carrinho, id_cliente: int,
                 cpf_cliente: str, lista_produtos: list=None):
        self.id_venda = id_venda
        self.data = data
        self.produtos = carrinho.produtos
        self.preco_total = carrinho.preco_total
        self.id_cliente = id_cliente
        self.cpf_cliente = cpf_cliente

        # opcional: lista dos produtos (para armazenamento em json)
        self.lista_produtos = lista_produtos