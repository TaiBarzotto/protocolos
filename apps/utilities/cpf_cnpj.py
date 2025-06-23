def tratar_cpnj_cpf_ug(cpf_cnpj):
    tam = len(cpf_cnpj)
    if tam == 14:
        # É cnpj
        tipo_pessoa = 'J'
        cpf_cnpj_formatado = f'{cpf_cnpj[:2]}.{cpf_cnpj[2:5]}.{cpf_cnpj[5:8]}/{cpf_cnpj[8:12]}-{cpf_cnpj[12:]}'
    elif tam == 11:
        tipo_pessoa = 'F'
        cpf_cnpj_formatado = f'{cpf_cnpj[:3]}.{cpf_cnpj[3:6]}.{cpf_cnpj[6:9]}-{cpf_cnpj[9:]}'
        # É cpf
    elif tam == 6:
        tipo_pessoa = 'G'
        cpf_cnpj_formatado = f'{cpf_cnpj[:6]}'
        # É UG
    else:
        tipo_pessoa = 'Invalida'
        cpf_cnpj_formatado = ''
        # É invalido
    return tipo_pessoa, cpf_cnpj_formatado