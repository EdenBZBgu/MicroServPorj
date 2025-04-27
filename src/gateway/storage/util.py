import pika, json
from pika.exceptions import AMQPConnectionError

def upload_file(file, fs, channel, access):
    try:
        # Upload the file to MongoDB
        file_id = fs.put(file, filename=file.filename)

        # Send a message to RabbitMQ
        message = {
            'file_id': str(file_id),
            'mp3_file_id': None,
            'user_id': access['username'],
        }
        try:
            channel.basic_publish(exchange='',
                                  routing_key='video',
                                  body=json.dumps(message),
                                  properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
                                  )
            return None
        except AMQPConnectionError:
            fs.delete(file_id)
            return {'message': 'Failed to connect to RabbitMQ'}, 500

    except Exception as e:
        return {'message': str(e)}, 500