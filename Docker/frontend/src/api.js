import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const synthesizeAudio = async (text, voice_id = "en-US-Wavenet-D") => {
    try {
        const response = await api.post('/api/v1/synthesize', { text, voice_id });
        return response.data;
    } catch (error) {
        console.error("Error synthesizing audio:", error);
        throw error;
    }
};

export const fetchVoices = async () => {
    try {
        const response = await api.get('/api/v1/voices');
        return response.data;
    } catch (error) {
        console.error("Error fetching voices:", error);
        return [];
    }
};

export default api;
