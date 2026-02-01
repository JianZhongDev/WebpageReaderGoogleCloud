import React, { useState, useRef, useEffect } from 'react';
import { synthesizeAudio, fetchVoices, detectLanguage } from './api';

function App() {
    const [text, setText] = useState('');
    const [words, setWords] = useState([]);
    const [audioData, setAudioData] = useState(null);
    const [timepoints, setTimepoints] = useState([]);
    const [activeWordIndex, setActiveWordIndex] = useState(-1);
    const [loading, setLoading] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [voices, setVoices] = useState([]);
    const [selectedVoice, setSelectedVoice] = useState("en-US-Wavenet-D");
    const audioRef = useRef(null);

    useEffect(() => {
        fetchVoices().then(data => {
            if (data && data.length > 0) {
                setVoices(data);
                if (!data.find(v => v.name === selectedVoice)) {
                    setSelectedVoice(data[0].name);
                }
            }
        });
    }, []);

    // Debounce detection
    useEffect(() => {
        const timer = setTimeout(async () => {
            if (text && text.trim().length > 1) {
                const result = await detectLanguage(text);
                if (result && result.recommended_voice) {
                    // Check if recommended voice exists in our list
                    const voiceExists = voices.find(v => v.name === result.recommended_voice);
                    if (voiceExists) {
                        setSelectedVoice(result.recommended_voice);
                    }
                }
            }
        }, 800); // 800ms debounce

        return () => clearTimeout(timer);
    }, [text, voices]);

    const handleSynthesize = async () => {
        if (!text) return;
        setLoading(true);
        // Reset state
        setAudioData(null);
        setTimepoints([]);
        setActiveWordIndex(-1);
        setWords([]);

        try {
            const data = await synthesizeAudio(text, selectedVoice);
            setAudioData(data.audio_base64);
            setTimepoints(data.timepoints || []);
            setWords(data.disp_world_list || []);
        } catch (error) {
            console.error(error);
            const msg = error.response?.data?.detail || error.message || "Failed to synthesize";
            alert(`Error: ${msg}`);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (audioData && audioRef.current) {
            // Use WAV mime type for LINEAR16
            audioRef.current.src = `data:audio/wav;base64,${audioData}`;
            audioRef.current.play().catch(e => console.log("Auto-play prevented:", e));
            setIsPlaying(true);
        }
    }, [audioData]);

    const handleTimeUpdate = () => {
        if (!audioRef.current || timepoints.length === 0) return;

        const currentTime = audioRef.current.currentTime;

        // Find the last timepoint that is <= active time
        // Timepoints are sorted by time
        let activeIdx = -1;
        for (let i = 0; i < timepoints.length; i++) {
            if (currentTime >= timepoints[i].time_seconds) {
                // mark_name is the index string "0", "1", etc.
                activeIdx = parseInt(timepoints[i].mark_name, 10);
            } else {
                // Once we find a timepoint in the future, we stop
                break;
            }
        }

        if (activeIdx !== activeWordIndex) {
            setActiveWordIndex(activeIdx);
        }
    };

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
                            rows={6}
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

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <label style={{ fontWeight: 600, color: '#4b5563' }}>Voice:</label>
                                <select
                                    value={selectedVoice}
                                    onChange={(e) => setSelectedVoice(e.target.value)}
                                    style={{
                                        padding: '0.5rem',
                                        borderRadius: '0.5rem',
                                        border: '1px solid #d1d5db',
                                        backgroundColor: 'white',
                                        fontSize: '0.9rem'
                                    }}
                                >
                                    {voices.map(voice => (
                                        <option key={voice.name} value={voice.name}>
                                            {voice.name} ({voice.ssml_gender})
                                        </option>
                                    ))}
                                </select>
                            </div>

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
                                    fontWeight: '600'
                                }}
                            >
                                {loading ? 'Processing...' : 'Listen'}
                            </button>
                        </div>
                    </div>

                    {/* Karaoke Display Area */}
                    {words.length > 0 && (
                        <div style={{
                            marginBottom: '2rem',
                            padding: '1.5rem',
                            backgroundColor: '#f9fafb',
                            borderRadius: '0.75rem',
                            lineHeight: '2',
                            fontSize: '1.125rem',
                            color: '#374151',
                            border: '1px solid #e5e7eb'
                        }}>
                            {words.map((word, index) => (
                                <span
                                    key={index}
                                    style={{
                                        backgroundColor: index === activeWordIndex ? '#fde047' : 'transparent', // Yellow highlight
                                        padding: '0.1rem 0.2rem',
                                        borderRadius: '0.25rem',
                                        transition: 'background-color 0.2s',
                                        display: 'inline-block',
                                        marginRight: '0.25rem'
                                    }}
                                >
                                    {word}
                                </span>
                            ))}
                        </div>
                    )}

                    <audio
                        ref={audioRef}
                        controls
                        style={{ width: '100%', display: audioData ? 'block' : 'none' }}
                        onPlay={() => setIsPlaying(true)}
                        onPause={() => setIsPlaying(false)}
                        onTimeUpdate={handleTimeUpdate}
                    />
                </div>
            </div>
        </div>
    );
}

export default App;
