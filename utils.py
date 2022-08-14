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


def telefone_valido(telefone):
    try:
        padrao = "([0-9]{2,3}) ?(\([0-9]{2}\))([0-9]{4,5})([0-9]{4})"
        resposta = re.search(padrao, telefone)
        numero_formatado = "+{} {}{}-{}".format(resposta.group(1),resposta.group(2),
                                                resposta.group(3), resposta.group(4))
        return numero_formatado
    except:
        return False


def email_valido(email):
    valida = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
    return valida.match(email)


def cpf_valido(cpf: str) -> bool:
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


def senha_valida(senha: str):
    if len(senha) < 8 or len(senha) > 20:
        return (False, 'A senha deve ter entre 8 e 20 caracteres!')
    elif not re.search('[a-z]', senha) or not re.search('[A-Z]', senha):
        return (False, 'A senha deve conter pelo pelo menos uma letrar maiúscula e minúscula!')
    elif not re.search('[0-9]', senha):
        return (False, 'A senha deve ter pelo menos um número!')
    elif re.search('\s', senha):
        return (False, 'A senha não deve ter espaços vazios!')
    else:
        return True


def hash_senha(senha: str, decode=False): 
    pwd_bytes = senha.encode("utf-8") 
    salt = bcrypt.gensalt()
    if decode:
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8') 
    return bcrypt.hashpw(pwd_bytes, salt)


def comparar_senha(senha_1: str, senha_2: str) -> bool:
    return bcrypt.checkpw(senha_1, senha_2)


def validar_tempo(tempo: dict):
    try:
        if not int(tempo['intervalo']) > 0:
            raise ValueError()
        datetime.datetime.strptime(tempo['proximo'], '%d/%m/%Y')
        return True
    except:
        return False


def proximo_lote(tempo: dict):
    proximo = datetime.datetime.strptime(tempo['proximo'], '%d/%m/%Y')
    proximo += datetime.timedelta(days=int(tempo['intervalo']))

    proximo = datetime.datetime.strftime(proximo, '%d/%m/%Y')
    tempo['proximo'] = proximo
    return tempo


def contar_quantidade(produto: dict) -> int:
    quantidade = 0
    for q in produto['quantidade']:
        quantidade += q[1]
    
    return quantidade


def preco_total(*produtos) -> float:
    preco_total = 0
    for i, p in enumerate(produtos):
        preco_total += p.preco_total
    
    return preco_total
