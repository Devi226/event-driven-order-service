import pika, json

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.exchange_declare(exchange='grocery.events', exchange_type='topic')

def callback(ch, method, properties, body):
    event = json.loads(body)
    event_id = properties.message_id
    print(f"Processing {event_id}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='inventory.queue', on_message_callback=callback)
print("Inventory consumer started")
channel.start_consuming()