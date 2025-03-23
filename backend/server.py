from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import aiofiles
import pika
import os
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory setup
UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")

def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.exchange_declare(exchange="video_tasks", exchange_type="fanout")
    return channel, connection
clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        clients.remove(websocket)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    channel, connection = get_rabbitmq_channel()
    task = {"video_path": file_path, "filename": file.filename}
    channel.basic_publish(exchange="video_tasks", routing_key="", body=json.dumps(task))
    connection.close()

    return {"message": "Video uploaded successfully", "filename": file.filename}

async def notify_clients(data):
    for ws in clients:
        try:
            await ws.send_json(data)
        except:
            clients.remove(ws)

@app.post("/internal/video-enhancement-status")
async def video_enhancement_status(data: dict):
    filename = data["filename"]
    await notify_clients({"status": "enhanced", "filename": filename})
    return {"message": "Video enhancement update sent"}

@app.post("/internal/metadata-extraction-status")
async def metadata_extraction_status(data: dict):
    filename = data["filename"]
    metadata = data["metadata"]
    await notify_clients({"status": "metadata", "filename": filename, "metadata": metadata})
    return {"message": "Metadata update sent"}
