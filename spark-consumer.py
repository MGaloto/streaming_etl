from pyspark.sql import SparkSession
from cassandra.cluster import Cluster
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *
from cassandra import OperationTimedOut
import time
#import os
#import sys

#os.environ['PYSPARK_PYTHON'] = 'python3'
#os.environ['PYSPARK_DRIVER_PYTHON'] = 'python'



def create_keyspace(session):
    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS property_streams
        WITH replication = {'class' : 'SimpleStrategy', 'replication_factor':'1'}
        """
    )

def create_table(session):
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS property_streams.properties (
            id int,
            nombre text,
            email text,
            PRIMARY KEY (id)
        );
        """
    )


def insert_data(session, **kwargs):
        session.execute(
            """
            INSERT INTO property_streams.properties (id, nombre, email)
            VALUES (%s, %s, %s);
            """,kwargs.values()
        )

def create_cassandra_session(max_retries=5, delay=2):
    for attempt in range(max_retries):
        try:
            session = Cluster(['cassandra']).connect() #Cluster(['localhost']).connect()
            print("Conexión exitosa a Cassandra")
            return session
        except (ConnectionError, OperationTimedOut) as e:
            print(f"Error al conectar a Cassandra: {e}. Intento {attempt + 1}/{max_retries}")
            time.sleep(delay)
    raise Exception("No se pudo establecer la conexión con Cassandra después de múltiples intentos.")


def main():
    package_cassandra="com.datastax.spark:spark-cassandra-connector_2.13:3.4.1,"
    package_kafka="org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3"

    spark = (
        SparkSession.builder.appName("ETL")
        .config("spark.cassandra.connect.host", "cassandra") #.config("spark.cassandra.connect.host", "localhost")
        #.config("spark.mongodb.input.uri", "mongodb://localhost:27017/")
        .config(
            "spark.jars.packages", 
            f"{package_cassandra}"
            f"{package_kafka}"
        #    "org.mongodb.spark:mongo-spark-connector_2.13:10.4.0,"
        )
        .getOrCreate()
    )

    session = create_cassandra_session()

    create_keyspace(session)
    create_table(session)


    kafka_df = (
        spark.readStream.format('kafka')
        .option("kafka.bootstrap.servers", "kafka-broker:9092") #.option("kafka.bootstrap.servers", "localhost:9092")
        .option("subscribe", "properties")
        .option("startingOffsets", "earliest")
        .load()
    )
    

    schema = StructType([
         StructField('id', IntegerType(), False),
         StructField('nombre', StringType(), True),
         StructField('email', StringType(), True)
    ])

    kafka_df = (
         kafka_df
         .selectExpr("CAST(value AS STRING) as value")
         .select(from_json(col('value'), schema).alias('data'))
         .select('data.*')
    )
    

    query = (
        kafka_df.writeStream
        .foreachBatch(
             lambda batch_df, batch_id: batch_df.foreach(
                  lambda row :insert_data(create_cassandra_session(), **row.asDict())
                  )
             )
             #.trigger(processingTime='5 seconds')
             .start()
             .awaitTermination()
    )




if __name__ == "__main__":
    main()

