# cria os modelos do banco de dados


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
