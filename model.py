class Categoria:
    def __init__(self, categoria: str, id: int):
        self.categoria = categoria
        self.id = id


class Produto:
    def __init__(self, id: int, id_categoria: int, nome: str, marca: str, preco: float, quantidade: int=None, id_fornecedor: int=None):
        self.id = id
        self.id_categoria = id_categoria
        self.nome = nome
        self.marca = marca
        self.preco = preco
        self.quantidade = quantidade
        self.id_fornecedor = id_fornecedor


class Cliente:
    def __init__(self, nome: str, cpf: str=None, telefone: str=None, email: str=None):
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email


class Fornecedor(Cliente):
    def __init__(self, id: int, nome: str, telefone: str = None, email: str = None, cnpj: str=None):
        super().__init__(nome, telefone=telefone, email=email)
        self.id = id
        self.cnpj = cnpj
