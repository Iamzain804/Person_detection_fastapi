import React, { useState, useRef, useEffect } from 'react';
import { Camera, Shield, Zap, Activity, Info } from 'lucide-react';

// Replace the URL below with your Hugging Face Direct URL
const API_URL = 'https://muhammadzain09-ai-person-detector-api.hf.space/api/v1/detect';
const API_KEY = 'your-super-secret-api-key';

function App() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({ count: 0, time: 0 });
  const [error, setError] = useState(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  // Start Webcam
  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720 }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;

        // Force video to play
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play().catch(e => console.error("Video play failed:", e));
        };

        setIsStreaming(true);
        setError(null);
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      setError("Webcam access denied or not found.");
    }
  };

  // Stop Webcam
  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      setIsStreaming(false);
      setDetections([]);
    }
  };

  // Capture Frame and Send to API
  const processFrame = async () => {
    if (!isStreaming || !videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    // Draw video frame to hidden canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to Blob
    canvas.toBlob(async (blob) => {
      if (!blob) return;

      const formData = new FormData();
      formData.append('file', blob, 'frame.jpg');

      try {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: {
            'X-API-Key': API_KEY
          },
          body: formData
        });

        if (response.ok) {
          const data = await response.json();
          setDetections(data.detections);
          setStats({ count: data.count, time: data.inference_time });
        }
      } catch (err) {
        console.error("API Error:", err);
      }
    }, 'image/jpeg', 0.8);
  };

  // Continuous Processing Loop
  useEffect(() => {
    let interval;
    if (isStreaming) {
      interval = setInterval(processFrame, 500); // Check every 500ms
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isStreaming]);

  return (
    <div style={{ minHeight: '100vh', padding: '20px' }}>
      {/* Header */}
      <header style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1 className="glow-text" style={{ fontSize: '3rem', margin: '0', fontWeight: '800' }}>
          NEON SENTRY
        </h1>
        <p style={{ color: '#666', letterSpacing: '4px' }}>AI POWERED PERSON DETECTION</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '30px', maxWidth: '1200px', margin: '0 auto' }}>

        {/* Main Viewport */}
        <div className="neon-border" style={{ background: '#111', padding: '10px', borderRadius: '12px' }}>
          <div className="webcam-container">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              style={{ width: '100%', minHeight: '450px', display: 'block', objectFit: 'cover' }}
            />

            {/* Detection Bounding Boxes */}
            <div className="detection-overlay">
              {detections.map((det, index) => {
                const [x1, y1, x2, y2] = det.box;
                const videoWidth = videoRef.current?.videoWidth || 1;
                const videoHeight = videoRef.current?.videoHeight || 1;

                return (
                  <div
                    key={index}
                    className="bounding-box"
                    style={{
                      left: `${(x1 / videoWidth) * 100}%`,
                      top: `${(y1 / videoHeight) * 100}%`,
                      width: `${((x2 - x1) / videoWidth) * 100}%`,
                      height: `${((y2 - y1) / videoHeight) * 100}%`
                    }}
                  >
                    <span className="label-tag">
                      PERSON {Math.round(det.confidence * 100)}%
                    </span>
                  </div>
                );
              })}
            </div>

            {!isStreaming && (
              <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.8)' }}>
                <Camera size={64} color="#333" />
              </div>
            )}
          </div>

          <div style={{ marginTop: '20px', display: 'flex', gap: '15px', justifyContent: 'center' }}>
            {!isStreaming ? (
              <button className="btn-neon" onClick={startWebcam}>
                INITIALIZE SENTRY
              </button>
            ) : (
              <button className="btn-neon" style={{ borderColor: '#ff3e3e', color: '#ff3e3e' }} onClick={stopWebcam}>
                TERMINATE SESSION
              </button>
            )}
          </div>
          {error && <p style={{ color: '#ff3e3e', textAlign: 'center', marginTop: '10px' }}>{error}</p>}
        </div>

        {/* Sidebar Stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          <div className="neon-border" style={{ background: '#111', padding: '20px', borderRadius: '12px' }}>
            <h3 style={{ margin: '0 0 15px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Activity className="glow-text" size={20} /> LIVE STATUS
            </h3>
            <div style={{ fontSize: '24px', fontWeight: '800' }}>
              {isStreaming ? <span style={{ color: '#00ff00' }}>ONLINE</span> : <span style={{ color: '#ff3e3e' }}>OFFLINE</span>}
            </div>
          </div>

          <div className="neon-border" style={{ background: '#111', padding: '20px', borderRadius: '12px' }}>
            <h3 style={{ margin: '0 0 15px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Shield className="glow-text" size={20} /> DETECTIONS
            </h3>
            <div style={{ fontSize: '48px', fontWeight: '800', color: '#00d2ff' }}>
              {stats.count}
            </div>
            <p style={{ margin: '0', color: '#666' }}>PERSONS IDENTIFIED</p>
          </div>

          <div className="neon-border" style={{ background: '#111', padding: '20px', borderRadius: '12px' }}>
            <h3 style={{ margin: '0 0 15px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Zap className="glow-text" size={20} /> LATENCY
            </h3>
            <div style={{ fontSize: '24px', fontWeight: '800' }}>
              {stats.time.toFixed(3)}s
            </div>
            <p style={{ margin: '0', color: '#666' }}>INFERENCE SPEED</p>
          </div>

          <div style={{ background: '#1a1a1a', padding: '15px', borderRadius: '12px', fontSize: '12px', color: '#888' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '5px' }}>
              <Info size={14} /> SECURITY LOG
            </div>
            {isStreaming ? "Scanning environment for human activity..." : "Awaiting user authentication and stream initialization."}
          </div>

        </div>
      </div>

      {/* Hidden Canvas for Processing */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
    </div>
  );
}

export default App;
