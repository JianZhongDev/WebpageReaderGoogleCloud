import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from './App';
import * as api from './api';

// Mock the API module
vi.mock('./api');

// Mock HTMLMediaElement.prototype.play
window.HTMLMediaElement.prototype.play = vi.fn(() => Promise.resolve());


describe('App Component', () => {
    it('renders title', () => {
        render(<App />);
        expect(screen.getByText('Web Reader')).toBeInTheDocument();
    });

    it('synthesizes audio and renders words', async () => {
        // Mock the response
        api.synthesizeAudio.mockResolvedValueOnce({
            audio_base64: 'fakeaudio',
            timepoints: [
                { mark_name: "0", time_seconds: 0.1 },
                { mark_name: "1", time_seconds: 0.5 }
            ]
        });

        render(<App />);
        const textarea = screen.getByPlaceholderText('Paste your text here...');
        fireEvent.change(textarea, { target: { value: 'Hello World' } });

        const button = screen.getByText('Listen');
        fireEvent.click(button);

        // Wait for API call and rendering
        await waitFor(() => {
            expect(screen.getByText('Hello')).toBeInTheDocument();
            expect(screen.getByText('World')).toBeInTheDocument();
        });
    });
});
