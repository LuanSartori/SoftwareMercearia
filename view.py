# sistema do telefone
'''codigo_pais = str(input('Código do País: +')).strip()
estado = '(' + str(input('Estado: ()')).strip() + ')'
numero = str(input('Número: ')).strip()

telefone = codigo_pais + estado + numero

try:
    FornecedorController.cadastrar('Fernado', telefone, 'hey@gmail.com', '999999999')
except AttributeError:
    print('Número inválido!')'''


# para formatar um telefone:
'''padrao = "([0-9]{2,3}) ?(\([0-9]{2}\))([0-9]{4,5})([0-9]{4})"
telefone = re.search(padrao, telefone)
numero_formatado = "+{} {}{}-{}".format(telefone.group(1),telefone.group(2),
                                        telefone.group(3), telefone.group(4))'''

# para formatar um cpf
# '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])


# para formatar um cnpj
# "{}.{}.{}/{}-{}".format(cnpj[0:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:14])
