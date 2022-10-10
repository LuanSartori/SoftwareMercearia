import sys
sys.path.insert(0, '../SoftwareMercearia')

from model import *
from utils import *
from controller import *
from dal import *


gerar_banco(BANCO)

CategoriaController.cadastrar_categoria('frutas')
codigo_categoria = CategoriaDal.ler_arquivo()
id = CategoriaDal.pesquisar_arquivo('categoria', 'frutas', codigo_categoria, retorna_id=True)
EstoqueController.cadastrar_produto(id, 'Maça', 'Aurora', 5.99, [['31/08/2025', 50], ['14/09/2025', 15]], 0)
EstoqueController.cadastrar_produto(id, 'Banana Nanica Cacho', 'Sadia', 3.99, [['31/08/2025', 5], ['14/09/2025', 500]], 0)


# ------------------------------


login = LoginFuncionario(0, 'xxxx', 'Luca', True, 5)
FuncionarioController.cadastrar_funcionario('Mateus', '55 19912345678', 'mateuzin@gmail.com',
                                            '412.221.560-91', 'Chefe', 'Chefe1234', True, 5, login)
FuncionarioController.cadastrar_funcionario('Einsten', '55 19987460180', 'genio@gmail.com',
                                            '173.610.770-48', 'Gerente Auxiliar', 'Genio1234')


# ------------------------------


FornecedorController.cadastrar_fornecedor('Peixonauta', '55 21999999999', 'peixe_pop@gmail.com', '83.924.169/0001-65')
FornecedorController.cadastrar_lote(1, 1_500, 2, 0, 70, {"intervalo": 7, "proximo": "31/08/2022"})

FornecedorController.lote_recebido(1, 0, [['31/08/2025', 50], ['14/09/2025', 20]])


# ------------------------------


CaixaController.cadastrar_caixa(1, 500.0)
CaixaController.cadastrar_caixa(2, 250.0)
CaixaController.cadastrar_caixa(3, 50.0)


# ------------------------------


ClienteController.cadastrar_cliente('Marquinhos', '490.465.540-07', 'Marquinhos1234',
                                    '55 25887654321', 'marcos_antonio@gmail.com')
ClienteController.cadastrar_cliente('Luquinhas', '692.954.800-66', 'Luquinhas1234',
                                    '55 19985673916', 'lucas_sereio@gmail.com')
ClienteController.cadastrar_cliente('Stanford', '442.738.640-70', '4321drofnatS',
                                    '1 19000000000', 'escritor_dos_diarios@gmail.com')


# ------------------------------


login_funcionario = LoginController.logar_funcionario('Einsten', 'Genio1234', False)
login_cliente = LoginController.logar_cliente('Stanford', '4321drofnatS')

CaixaController.definir_caixa(1, login_funcionario, False)


# ------------------------------


carrinho = Carrinho([], 0)

produtos = []
produtos.append(CaixaController.passar_produto(0, 15))
produtos.append(CaixaController.passar_produto(1, 50))
produtos.append(CaixaController.passar_produto(0, 5))

for p in produtos:
    carrinho.produtos.append(p)
carrinho.preco_total = preco_total(carrinho.produtos)

print(VendaController.venda(login_funcionario, 1, carrinho, 347.55, None))
print(VendaController.venda_online(login_cliente, carrinho, 332.50))

VendaController.gerar_relatorio_vendas(None, None, False)


# ------------------------------
