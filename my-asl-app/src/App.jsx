import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

// CHANGE THIS: If your Python server uses a different port, change 5000 to that number
const SOCKET_SERVER_URL = "http://localhost:5000";

const App = () => {
  const [currentPrediction, setCurrentPrediction] = useState({ word: "Waiting...", confidence: 0 });
  const [sentence, setSentence] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState(["System initialized"]);

  // --- Live Connection Logic ---
  useEffect(() => {
    // 1. Connect to your Python backend
    const socket = io(SOCKET_SERVER_URL);

    socket.on('connect', () => {
      setIsConnected(true);
      addLog("Connected to ASLShadow Backend");
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      addLog("Disconnected from Backend");
    });

    // 2. Listen for the prediction. 
    // Note: If your Python code uses a different name than 'prediction', change it here!
    socket.on('prediction', (data) => {
      // Expecting data format: { "word": "Hello", "confidence": 92 }
      setCurrentPrediction({
        word: data.word || data.prediction || "Unknown",
        confidence: data.confidence || 0
      });
      addLog(`Received: ${data.word}`);
    });

    return () => socket.disconnect();
  }, []);

  const addLog = (msg) => {
    setLogs(prev => [`[${new Date().toLocaleTimeString([], {hour12:false})}] ${msg}`, ...prev.slice(0, 5)]);
  };

  const addToSentence = (word = currentPrediction.word) => {
    if (word === "Waiting...") return;
    setSentence(prev => prev ? `${prev} ${word}` : word);
  };

  const speak = () => {
    const utterance = new SpeechSynthesisUtterance(sentence);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>ASL Shadow Translator</h1>
        <div style={{...styles.badge, backgroundColor: isConnected ? '#e6f4ea' : '#fee2e2', color: isConnected ? '#137333' : '#ef4444'}}>
          {isConnected ? '● Connected' : '○ Offline'}
        </div>
      </header>

      <div style={styles.grid}>
        <div style={styles.left}>
          {/* Gesture Video Placeholder */}
          <div style={styles.feedCard}>
            <div style={{textAlign:'center'}}>
              <p style={{fontSize: '2rem'}}>📷</p>
              <p>Camera feed handled by Python</p>
              <p style={{fontSize: '0.8rem', opacity: 0.5}}>Predictions appearing below</p>
            </div>
          </div>

          {/* Real-time Prediction */}
          <div style={styles.card}>
            <p style={styles.label}>Detected Sign</p>
            <h2 style={styles.word}>{currentPrediction.word}</h2>
            <div style={styles.progressTrack}>
               <div style={{...styles.progressBar, width: `${currentPrediction.confidence}%`}}></div>
            </div>
            <button onClick={() => addToSentence()} style={styles.primaryBtn}>Add to Sentence</button>
          </div>
        </div>

        <div style={styles.right}>
          {/* Sentence Builder */}
          <div style={styles.card}>
            <p style={styles.label}>Sentence</p>
            <div style={styles.sentenceBox}>{sentence || "Sign something to begin..."}</div>
            <div style={styles.btnRow}>
              <button onClick={speak} style={styles.speakBtn}>🔊 Speak</button>
              <button onClick={() => setSentence("")} style={styles.clearBtn}>Clear</button>
            </div>
          </div>

          {/* Status Logs */}
          <div style={styles.logCard}>
            <p style={styles.label}>System Status</p>
            {logs.map((log, i) => <div key={i} style={styles.logItem}>{log}</div>)}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Styling ---
const styles = {
  container: { padding: '2rem', fontFamily: 'Inter, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh', color: '#1e293b' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', maxWidth: '1000px', margin: '0 auto 2rem auto' },
  title: { fontSize: '1.8rem', fontWeight: '800', background: 'linear-gradient(to right, #4f46e5, #9333ea)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' },
  badge: { padding: '6px 14px', borderRadius: '100px', fontSize: '0.8rem', fontWeight: 'bold', border: '1px solid rgba(0,0,0,0.05)' },
  grid: { display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '1.5rem', maxWidth: '1000px', margin: '0 auto' },
  feedCard: { height: '350px', backgroundColor: '#0f172a', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', marginBottom: '1.5rem' },
  card: { backgroundColor: '#fff', padding: '1.5rem', borderRadius: '16px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)', marginBottom: '1rem' },
  logCard: { backgroundColor: '#1e293b', color: '#94a3b8', padding: '1.2rem', borderRadius: '16px' },
  label: { fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', color: '#64748b', marginBottom: '12px', letterSpacing: '0.05em' },
  word: { fontSize: '3.5rem', margin: '0.5rem 0', color: '#4f46e5', fontWeight: '800' },
  progressTrack: { height: '10px', backgroundColor: '#f1f5f9', borderRadius: '10px', marginBottom: '1.5rem', overflow: 'hidden' },
  progressBar: { height: '100%', backgroundColor: '#10b981', transition: 'width 0.5s ease' },
  sentenceBox: { minHeight: '80px', padding: '1.2rem', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '1.3rem', marginBottom: '1rem' },
  primaryBtn: { width: '100%', padding: '14px', backgroundColor: '#4f46e5', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: '700' },
  btnRow: { display: 'flex', gap: '10px' },
  speakBtn: { flex: 2, padding: '12px', backgroundColor: '#8b5cf6', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: '600' },
  clearBtn: { flex: 1, padding: '12px', backgroundColor: '#f1f5f9', color: '#64748b', border: 'none', borderRadius: '10px', cursor: 'pointer' },
  logItem: { fontSize: '0.8rem', marginBottom: '6px', fontFamily: 'monospace' }
};

export default App;