# Criando um Cluster MongoDB utilizando conteiners no Docker

Nesse projeto vou exemplicar um projeto de implantação de um banco de dados documental escalável e distribuido, com o objetivo de aplicar os conhecimentos adquiridos nas aulas de Banco de Dados NoSQL do curso de Engenharia de Dados da PUC Minas, ministrado pelo (excelente) professor [Anderson Theobaldo](https://www.linkedin.com/in/atheobaldo/)

# 🚀 Começando

## [Cenário]

Vamos criar um cluster para atender às necessidades de uma cadeia de supermercados, com foco em escalabilidade e eficiência. Nosso cliente planeja expandir para novas cidades em breve, aumentando rapidamente o número de filiais.

Cada filial possui um grande volume de produtos em seu estoque. O sistema precisa ser capaz de lidar com milhões de registros de produtos, garantindo que as consultas de estoque e as atualizações de inventário sejam rápidas e eficientes. A escalabilidade do sistema é essencial, pois nosso cliente tem planos de expansão e vai abrir novas filiais em um futuro breve.

## [Arquitetura da Solução]
Baseando-se no artigo [artigo](https://gustavo-leitao.medium.com/criando-um-cluster-mongodb-com-replicaset-e-sharding-com-docker-9cb19d456b56) de Gustavo Leitão, vamos criar um cluster de MongoDB em Docker. Para isso, utilizaremos três tipos de serviços: Roteador, Servidor de Configuração e Shards, que serão responsáveis pelas partições.


No caso do nosso cliente já existem 4 filiais

_______

Todos os comandos abaixo devem ser executados diretamente no prompt do comando do seu computador. no meu caso, estou usando Windows

## Criando a Rede

```
$ docker network create supermercados-gigios
```

#Criando os ConfigServers
```
$ docker run --name m-c01 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
```
```
$ docker run --name m-c02 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
```
```
$ docker run --name m-c03 --net supermercados-gigios -d mongo mongod --configsvr --replSet configserver --port 27017
```
#Configurando os ConfigServers

```
$ docker exec -it m-c01 mongosh
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
         { _id: 2, host : "m-c03:27017" }
      ]
   }
)
```

## Criando os Shards

```
$ docker run --name mongo-sd001a --net supermercados-gigios -d mongo mongod --port 27018 --shardsvr --replSet shard001
```
```
$ docker run --name mongo-sd001b --net supermercados-gigios -d mongo mongod --port 27018 --shardsvr --replSet shard001
```
```
$ docker run --name mongo-sd002a --net supermercados-gigios -d mongo mongod --port 27019 --shardsvr --replSet shard002
```
```
$ docker run --name mongo-sd002b --net supermercados-gigios -d mongo mongod --port 27019 --shardsvr --replSet shard002
```
```
$ docker run --name mongo-sd003a --net supermercados-gigios -d mongo mongod --port 27020 --shardsvr --replSet shard003
```
```
$ docker run --name mongo-sd003b --net supermercados-gigios -d mongo mongod --port 27020 --shardsvr --replSet shard003
```

## configurando os shards - procedimento precisa ser feito para todos os shards individualmente.

```
$ docker exec -it mongo-sd001a mongosh --port 27018
```
```
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
```

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/666e1536-28ec-4014-97dd-706a03921762)

```
$ docker exec -it mongo-sd002a mongosh --port 27019
```
```
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
```
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/5120ef50-6d91-4222-93b7-bbfe0e8111b9)

```
$ docker exec -it mongo-sd003a mongosh --port 27020
```
```
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
```
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/056387b9-fca9-448b-8546-960fd18c298f)

## Criando o Roteador

```
$ docker run -p 27017:27017 --name mongo-rt --net supermercados-gigios -d mongo mongos --port 27017 --configdb configserver/m-c01:27017,m-c02:27017,m-c03:27017 --bind_ip_all
```
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/4f82339b-44e8-4551-bb47-bf5fc67a649c)


checando se tudo está ok


```
$ docker ps
```
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/ce12e52c-d53d-4ac6-9748-4a77135d1af5)


## Configurando o roteador - execute cada linha separadamente.

```
$ docker exec -it mongo-rt mongosh
```
```
$ sh.addShard("shard001/mongo-sd001a:27018")
```
```
$ sh.addShard("shard001/mongo-sd001b:27018") 
```
```
$ sh.addShard("shard002/mongo-sd002a:27019")
```
```
$ sh.addShard("shard002/mongo-sd002b:27019") 
```
```
$ sh.addShard("shard003/mongo-sd003a:27020")
```
```
$ sh.addShard("shard003/mongo-sd003b:27020")
```

para conferir

```
sh.status()
```
![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/2678ecdf-73ed-457c-925a-ef37e9aad5bf)


Após a criação do cluster, podemo utilizar o MongoCompass para acessar o ambiente. é interessante observar as coleções do database Config:

nossos Shards Criados

![image](https://github.com/giovaniramosferreira/mongodb_cluster_on_docker/assets/62471615/b1007c5e-eb40-40c9-8a2d-ff0626cd6ec4)


__________________________________________________________


fazer relatorio nesse padrão

# Título do projeto

Um parágrafo da descrição do projeto vai aqui

## 🚀 Começando

Essas instruções permitirão que você obtenha uma cópia do projeto em operação na sua máquina local para fins de desenvolvimento e teste.

Consulte **[Implantação](#-implanta%C3%A7%C3%A3o)** para saber como implantar o projeto.

### 📋 Pré-requisitos

De que coisas você precisa para instalar o software e como instalá-lo?

```
Dar exemplos
```

### 🔧 Instalação

Uma série de exemplos passo-a-passo que informam o que você deve executar para ter um ambiente de desenvolvimento em execução.

Diga como essa etapa será:

```
Dar exemplos
```

E repita:

```
Até finalizar
```

Termine com um exemplo de como obter dados do sistema ou como usá-los para uma pequena demonstração.

## ⚙️ Executando os testes

Explicar como executar os testes automatizados para este sistema.

### 🔩 Analise os testes de ponta a ponta

Explique que eles verificam esses testes e porquê.

```
Dar exemplos
```

### ⌨️ E testes de estilo de codificação

Explique que eles verificam esses testes e porquê.

```
Dar exemplos
```

## 📦 Implantação

Adicione notas adicionais sobre como implantar isso em um sistema ativo

## 🛠️ Construído com

Mencione as ferramentas que você usou para criar seu projeto

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - O framework web usado
* [Maven](https://maven.apache.org/) - Gerente de Dependência
* [ROME](https://rometools.github.io/rome/) - Usada para gerar RSS

## 🖇️ Colaborando

Por favor, leia o [COLABORACAO.md](https://gist.github.com/usuario/linkParaInfoSobreContribuicoes) para obter detalhes sobre o nosso código de conduta e o processo para nos enviar pedidos de solicitação.

## 📌 Versão

Nós usamos [SemVer](http://semver.org/) para controle de versão. Para as versões disponíveis, observe as [tags neste repositório](https://github.com/suas/tags/do/projeto). 

## ✒️ Autores

Mencione todos aqueles que ajudaram a levantar o projeto desde o seu início

* **Um desenvolvedor** - *Trabalho Inicial* - [umdesenvolvedor](https://github.com/linkParaPerfil)
* **Fulano De Tal** - *Documentação* - [fulanodetal](https://github.com/linkParaPerfil)

Você também pode ver a lista de todos os [colaboradores](https://github.com/usuario/projeto/colaboradores) que participaram deste projeto.

## 📄 Licença

Este projeto está sob a licença (sua licença) - veja o arquivo [LICENSE.md](https://github.com/usuario/projeto/licenca) para detalhes.

## 🎁 Expressões de gratidão

* Conte a outras pessoas sobre este projeto 📢;
* Convide alguém da equipe para uma cerveja 🍺;
* Um agradecimento publicamente 🫂;
* etc.


---
