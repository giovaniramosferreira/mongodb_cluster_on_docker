from pymongo import MongoClient
from datetime import datetime
from faker import Faker
import random

# Configurações de conexão com o MongoDB
HOST = 'localhost'    # Altere para o endereço do roteador MongoDB, se necessário
PORT = 27017          # Porta padrão do MongoDB

# Lista de filiais
filiais = ['filial_001', 
           'filial_002', 
           'filial_003', 
           'filial_004'
           ]

# Função para conectar ao MongoDB
def connect_to_mongodb(host, port):
    client = MongoClient(host, port)
    return client

# Função para obter o ID máximo existente na coleção de movimentação
def get_max_id(collection):
    result = collection.find_one(sort=[('_id', -1)])
    if result:
        return result['_id']
    else:
        return 0

def calculate_stock(movimentacao_collection):
    pipeline = [
        {
            '$group': {
                '_id': '$item_id',
                'total_entrada': {
                    '$sum': {
                        '$cond': [{'$eq': ['$tipo_operacao', 'entrada']}, '$quantidade', 0]
                    }
                },
                'total_saida': {
                    '$sum': {
                        '$cond': [{'$eq': ['$tipo_operacao', 'saida']}, '$quantidade', 0]
                    }
                }
            }
        },
        {
            '$project': {
                'item_id': '$_id',
                '_id': 0,
                'estoque_atual': {'$subtract': ['$total_entrada', '$total_saida']}
            }
        }
    ]

    result = list(movimentacao_collection.aggregate(pipeline))
    return result

# Função para verificar se há estoque suficiente para uma saída
def has_sufficient_stock(estoque_collection, item_id, quantidade):
    item = estoque_collection.find_one({'item_id': item_id})
    item_stock = item['estoque_atual'] if item else 0
    return item_stock >= quantidade

# Função para inserir documentos de pedidos realizados
def insert_order_documents(movimentacao_collection, estoque_collection):
    fake = Faker()
    max_id = get_max_id(movimentacao_collection)
    order_id = max_id + 1
    item_id = fake.random_int(min=1, max=10)
    quantidade = fake.random_int(min=1, max=100)
    tipo_operacao = random.choice(['entrada', 'saida'])

    # Verificar se a operação de saída é possível
    if tipo_operacao == 'saida' and not has_sufficient_stock(estoque_collection, item_id, quantidade):
        #print(f"Estoque insuficiente para item_id {item_id}. Saída não registrada.")
        return  # Não registra a operação de saída se o estoque for insuficiente

    order = {
        '_id': order_id,  # ID sequencial
        'id' :random.randint(0, 999999999), # campo shardeado hashkey 
        'item_id': item_id,  
        'data_operacao': datetime.now(),  
        'quantidade': quantidade,  
        'tipo_operacao': tipo_operacao,
        'preco_unitario': fake.random_int(min=1, max=100),  # Preço unitário do item
        'valor_total': quantidade * fake.random_int(min=1, max=100),  # Valor total da operação
        'fornecedor': fake.company(),  # Nome do fornecedor
        'codigo_fornecedor': fake.random_int(min=1, max=1000),  # Código do fornecedor
        'codigo_categoria': fake.random_int(min=1, max=10),  # Código da categoria do item
        'nome_categoria': fake.word(),  # Nome da categoria do item
        'marca': fake.company_suffix(),  # Marca do item
        'codigo_local': fake.random_int(min=1, max=100),  # Código do local de armazenamento
        'nome_local': fake.word(),  # Nome do local de armazenamento
        'data_validade': fake.date_time_between(start_date='+1d', end_date='+2y'),  # Data de validade do item
        'lote': fake.random_int(min=1000, max=9999)  # Número do lote do item
    }
    movimentacao_collection.insert_one(order)
    print("Documento de pedido inserido:", order_id)

    # Atualizar a coleção de estoque
    if tipo_operacao == 'entrada':
        estoque_collection.update_one(
            {'item_id': item_id},
            {'$inc': {'estoque_atual': quantidade}},
            upsert=True  # Cria o documento se não existir
        )
    else:  # tipo_operacao == 'saida'
        estoque_collection.update_one(
            {'item_id': item_id},
            {'$inc': {'estoque_atual': -quantidade}}
        )

# Conectar ao MongoDB
client = connect_to_mongodb(HOST, PORT)

numero_operacoes = 1000  # Número de documentos a serem inseridos por filial

# Loop para processar cada filial
for filial in filiais: 
    db_origem = client[filial]
    movimentacao_collection = db_origem.movimentacao
    estoque_collection = db_origem.estoque

    for _ in range(numero_operacoes):
        insert_order_documents(movimentacao_collection, estoque_collection)  # Inserir documentos

    stock = calculate_stock(movimentacao_collection)  # Calcular estoque
    print(f"Estoque calculado para {filial}: {stock}")
