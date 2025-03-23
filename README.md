# 🎥 Video Processing Pipeline with FastAPI, RabbitMQ & FFmpeg  

A **distributed event-driven video processing pipeline** that allows users to upload videos, extract metadata, and apply video enhancements using **FastAPI, RabbitMQ, FFmpeg, and WebSockets**.

## 📌 Features  
✅ **Upload Videos** via a frontend interface  
✅ **Metadata Extraction** (Resolution, FPS, Frame Count, Duration)  
✅ **Video Enhancement** (Grayscale Conversion using FFmpeg)  
✅ **Real-time WebSocket Updates** for status tracking  
✅ **Asynchronous Event Processing** with RabbitMQ workers  

---

## 🛠️ **Tech Stack**  
- **Frontend:** React, HTML/CSS (Industry-standard styling)  
- **Backend:** FastAPI (Python-based high-performance API)  
- **Queue:** RabbitMQ (Message Broker for distributed processing)  
- **Video Processing:** FFmpeg (Efficient video enhancement & encoding)  
- **Database:** (Optional) Can be integrated with MongoDB/PostgreSQL  

---

## 🚀 **Architecture Overview**  

```plaintext
 ┌────────────┐         ┌───────────┐        ┌─────────────────────┐        ┌──────────────────────┐
 │ React UI   │  ⇄     │ FastAPI   │ ⇄    │ RabbitMQ Exchange │ ⇄  │ Worker Services (FFmpeg) │
 └────────────┘         └───────────┘        └─────────────────────┘        └──────────────────────┘
      ⬆                             ⬆                                   ⬆                                    ⬆
[WebSocket Updates]   [Video Upload]      [Metadata Extraction]     [Video Enhancement]
