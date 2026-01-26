import base64
import html
from typing import List, Dict, Any
import base64
import html
from typing import List, Dict, Any
from google.cloud import texttospeech_v1beta1 as texttospeech

# Global client to reuse connection if possible
_client = None

def get_tts_client():
    global _client
    if _client is None:
        try:
             _client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Warning: Could not initialize TTS client: {e}")
            return None
    return _client

async def synthesize_text(text: str, voice_id: str = "en-US-Wavenet-D") -> Dict[str, Any]:
    """
    Synthesizes text to speech using Google Cloud TTS with SSML for timepoints.
    Returns base64 encoded audio (WAV) and a list of timepoints.
    """
    client = get_tts_client()
    if not client:
        raise Exception("Google Cloud TTS Client not initialized. Check credentials.")

    # 1. Tokenize text (simple split by whitespace)
    # matching what we expect the frontend to do
    words = text.split()
    
    # 2. Build SSML with marks
    # <speak> word <mark name="0"/> word <mark name="1"/> ... </speak>
    # Note: We place the mark AFTER the word to know when it ENDS? 
    # Or BEFORE to know when it STARTS? 
    # Usually highlighting starts when the word is spoken. So BEFORE.
    # <speak> <mark name="0"/> word <mark name="1"/> word ... </speak>
    
    ssml_parts = ["<speak>"]
    for i, word in enumerate(words):
        # Escape special XML characters in the word
        escaped_word = html.escape(word)
        ssml_parts.append(f'<mark name="{i}"/>{escaped_word}')
    ssml_parts.append("</speak>")
    
    ssml_text = " ".join(ssml_parts)

    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    # Build the voice request
    language_code = "-".join(voice_id.split("-")[:2])
    name = voice_id

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=name
    )

    # Select LINEAR16 (WAV) for timepoint support
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Perform the request
    response = client.synthesize_speech(
        request=texttospeech.SynthesizeSpeechRequest(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
            enable_time_pointing=[texttospeech.SynthesizeSpeechRequest.TimepointType.SSML_MARK]
        )
    )

    # Process Timepoints
    # response.timepoints contains list of Timepoint objects (time_seconds, mark_name)
    processed_timepoints = []
    for tp in response.timepoints:
        processed_timepoints.append({
            "mark_name": tp.mark_name,
            "time_seconds": tp.time_seconds
        })

    encoded_audio = base64.b64encode(response.audio_content).decode('utf-8')
    
    return {
        "audio_base64": encoded_audio,
        "timepoints": processed_timepoints,
        "audio_format": "wav" # helpful for frontend
    }
