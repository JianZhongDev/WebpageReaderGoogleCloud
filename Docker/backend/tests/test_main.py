import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

# Mock services
@pytest.fixture
def mock_tts(mocker):
    # Patching the function reference in main.py because it's imported via 'from ... import ...'
    return mocker.patch("main.synthesize_text", new_callable=AsyncMock)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Web Reader API is running"}

@pytest.mark.asyncio
async def test_synthesize_audio_success(mock_tts):
    mock_tts.return_value = {
        "audio_base64": "fakeaudioblob",
        "timepoints": []
    }
    
    response = client.post("/api/v1/synthesize", json={"text": "Hello", "voice_id": "en-US-Wavenet-D"})
    assert response.status_code == 200
    assert response.json()["audio_base64"] == "fakeaudioblob"
    mock_tts.assert_called_once_with("Hello", "en-US-Wavenet-D")
