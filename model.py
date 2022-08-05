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
    def __init__(self, id: int, nome: str, telefone: str = None, email: str = None, cnpj: str=None):
        super().__init__(nome, telefone=telefone, email=email)
        self.id = id
        self.cnpj = cnpj


class Lote():
    def __init__(self, id_lote: int, preco_lote: float, id_produto: int, quantidade: int, tempo: list=None):
        self.id_lote = id_lote
        self.preco_lote = preco_lote
        self.id_produto = id_produto
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


class Venda:
    def __init__(self, id_venda: int, id_cliente: int, id_produto: int, quantidade: int, preco_unitario: float):
        self.id_venda = id_venda
        self.id_cliente = id_cliente
        self.id_produto = id_produto
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.preco_total = preco_unitario * quantidade
