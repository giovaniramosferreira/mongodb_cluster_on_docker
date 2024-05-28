
from pymongo import MongoClient

# Configurações de conexão com o MongoDB
HOST = 'localhost'    # Altere para o endereço do seu servidor MongoDB, se necessário
PORT = 27017          # Porta padrão do MongoDB

# Função para conectar ao MongoDB
def connect_to_mongodb(host, port):
    client = MongoClient(host, port)
    return client

# Função para listar todos os bancos de dados
def list_databases(client):
    return client.list_database_names()

# Função para filtrar os bancos de dados que contêm "filial" no nome
def filter_filiais_databases(databases):
    return [db for db in databases if 'filial' in db]

# Função para excluir os bancos de dados
def drop_databases(client, databases):
    for db_name in databases:
        client.drop_database(db_name)
        print(f"Banco de dados {db_name} excluído com sucesso.")

# Conectar ao MongoDB
client = connect_to_mongodb(HOST, PORT)

# Listar todos os bancos de dados
all_databases = list_databases(client)

# Filtrar os bancos de dados que contêm "filial" no nome
filiais_databases = filter_filiais_databases(all_databases)

# Excluir os bancos de dados filtrados
drop_databases(client, filiais_databases)

# Fechar a conexão com o MongoDB
client.close()
