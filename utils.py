from itertools import cycle
import re


def telefone_valido(telefone):
    try:
        padrao = "([0-9]{2,3})?(\([0-9]{2}\))([0-9]{4,5})([0-9]{4})"
        resposta = re.search(padrao, telefone)
        numero_formatado = "+{} {}{}-{}".format(
                    resposta.group(1),resposta.group(2),
                    resposta.group(3), resposta.group(4))
        return numero_formatado
    except:
        return False


def email_valido(email):
    valida = re.compile(r'^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$')
    return valida.match(email)


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