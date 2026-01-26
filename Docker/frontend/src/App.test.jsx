import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from './App';
import * as api from './api';

// Mock the API module
vi.mock('./api');

describe('App Component', () => {
    it('renders title', () => {
        render(<App />);
        expect(screen.getByText('Web Reader')).toBeInTheDocument();
    });

    it('allows entering text', () => {
        render(<App />);
        const textarea = screen.getByPlaceholderText('Paste your text here...');
        fireEvent.change(textarea, { target: { value: 'Hello World' } });
        expect(textarea.value).toBe('Hello World');
    });

    it('synthesizes audio when button clicked', async () => {
        // Mock the response
        api.synthesizeAudio.mockResolvedValueOnce({
            audio_base64: 'fakeaudio',
            timepoints: []
        });

        render(<App />);
        const textarea = screen.getByPlaceholderText('Paste your text here...');
        fireEvent.change(textarea, { target: { value: 'Hello World' } });

        // Check loading button isn't disabled
        const button = screen.getByText('Listen');
        fireEvent.click(button);

        // Should call API
        expect(api.synthesizeAudio).toHaveBeenCalledTimes(1);
        expect(api.synthesizeAudio).toHaveBeenCalledWith('Hello World');
    });
});
