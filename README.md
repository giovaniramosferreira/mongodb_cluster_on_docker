# mongodb_cluster_on_docker

Criando um cluster de MongoDB utilizando Docker para criar um ambiente distribuido, escalável e tolerante a particionamento.

Utilizando como referencia o arquigo de gustavo leitão (https://gustavo-leitao.medium.com/criando-um-cluster-mongodb-com-replicaset-e-sharding-com-docker-9cb19d456b56) vamos criar um cluster ligeiramente diferente, prevendo a escalabilidade pois o Supermercado tem planos de expanção para novas cidades, com crescente numero de filiais.


para tal, utilzaremos tres tipos de serviços, Roteador, Servidor de Configuração e os Shards que ficarão responsáveis pelas partições.

(DESENHO)



Todos os comandos abaixo devem ser executados diretamente no prompt do comando do seu computador. no meu caso, estou usando Windows

#Criando a Rede

$ docker network create supermercados-gigios


#Criando os ConfigServers

$ docker run --name m-c01 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
$ docker run --name m-c02 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
$ docker run --name m-c03 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017

#Configurando os ConfigServers

$ docker exec -it m-c01 mongosh

rs.initiate(
   {
      _id: "configserver",
      configsvr: true,
      version: 1,
      members: [
         { _id: 0, host : "m-c01:27017" },
         { _id: 1, host : "m-c02:27017" },
         { _id: 2, host : "m-c03:27017" }
      ]
   }
)


#Criando os Shards

$ docker run --name mongo-sd001a --net supermercados-gigios -d mongo mongod --port 27018 --shardsvr --replSet shard001
$ docker run --name mongo-sd001b --net supermercados-gigios -d mongo mongod --port 27018 --shardsvr --replSet shard001


$ docker run --name mongo-sd002a --net supermercados-gigios -d mongo mongod --port 27019 --shardsvr --replSet shard002
$ docker run --name mongo-sd002b --net supermercados-gigios -d mongo mongod --port 27019 --shardsvr --replSet shard002


$ docker run --name mongo-sd003a --net supermercados-gigios -d mongo mongod --port 27020 --shardsvr --replSet shard003
$ docker run --name mongo-sd003b --net supermercados-gigios -d mongo mongod --port 27020 --shardsvr --replSet shard003


#configurando os shards - procedimento precisa ser feito para todos os shards individualmente.

$ docker exec -it mongo-sd001a mongosh --port 27018

rs.initiate(
   {
      _id: "shard001",
      version: 1,
      members: [
         { _id: 0, host : "mongo-sd001a:27018" },
         { _id: 1, host : "mongo-sd001b:27018" },
      ]
   }
)

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/666e1536-28ec-4014-97dd-706a03921762)


$ docker exec -it mongo-sd002a mongosh --port 27019

rs.initiate(
   {
      _id: "shard002",
      version: 1,
      members: [
         { _id: 0, host : "mongo-sd002a:27019" },
         { _id: 1, host : "mongo-sd002b:27019" },
      ]
   }
)

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/5120ef50-6d91-4222-93b7-bbfe0e8111b9)


$ docker exec -it mongo-sd003a mongosh --port 27020

rs.initiate(
   {
      _id: "shard003",
      version: 1,
      members: [
         { _id: 0, host : "mongo-sd003a:27020" },
         { _id: 1, host : "mongo-sd003b:27020" },
      ]
   }
)

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/056387b9-fca9-448b-8546-960fd18c298f)

Criando o Roteador

$ docker run -p 27017:27017 --name mongo-rt --net supermercados-gigios -d mongo mongos --port 27017 --configdb configserver/m-c01:27017,m-c02:27017,m-c03:27017 --bind_ip_all

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/4f82339b-44e8-4551-bb47-bf5fc67a649c)


checando se tudo está ok



$ docker ps

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/ce12e52c-d53d-4ac6-9748-4a77135d1af5)


configurando o roteador - execute cada linha separadamente.

$ docker exec -it mongo-rt mongosh

$ sh.addShard("shard001/mongo-sd001a:27018")

$ sh.addShard("shard001/mongo-sd001b:27018") 

$ sh.addShard("shard002/mongo-sd002a:27019")

$ sh.addShard("shard002/mongo-sd002b:27019") 

$ sh.addShard("shard003/mongo-sd003a:27020")

$ sh.addShard("shard003/mongo-sd003b:27020")


para conferir

sh.status()

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/2678ecdf-73ed-457c-925a-ef37e9aad5bf)

