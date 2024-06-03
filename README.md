# Criando um Cluster MongoDB utilizando conteiners no Docker

Nesse projeto vou exemplicar um projeto de implantação de um banco de dados documental escalável e distribuido, com o objetivo de aplicar os conhecimentos adquiridos nas aulas de Banco de Dados NoSQL do curso de Engenharia de Dados da PUC Minas, ministrado pelo (excelente) professor [Anderson Theobaldo](https://www.linkedin.com/in/atheobaldo/)

# 🚀 Começando

## [Cenário]

Vamos criar um cluster para atender às necessidades de uma cadeia de supermercados, com foco em escalabilidade e eficiência. Nosso cliente planeja expandir para novas cidades em breve, aumentando rapidamente o número de filiais.

Cada filial possui um grande volume de produtos em seu estoque. O sistema precisa ser capaz de lidar com milhões de registros de produtos, garantindo que as consultas de estoque e as atualizações de inventário sejam rápidas e eficientes. A escalabilidade do sistema é essencial, pois nosso cliente tem planos de expansão e vai abrir novas filiais em um futuro breve.

## [Arquitetura da Solução]
Baseando-se no artigo [artigo](https://gustavo-leitao.medium.com/criando-um-cluster-mongodb-com-replicaset-e-sharding-com-docker-9cb19d456b56) de Gustavo Leitão, vamos criar um cluster de MongoDB em Docker. Para isso, utilizaremos três tipos de serviços: Roteador, Servidor de Configuração e Shards, que serão responsáveis pelas partições.

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/57086f13-4918-478e-87b4-9a6b0afe37a6)


No caso do nosso cliente já existem 4 filiais

_______

## [Construindo a Solução]

Todos os comandos abaixo devem ser executados diretamente no prompt do comando do seu computador. no meu caso, estou usando Windows

## 🔧 Criando a Rede

```
docker network create supermercados-gigios
```

Para deletar uma rede Criada, utilize o comando
```
docker network rm supermercados-gigios
```
## 🔧 Criando os ConfigServers
```
docker run --name m-c01 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
```
```
docker run --name m-c02 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
```
```
docker run --name m-c03 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
```
```
docker run --name m-c04 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
```
## 🔧 Configurando os ConfigServers

```
docker exec -it m-c01 mongosh
```

```
rs.initiate(
   {
      _id: "configserver",
      configsvr: true,
      version: 1,
      members: [
         { _id: 0, host : "m-c01:27017" },
         { _id: 1, host : "m-c02:27017" },
         { _id: 2, host : "m-c03:27017" },
         { _id: 3, host : "m-c04:27017" }
      ]
   }
)
```

## 🔧 Criando os Shards

shard001

```
docker run --name mongo-sd001a --net supermercados-gigios -d mongo mongod --port 27018 --shardsvr --replSet shard001
```
```
docker run --name mongo-sd001b --net supermercados-gigios -d mongo mongod --port 27018 --shardsvr --replSet shard001
```
```
docker run --name mongo-sd001c --net supermercados-gigios -d mongo mongod --port 27018 --shardsvr --replSet shard001
```
shard002
```
docker run --name mongo-sd002a --net supermercados-gigios -d mongo mongod --port 27019 --shardsvr --replSet shard002
```
```
docker run --name mongo-sd002b --net supermercados-gigios -d mongo mongod --port 27019 --shardsvr --replSet shard002
```
```
docker run --name mongo-sd002c --net supermercados-gigios -d mongo mongod --port 27019 --shardsvr --replSet shard002
```
shard003
```
docker run --name mongo-sd003a --net supermercados-gigios -d mongo mongod --port 27020 --shardsvr --replSet shard003
```
```
docker run --name mongo-sd003b --net supermercados-gigios -d mongo mongod --port 27020 --shardsvr --replSet shard003
```
```
docker run --name mongo-sd003c --net supermercados-gigios -d mongo mongod --port 27020 --shardsvr --replSet shard003
```
shard004
```
docker run --name mongo-sd004a --net supermercados-gigios -d mongo mongod --port 27021 --shardsvr --replSet shard004
```
```
docker run --name mongo-sd004b --net supermercados-gigios -d mongo mongod --port 27021 --shardsvr --replSet shard004
```
```
docker run --name mongo-sd004c --net supermercados-gigios -d mongo mongod --port 27021 --shardsvr --replSet shard004
```

## 🔧 Configurando os shards - procedimento precisa ser feito para todos os shards individualmente.

```
docker exec -it mongo-sd001a mongosh --port 27018
```
```
rs.initiate(
   {
      _id: "shard001",
      version: 1,
      members: [
         { _id: 0, host : "mongo-sd001a:27018" },
         { _id: 1, host : "mongo-sd001b:27018" },
         { _id: 3, host : "mongo-sd001c:27018" },
      ]
   }
)
```

```
docker exec -it mongo-sd002a mongosh --port 27019
```
```
rs.initiate(
   {
      _id: "shard002",
      version: 1,
      members: [
         { _id: 0, host : "mongo-sd002a:27019" },
         { _id: 1, host : "mongo-sd002b:27019" },
         { _id: 2, host : "mongo-sd002c:27019" },
      ]
   }
)
```

```
docker exec -it mongo-sd003a mongosh --port 27020
```
```
rs.initiate(
   {
      _id: "shard003",
      version: 1,
      members: [
         { _id: 0, host : "mongo-sd003a:27020" },
         { _id: 1, host : "mongo-sd003b:27020" },
         { _id: 2, host : "mongo-sd003c:27020" },
      ]
   }
)
```

```
docker exec -it mongo-sd004a mongosh --port 27021
```
```
rs.initiate(
   {
      _id: "shard004",
      version: 1,
      members: [
         { _id: 0, host : "mongo-sd004a:27021" },
         { _id: 1, host : "mongo-sd004b:27021" },
         { _id: 2, host : "mongo-sd004c:27021" },
      ]
   }
)
```

## 🔧 Criando o Roteador

```
docker run -p 27017:27017 --name mongo-rt --net supermercados-gigios -d mongo mongos --port 27017 --configdb configserver/m-c01:27017,m-c02:27017,m-c03:27017,m-c04:27017 --bind_ip_all
```

checando se tudo está ok


```
docker ps
```

se tudo estiver certo, veremos a seguinte tela
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/82cd1486-be87-44ed-bdd1-12eb3638c249)



## 🔧 Configurando o roteador - execute cada linha separadamente.

```
docker exec -it mongo-rt mongosh
```
```
sh.addShard("shard001/mongo-sd001a:27018")
sh.addShard("shard001/mongo-sd001b:27018")
sh.addShard("shard001/mongo-sd001c:27018")
```
```
sh.addShard("shard002/mongo-sd002a:27019")
sh.addShard("shard002/mongo-sd002b:27019")
sh.addShard("shard002/mongo-sd002c:27019")
```
```
sh.addShard("shard003/mongo-sd003a:27020")
sh.addShard("shard003/mongo-sd003b:27020")
sh.addShard("shard003/mongo-sd003c:27020")
```
```
sh.addShard("shard004/mongo-sd004a:27021")
sh.addShard("shard004/mongo-sd004b:27021")
sh.addShard("shard004/mongo-sd004c:27021")
```

para conferir

```
sh.status()
```
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/20304f8e-3345-453c-a399-be2121430fee)



Após a criação do cluster, podemo utilizar o MongoCompass para acessar o ambiente. é interessante observar as coleções do database Config:

nossos Shards Criados

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/33aa0f1f-297a-4036-af60-9063a807b287)


# 📦 Montando a Aplicação e os bancos

Com tudo configurado, chegou a hora de criarmos a aplicação que vai realizar operações em nosso banco de dados. para isso, criei um script Python que faz:

1 - Conexão ao Banco de Dados: Conecta-se ao banco de dados MongoDB onde os dados de estoque são armazenados.
2 - Geração de Pedidos: Gera movimentaçoes de entrada e saída de produtos para cada filial.
3 - Atualização do Estoque: Registra os pedidos no sistema e atualiza automaticamente o estoque disponível.
4 - Cálculo do Estoque Atual: Calcula o estoque atualizado após a execução dos pedidos para cada filial.

Essencialmente, o script automatiza o controle de estoque, garantindo que as operações de entrada e saida sejam registradas corretamente e refletidas no estoque disponível em cada filial.

Os campos inseridos em nossas transações são esses:
        '_id'
        'item_id'
        'data_operacao'
        'quantidade'
        'tipo_operacao'
        'preco_unitario'
        'valor_total'
        'fornecedor'
        'codigo_fornecedor'
        'codigo_categoria'
        'nome_categoria'
        'marca'
        'codigo_local'
        'nome_local'
        'data_validade'
        'lote'

o Script:

```
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
           'filial_004',
           'filial_005', 
           'filial_006', 
           'filial_007', 
           'filial_008',
           'filial_009', 
           'filial_010'
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

numero_operacoes = 500  # Número de documentos a serem inseridos por filial

# Loop para processar cada filial
for filial in filiais: 
    db_origem = client[filial]
    movimentacao_collection = db_origem.movimentacao
    estoque_collection = db_origem.estoque

    for _ in range(numero_operacoes):
        insert_order_documents(movimentacao_collection, estoque_collection)  # Inserir documentos

    stock = calculate_stock(movimentacao_collection)  # Calcular estoque
    print(f"Estoque calculado para {filial}: {stock}")
```


# 📦 Monitorando e extraindo métricas

Para extrair metricas, vamos utilizar a extensão do docker chamada [ContainerWath](https://hub.docker.com/extensions/containerwatch/containerwatch#!)

Para instalar, vamos nas estensões do Docker e instalar. simples assim.
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/9489be50-8b7e-4dc7-81e4-e1ad4b355295)


