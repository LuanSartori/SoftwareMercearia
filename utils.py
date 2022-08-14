from itertools import cycle
import re
import datetime
import bcrypt


class IdError(Exception):
    def __init__(self, *objects):
        pass


class ServerError(Exception):
    def __init__(self, *objects):
        pass


# --------------------------------------------------
# --------------------------------------------------


def formatar_telefone(telefone: str, country_code=False):
    """

    Recebe um telefone nos formatos:
    * country_code=True:  55 00999999999
    * country_code=False: 00999999999

    ---

    Args:
        telefone (str): número de telefone
        country_code (bool): True para incluir country code. default=False
    Returns:
        str: Número de telefone formatado para: +55 (00)99999-9999
        bool: False se o número for inválido
    """

    try:
        if country_code:
            padrao = "([0-9]{2,3}) ?([0-9]{2})([0-9]{4,5})([0-9]{4})"
            resposta = re.search(padrao, telefone)
            numero_formatado = "+{} ({}){}-{}".format(resposta.group(1),resposta.group(2),
                                                    resposta.group(3), resposta.group(4))
        else:
            padrao = "([0-9]{2})([0-9]{4,5})([0-9]{4})"
            resposta = re.search(padrao, telefone)
            numero_formatado = "+55 ({}){}-{}".format(resposta.group(1), resposta.group(2), resposta.group(3))
        return numero_formatado
    except:
        return False


def email_valido(email: str) -> bool:
    """
    Recebe e valida um email

    Args:
        email (str): string
    Returns:
        True para um email válido. False para inválido
    """

    valida = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
    return False if not valida.match(email) else True


def cpf_valido(cpf: str) -> bool:
    """
    Recebe um cpf nos formatos:
        * `xxx.xxx.xxx-xx`
        * `xxxxxxxxxxx`

    ---

    Args:
        cpf (str): string
    Returns:
        True para um cpf válido. False para inválido
    """

    cpf = cpf.replace('.', '')
    cpf = cpf.replace('-', '')

    TAMANHO_CPF = 11
    if len(cpf) != TAMANHO_CPF:
        return False

    if cpf in (c * TAMANHO_CPF for c in "1234567890"):
        return False

    cpf_reverso = cpf[::-1]
    for i in range(2, 0, -1):
        cpf_enumerado = enumerate(cpf_reverso[i:], start=2)
        dv_calculado = sum(map(lambda x: int(x[1]) * x[0], cpf_enumerado)) * 10 % 11
        if cpf_reverso[i - 1:i] != str(dv_calculado % 10):
            return False

    return True


def cnpj_valido(cnpj: str) -> bool:
    """
    Recebe um cnpj nos formatos:
        * `xx.xxx.xxx/xxxx-xx`
        * `xxxxxxxxxxxxxx`

    ---

    Args:
        cnpj (str): string
    Returns:
        True para um cnpj válido. False para inválido
    """

    LENGTH_CNPJ = 14
    
    cnpj = ''.join(re.findall('\d', str(cnpj)))
    if len(cnpj) != LENGTH_CNPJ:
        return False

    if cnpj in (c * LENGTH_CNPJ for c in "1234567890"):
        return False

    cnpj_r = cnpj[::-1]
    for i in range(2, 0, -1):
        cnpj_enum = zip(cycle(range(2, 10)), cnpj_r[i:])
        dv = sum(map(lambda x: int(x[1]) * x[0], cnpj_enum)) * 10 % 11
        if cnpj_r[i - 1:i] != str(dv % 10):
            return False

    return True


def senha_valida(senha: str) -> bool:
    """
    Recebe uma senha e verifica se:
        * A senha deve tem entre 8 e 20 caracteres;
        * A senha deve tem pelo menos uma letra maiúscula e minúscula;
        * A senha deve tem pelo menos um número;
        * A senha não tem espaços vazios
    
    ---

    Args:
        senha (str): string
    Returns:
        True: se a senha passar pelas verificações
        str: motivo do erro caso ela não passe
    """

    if len(senha) < 8 or len(senha) > 20:
        return 'A senha deve ter entre 8 e 20 caracteres!'
    elif not re.search('[a-z]', senha) or not re.search('[A-Z]', senha):
        return 'A senha deve ter pelo pelo menos uma letra maiúscula e minúscula!'
    elif not re.search('[0-9]', senha):
        return 'A senha deve ter pelo menos um número!'
    elif re.search('\s', senha):
        return 'A senha não deve ter espaços vazios!'
    else:
        return True


def hash_senha(senha: str, decode=False) -> str: 
    """
    Dê um hash na senha recebida e retorne ela
    
    ---

    Args:
        senha (str): string
        decode (bool): a senha deve retornar descodificada. default=False
    Returns:
        decode=False: senha codificada em `utf-8`
        decode=True: senha descodificada
    """

    pwd_bytes = senha.encode("utf-8") 
    salt = bcrypt.gensalt()
    senha = bcrypt.hashpw(pwd_bytes, salt)
    return senha.decode('utf-8') if decode else senha


def comparar_senha(senha_1: str, senha_2: str) -> bool:
    """
    Recebe duas senhas e verifica se são iguais
    
    ---

    Args:
        senha_1 (str): string codificada em `utf-8`
        senha_2 (str): senha em hash codificada em `utf-8`
    Returns:
        True se as duas senhas forem iguais, senão False
    """
    return bcrypt.checkpw(senha_1, senha_2)


def validar_tempo(tempo: dict) -> bool:
    """
    Valida os valores do dicionário, verifica o valor da chave `intervalo` e a data da chave `proximo`

    Recebe um dicionário no formato::
    
        {
            "intervalo": 7,
            "proximo": "19/08/2022"
        }
    
    ---

    Args:
        tempo (dict): dicionário com um intervalo e data
    Returns:
        True se o dicionário for válido, senão False
    Raises:
        ValueError: se o valor da chave `intervalo` for menor que 1
    """
    try:
        if not int(tempo['intervalo']) > 0:
            raise ValueError('O intervalo não pode ser menor que 1')
        datetime.datetime.strptime(tempo['proximo'], '%d/%m/%Y')
        return True
    except:
        return False


def proximo_lote(tempo: dict) -> dict:
    """
    Recebe um dicionário `tempo` e calcula a próxima data da chave `proximo` de acordo com o valor da chave `intervalo`

    Recebe um dicionário no formato::
    
        {
            "intervalo": 7,
            "proximo": "19/08/2022"
        }
    
    ---

    Args:
        tempo (dict): dicionário com um intervalo e data
    Returns:
        tempo(dict) com o valor da chave `proximo` alterado
    Raises:
        ValueError: se o valor de intervalo for menor que 1
    """
    proximo = datetime.datetime.strptime(tempo['proximo'], '%d/%m/%Y')
    proximo += datetime.timedelta(days=int(tempo['intervalo']))

    proximo = datetime.datetime.strftime(proximo, '%d/%m/%Y')
    tempo['proximo'] = proximo
    return tempo


def contar_quantidade(produto: dict) -> int:
    """
    Recebe um dicionário `produto` e retorna a soma dos valores na chave `quantidade`

    O dicionário deve estar no formato::

        {
            "id": 0,
            "id_categoria": 0,
            "nome": "nome do produto",
            "marca": "marca do produto",
            "preco": 0.00,
            "quantidade": [
                [
                    "00/00/0000",
                    0
                ],
                [
                    "00/00/0000",
                    0
                ]
            ],
            "id_fornecedor": 0
        }
    
    ---

    Args:
        produto (dict): uma instância de `Produto` em forma de dicionário
    Returns:
        int da soma das quantidades
    """
    quantidade = 0
    for q in produto['quantidade']:
        quantidade += q[1]
    
    return quantidade


def preco_total(*produtos) -> float:
    """
    Recebe x instâncias de `ProdutoNoCarrinho` e retorna a soma dos preços
    
    ---

    Args:
        *produtos: Instâncias de `ProdutoNoCarrinho`
    Returns:
        int do preço total de todos os produtos
    """
    preco_total = 0
    for i, p in enumerate(produtos):
        preco_total += p.preco_total
    
    return preco_total
