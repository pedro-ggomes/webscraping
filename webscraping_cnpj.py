from selectolax.parser import HTMLParser
from curl_cffi import requests
import unicodedata
import re
# import pprint

def main(cnpj:str):
    
    def strip_accents(text:str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                    if unicodedata.category(c) != 'Mn')

    def normalize_string(text:str) -> str:
        text = text.replace(' ','_').replace('-','').lower()
        text = strip_accents(text)
        return text

    def email(text:str) -> str:
        r = int(text[:2], 16)
        email = ''.join([chr(int(text[i:i+2], 16) ^ r)
                        for i in range(2, len(text), 2)])
        return email

    def telefone(text:str) -> str:
        pattern = r'\(\d{2}\)\s\d{4,5}-\d{4}'
        return re.findall(pattern,text)

    def fix_cnpj(text:str) -> str:
        pattern = r'\d+'
        return ''.join(re.findall(pattern,text))

    estados_e_siglas = {
        "Acre": "AC",
        "Alagoas": "AL",
        "Amapá": "AP",
        "Amazonas": "AM",
        "Bahia": "BA",
        "Ceará": "CE",
        "Distrito Federal": "DF",
        "Espírito Santo": "ES",
        "Goiás": "GO",
        "Maranhão": "MA",
        "Mato Grosso": "MT",
        "Mato Grosso do Sul": "MS",
        "Minas Gerais": "MG",
        "Pará": "PA",
        "Paraíba": "PB",
        "Paraná": "PR",
        "Pernambuco": "PE",
        "Piauí": "PI",
        "Rio de Janeiro": "RJ",
        "Rio Grande do Norte": "RN",
        "Rio Grande do Sul": "RS",
        "Rondônia": "RO",
        "Roraima": "RR",
        "Santa Catarina": "SC",
        "São Paulo": "SP",
        "Sergipe": "SE",
        "Tocantins": "TO"
    }  

    cnpj = fix_cnpj(cnpj)

    url = f"https://cnpj.biz/{cnpj}"

    resp = requests.get(url,impersonate='chrome110')

    html = HTMLParser(resp.text)
    try:
        itens = html.css_first('body > div.container > div > div > div > div.column-1.box').css('p')
        sobre = html.css_first('body > div.container > div > div > div > div.column-1.box > p:nth-child(39)').text()
    except Exception as e:
        print(e)
        final_dict = {'cnpj':cnpj,'msg':'Não encontrado'}
        exit()

    final_dict = {}

    for item in itens:
        try:
            key, value = item.text().split(": ")
            key = normalize_string(key)
            if key == 'email':
                value = email(item.css_first('a').attributes['data-cfemail'])
            if key == 'telefone(s)':
                key = 'tel'
                value = telefone(value)
            final_dict[normalize_string(key)] = value
        except ValueError:
            continue

    final_dict['sobre'] = sobre.strip()
    final_dict['sigla_estado'] = estados_e_siglas[final_dict['estado']]

    keys = ['cnpj',
    'razao_social',
    'data_da_abertura',
    'nome_fantasia',
    'porte',
    'natureza_juridica',
    'situacao',
    'tel',
    'logradouro',
    'bairro',
    'cep',
    'municipio',
    'estado',
    'sigla_estado',
    'sobre']

    for key in final_dict.keys():
        if key not in keys:
            final_dict[key] = ''

    final_dict = {key: final_dict[key] for key in keys}

    return final_dict

if __name__ == "__main__":
    result = main('cnpj que quer consultar aqui')
    print(result)