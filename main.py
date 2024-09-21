from kafka import KafkaProducer
import json
import time
from faker import Faker
from kafka.admin import KafkaAdminClient, NewTopic





def main():

    faker = Faker()
    limit = 100

    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers="kafka-broker:29092", 
            client_id='test'
        )
        topic_list = [NewTopic(name="properties", num_partitions=1, replication_factor=1)]
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
    except Exception as e:
        print(e)

    producer = KafkaProducer(
            bootstrap_servers='kafka-broker:9092', #localhost
            max_block_ms=1000
        )

    for i in range(0,limit):
        time.sleep(0.25)
        data = {
            'id': i,
            'nombre': faker.name(),
            'email': faker.email()
        }
        print(f"Faltan: {limit-i}. {producer}")

        producer.send('properties', value=json.dumps(data).encode('utf-8'))



if __name__ == "__main__":
    main()