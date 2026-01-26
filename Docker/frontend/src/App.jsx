import React, { useState, useRef, useEffect } from 'react';
import { synthesizeAudio } from './api';

function App() {
    const [text, setText] = useState('');
    const [audioData, setAudioData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const audioRef = useRef(null);

    const handleSynthesize = async () => {
        if (!text) return;
        setLoading(true);
        try {
            const data = await synthesizeAudio(text);
            setAudioData(data);
        } catch (error) {
            alert("Failed to synthesize audio.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (audioData && audioRef.current) {
            audioRef.current.src = `data:audio/mp3;base64,${audioData.audio_base64}`;
            audioRef.current.play();
            setIsPlaying(true);
        }
    }, [audioData]);

    return (
        <div style={{
            minHeight: '100vh',
            backgroundColor: '#f3f4f6',
            padding: '2rem',
            fontFamily: 'Inter, sans-serif'
        }}>
            <div style={{ maxWidth: '48rem', margin: '0 auto' }}>
                <div style={{
                    backgroundColor: 'white',
                    padding: '2rem',
                    borderRadius: '1rem',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}>
                    <h1 style={{ fontSize: '1.875rem', fontWeight: 'bold', marginBottom: '1.5rem', textAlign: 'center' }}>
                        Web Reader
                    </h1>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
                        <textarea
                            placeholder="Paste your text here..."
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            rows={10}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                borderRadius: '0.5rem',
                                border: '1px solid #d1d5db',
                                fontFamily: 'inherit',
                                fontSize: '1rem',
                                resize: 'vertical'
                            }}
                        />
                        <button
                            onClick={handleSynthesize}
                            disabled={loading || !text}
                            style={{
                                backgroundColor: '#2563eb',
                                color: 'white',
                                padding: '0.75rem 1.5rem',
                                borderRadius: '0.5rem',
                                border: 'none',
                                cursor: (loading || !text) ? 'not-allowed' : 'pointer',
                                opacity: (loading || !text) ? 0.7 : 1,
                                fontWeight: '600',
                                alignSelf: 'flex-end'
                            }}
                        >
                            {loading ? 'Processing...' : 'Listen'}
                        </button>
                    </div>

                    <audio
                        ref={audioRef}
                        controls
                        style={{ width: '100%', marginTop: '2rem', display: audioData ? 'block' : 'none' }}
                        onPlay={() => setIsPlaying(true)}
                        onPause={() => setIsPlaying(false)}
                    />
                </div>
            </div>
        </div>
    );
}

export default App;
