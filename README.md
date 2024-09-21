# levantar el docker

```{bash}
docker compose up -d
```


# ingresar al conenedor

```{bash}
 docker exec -it kafkaetl-spark-master-1 /bin/bash
```

# instalar las librerias

```{bash}
pip install -r jobs/requirements.txt
```

# ejecutar el productor

```{bash}
python jobs/main.py
```


# ejecutar el consumidor

```{bash}
spark-submit --conf "spark.pyspark.python=python" --packages com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3 jobs/spark-consumer.py
```


# Cassandra Container

QUERY_TABLE = 'select * from property_streams.properties;'
INIT_DB= 'cqlsh'


# Kafka Container

CONSUMER = 'kafka-console-consumer --topic properties --bootstrap-server kafka-broker:9092'
LIST_TOPICS = 'kafka-topics --list --bootstrap-server kafka-broker:9092'