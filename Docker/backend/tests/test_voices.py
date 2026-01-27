from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("services.tts.get_tts_client")
def test_get_voices_filtering(mock_get_client):
    # Mock the TTS client and its response
    mock_client_instance = MagicMock()
    mock_get_client.return_value = mock_client_instance
    
    # Create mock voices
    voice_wavenet = MagicMock()
    voice_wavenet.name = "en-US-Wavenet-D"
    voice_wavenet.ssml_gender = 1
    voice_wavenet.language_codes = ["en-US"]

    voice_standard = MagicMock()
    voice_standard.name = "en-US-Standard-A"
    voice_standard.ssml_gender = 2
    voice_standard.language_codes = ["en-US"]

    voice_neural2 = MagicMock()
    voice_neural2.name = "en-US-Neural2-F"
    voice_neural2.ssml_gender = 2
    voice_neural2.language_codes = ["en-US"]

    voice_chirp = MagicMock()
    voice_chirp.name = "en-US-Chirp-A"
    voice_chirp.ssml_gender = 1
    voice_chirp.language_codes = ["en-US"]
    
    mock_response = MagicMock()
    # Return a mix of voices
    mock_response.voices = [voice_wavenet, voice_standard, voice_neural2, voice_chirp]
    
    mock_client_instance.list_voices.return_value = mock_response

    response = client.get("/api/v1/voices")
    assert response.status_code == 200
    data = response.json()
    
    # Verify filtering
    # Should contain Wavenet and Standard
    # Should NOT contain Neural2 or Chirp
    names = [v["name"] for v in data]
    assert "en-US-Wavenet-D" in names
    assert "en-US-Standard-A" in names
    assert "en-US-Neural2-F" not in names
    assert "en-US-Chirp-A" not in names
    
    assert len(data) == 2
