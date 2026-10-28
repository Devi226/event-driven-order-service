import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.exchange_declare(exchange='grocery.events', exchange_type='topic', durable=True)
channel.queue_declare(queue='inventory.queue', durable=True)
channel.queue_declare(queue='inventory.dlq', durable=True)

def callback(ch, method, properties, body):
    try:
        event = json.loads(body)
        event_id = properties.message_id
        print(f"Processing event {event_id} correlation {properties.correlation_id}")
        # idempotency check here - skip if already processed
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error {e} - sending to DLQ")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(queue='inventory.queue', on_message_callback=callback)
print("Inventory consumer started with DLQ and retry")
channel.start_consuming()