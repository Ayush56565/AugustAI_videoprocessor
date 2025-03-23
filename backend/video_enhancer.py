import pika
import json
import os
import requests
import ffmpeg

RABBITMQ_HOST = "localhost"
PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def enhance_video(input_path, output_path):

    try:
        (
            ffmpeg
            .input(input_path)
            .filter("hue", s=0)  # Converts to grayscale
            .output(output_path, vcodec="libx264", pix_fmt="yuv420p", crf=23)
            .run(overwrite_output=True)  # Overwrites if file exists
        )
        print(f"Enhanced video saved at: {output_path}")
    except Exception as e:
        print(f"Error in FFmpeg processing: {e}")

def callback(ch, method, properties, body):

    task = json.loads(body)
    input_path = task["video_path"]
    filename = task["filename"]

    # Ensure the output is MP4
    output_filename = f"{os.path.splitext(filename)[0]}_enhanced.mp4"
    output_path = os.path.join(PROCESSED_DIR, output_filename)

    enhance_video(input_path, output_path)

    # Notify FastAPI server
    requests.post("http://localhost:8000/internal/video-enhancement-status", json={"filename": output_filename})

# Setup RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.exchange_declare(exchange="video_tasks", exchange_type="fanout")

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange="video_tasks", queue=queue_name)

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print("Video Enhancement Worker started...")
channel.start_consuming()
