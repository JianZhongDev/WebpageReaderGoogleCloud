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

    words = None
    if "cmn" in voice_id:
        split_puncts = ["。", "？", "！", ".", "!", "?", "：", ":", "；", ";", "、", ",", "，"] 
        sentences = []
        current_sentence = ""
        for char in text:
            current_sentence += char
            if char in split_puncts:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        sentences.append(current_sentence.strip())
        words = sentences
    else:
        words = text.split()

    if words is None:
        raise Exception("Failed to tokenize text for TTS.")
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

    print(ssml_text)

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
    

    print(processed_timepoints)

    disp_world_list = words

    return {
        "disp_world_list": disp_world_list,
        "audio_base64": encoded_audio,
        "timepoints": processed_timepoints,
        "audio_format": "wav" # helpful for frontend
    }

async def list_voices(language_code: str = None) -> List[Dict[str, Any]]:
    """
    Lists the available voices. 
    If language_code is provided, filters by that language.
    Otherwise returns all available Wavenet and Standard voices.
    """
    client = get_tts_client()
    if not client:
        raise Exception("Google Cloud TTS Client not initialized.")

    # Call list_voices with no arguments to get all voices if language_code is None
    # Or pass language_code if it's provided (though user wants all languages now effectively)
    response = client.list_voices(language_code=language_code) if language_code else client.list_voices()
    
    voices = []
    for voice in response.voices:
        # Filter for Wavenet and Standard voices only
        # User requested "only within in the wavenet support" and "standard voice type"
        # Exclude "Neural2", "Studio", "Chirp", "Journey" (unless they fall under Standard/Wavenet naming?)
        # Usually names are like "en-US-Wavenet-A" or "en-US-Standard-A"
        # We will strictly look for "Wavenet" or "Standard" in the name.
        if "Wavenet" in voice.name or "Standard" in voice.name:
            voices.append({
                "name": voice.name,
                "ssml_gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                "language_codes": list(voice.language_codes)
            })
    
    # Sort for UI consistency
    voices.sort(key=lambda x: x["name"])
    return voices
