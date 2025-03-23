import React, { useState, useEffect } from "react";
import "../styles/VideoProcessor.css"; 

const VideoProcessor = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [metadata, setMetadata] = useState(null);
    const [enhancedVideo, setEnhancedVideo] = useState(null);
    const [status, setStatus] = useState("Waiting for upload...");
    const [ws, setWs] = useState(null);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws");
        setWs(socket);

        socket.onopen = () => setStatus("Connected to WebSocket.");
        
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
        
            if (data.status === "error") {
                setStatus(`Error: ${data.message}. Please retry.`);
            } else if (data.status === "metadata") {
                setMetadata(data.metadata);
                setStatus(`Metadata received: ${data.filename}`);
                setProcessing(true);
            } else if (data.status === "enhanced") {
                setEnhancedVideo(`http://localhost:8000/processed/${data.filename}`);
                setStatus(`Enhanced video ready: ${data.filename}`);
                setProcessing(false);
            }
        };
        

        return () => socket.close();
    }, []);

    const handleUpload = async () => {
        if (!selectedFile) {
            alert("Please select a video first.");
            return;
        }

        setUploading(true);
        setStatus("Uploading video...");

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("http://localhost:8000/upload", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                setStatus(`Uploaded: ${data.filename}. Extracting metadata...`);
            } else {
                throw new Error("Upload failed.");
            }
        } catch (error) {
            console.error("Upload error:", error);
            setStatus("Upload failed. Try again.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="container">
            <h1 className="title">Video Processor</h1>

            <input type="file" accept="video/*" onChange={(e) => setSelectedFile(e.target.files[0])} className="file-input" />

            <button onClick={handleUpload} disabled={uploading} className={`upload-btn ${uploading ? "disabled" : ""}`}>
                {uploading ? "Uploading..." : "Upload Video"}
            </button>

            <p className="status">{status}</p>

            {processing && (
                <div className="loader-container">
                    <p>Enhancing video...</p>
                    <div className="loader"></div>
                </div>
            )}

            {metadata && (
                <div className="metadata">
                    <h2>Metadata</h2>
                    <pre>{JSON.stringify(metadata, null, 2)}</pre>
                </div>
            )}

            {enhancedVideo && (
                <div className="video-container">
                    <h2>Enhanced Video</h2>
                    <video controls src={enhancedVideo} className="video-player"></video>
                </div>
            )}
        </div>
    );
};

export default VideoProcessor;
