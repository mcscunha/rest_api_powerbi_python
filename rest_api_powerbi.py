'''
# Sugiro colocar estes dados em outro arquivo para que nao
# seja visivel a todos que olharem o codigo Python

parametros = {
    # Nao alterar estes dois parametros
    'grant_type': 'password', 
    'resource': 'https://analysis.windows.net/powerbi/api',
    
    # Alterar somente estes parametros abaixo
    'tenant_id': 'SEU_TENANT_ID', 
    'tenant_str': 'TENANT_EM_STRING', # teste.onmicrosoft.com'
    'client_id' : 'APPLICATION_ID', 
    'client_secret': 'APPLICATION_SECRET', 
    'username': 'USUARIO_POWERBI', 
    'password': 'SENHA_POWERBI', 
    }
'''


import json
import requests
import random
from datetime import date, timedelta
import config


# Variaveis de configuracao
tenant_str = config.parametros['tenant_str']
pontos_extremidade = f'https://login.microsoftonline.com/{tenant_str}/oauth2/token'
tenant_id = config.parametros['tenant_id']
grant_type = config.parametros['grant_type']
client_id = config.parametros['client_id']
client_secret = config.parametros['client_secret']
username = config.parametros['username']
password = config.parametros['password']
resource = config.parametros['resource']
token = ''


def obterToken():
    '''
        Obter o token para trabalhar com PowerBI
    '''
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = {
        'client_id': client_id,
        'grant_type': grant_type,
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
        'resource': resource
        }
    req = requests.post(url=pontos_extremidade, headers=header, data=body)
    req_json = json.loads(req.text)
    print(req_json['access_token'], '\n')
    return req_json['access_token']


def criarDataset():
    '''
        Criar dataset no workspace principal
    '''
    url_api = 'https://api.powerbi.com/v1.0/myorg/datasets'
    header = {'Content-Type': 'application/json',
              'Authorization': f'Bearer {token}'
              }
    body = '''
        {
        "name": "PesquisaSapatos",
        "defaultMode": "Push",
        "tables": [
            {
            "name": "Sapatos",
            "columns": [
                {
                "name": "Tamanho",
                "dataType": "Int64"
                },
                {
                "name": "Marca",
                "dataType": "string"
                },
                {
                "name": "Disponivel",
                "dataType": "bool"
                },
                {
                "name": "DataCadastro",
                "dataType": "DateTime"
                }
            ]
            }
        ]
        }'''
    req_dts = requests.post(url=url_api, headers=header, data=body)
    if req_dts.status_code != 201:
        print('Criacao do dataset COM ERRO', req_dts.text)
    else:
        print('Criacao do dataset COM SUCESSO!\n', 
            json.dumps(req_dts.text, indent=4), '\n'
            )


def listarDatasets():
    '''
        Exibir o ID do dataset procurado
    '''
    url_api = 'https://api.powerbi.com/v1.0/myorg/datasets'
    header = {'Content-Type': 'application/json',
              'Authorization': f'Bearer {token}'
              }
    req_ldts = requests.get(url=url_api, headers=header)
    j_req_ldts = json.loads(req_ldts.text)
    j_req_ldts_value = j_req_ldts['value']
    datasets = {}
    for i in j_req_ldts_value:
        datasets[i['name']] = i['id']
    id = datasets.get('PesquisaSapatos', '** NOME NAO ENCONTRADO **')
    print('ID do dataset criado agora:', id)
    return id


def inserirRegistro(id, tabela):
    '''
        Insere registro na tabela criada para push
    '''
    header = {'Content-Type': 'application/json',
              'Authorization': f'Bearer {token}'
              }
    url_api = f'https://api.powerbi.com/v1.0/myorg/datasets/{id}/tables/{tabela}/rows'

    # items = [1, 2, 3, 4, 5, 6, 7]
    # random.shuffle(items) # embaralha os itens aleatoriamente    
    nome_marcas = ['SAMELO', 'FERRACINI', 'JOTA_PE', 'CNS']
    random.seed()                               #inicia a semente dos número pseudo randômicos
    for i in range(0, 5):
        diferenca_dias = random.randrange(0, 90)
        data_atual = date.today() - timedelta(days=diferenca_dias)
        tama = random.randrange(12, 46, 2)      # Pares entre 12 e 46
        marc = random.choice(nome_marcas)       # seleciona um dos elementos aleatoriamente
        disp = random.choice(('True', 'False')) # escolher na tupla
        data = data_atual.strftime('%m/%d/%Y')  # deve ser nessa ordem a data
        dado = {
            'Tamanho': tama,
            'Marca': marc,
            'Disponivel': disp,
            'DataCadastro': data
            }
        body = "{'rows': [" + str(dado) + "]}"
        req = requests.post(url=url_api, headers=header, data=body)
        #print(req.status_code, '\n', req.text, '\n')
        print('Dado inserido: ', i, ' - ', body)


def limparDataset(id, tabela):
    '''
        Apaga todos os registros do dataset
    '''
    header = {'Content-Type': 'application/json',
              'Authorization': f'Bearer {token}'
              }
    url_api = f'https://api.powerbi.com/v1.0/myorg/datasets/{id}/tables/{tabela}/rows'
    req = requests.delete(url=url_api, headers=header)
    print(req.status_code, '\n', req.text, '\n')


def apagarDataset(id):
    '''
        Apaga o dataset
    '''
    header = {'Content-Type': 'application/json',
              'Authorization': f'Bearer {token}'
              }
    url_api = f'https://api.powerbi.com/v1.0/myorg/datasets/{id}'
    req = requests.delete(url=url_api, headers=header)
    print(req.status_code, '\n', req.text, '\n')


if __name__ == '__main__':
    # Pegar o token de acesso ao PowerBI Rest API
    token = obterToken()
    
    # Criar um dataset de push de dados
    criarDataset()

    # Pegar o ID do dataset criado
    dataset_id = listarDatasets()
    
    # Insere 5 registros aleatorios
    #
    # ATENCAO:
    #
    #   Os comandos de insercao para a API do PowerBI devem ser guardados em
    # um arquivo TXT para possivel reinsercao, pois a API nao tem recurso
    # de listar os registros contidos no dataset, entao, se precisar limpar
    # o dataset e reinserir os dados estes dados serao os comando guardados
    # no arquivo TXT.
    #
    inserirRegistro(dataset_id, 'Sapatos')

    # Editar registro inserido
    #
    # ATENCAO
    #
    # Hoje nao é possivel fazer isso
    # Implementacao desta ideia no banco de ideias da MS
    # https://ideas.powerbi.com/forums/265200-power-bi-ideas/suggestions/9366600-update-rows-rest-api
    #
    # Uma ideia que poderia ser feito para contornar este problema é
    # inserir um registro com valor negativo, assim, na contabilizacao
    # o registro a ser alterado, seria modificado pela nova insercao

    # Limpar a tabela toda
    limparDataset(dataset_id, 'Sapatos')

    # Apagar o dataset
    apagarDataset(dataset_id)
