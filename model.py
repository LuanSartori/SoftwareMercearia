# cria os modelos do banco de dados


class Categoria:
    def __init__(self, categoria: str, id_categoria: int):
        self.categoria = categoria
        self.id = id_categoria


class Produto:
    def __init__(self, id: int, id_categoria: int, nome: str, marca: str, preco: float, id_fornecedor: int=None):
        self.id = id
        self.id_categoria = id_categoria
        self.nome = nome
        self.marca = marca
        self.preco = preco
        self.id_fornecedor = id_fornecedor


class Estoque:
    def __init__(self, produto: Produto, quantidade: int):
        self.produto = produto
        self.quantidade = quantidade