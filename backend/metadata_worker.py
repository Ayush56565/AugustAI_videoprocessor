import pika
import json
import cv2
import requests

def extract_metadata(video_path):
    cap = cv2.VideoCapture(video_path)
    metadata = {
        "resolution": f"{int(cap.get(3))}x{int(cap.get(4))}",
        "fps": cap.get(5),
        "frame_count": int(cap.get(7))
    }
    cap.release()
    return metadata

def callback(ch, method, properties, body):
    task = json.loads(body)
    video_path = task["video_path"]

    metadata = extract_metadata(video_path)

    # Notify FastAPI server
    requests.post("http://localhost:8000/internal/metadata-extraction-status", json={
        "filename": task["filename"],
        "metadata": metadata
    })

# Setup RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.exchange_declare(exchange="video_tasks", exchange_type="fanout")

# Create a temporary queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange="video_tasks", queue=queue_name)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Metadata Extraction Worker started...")
channel.start_consuming()
