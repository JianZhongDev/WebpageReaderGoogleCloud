import pytest
from services.tts import detect_language, map_language_to_voice

def test_detect_language_english():
    text = "Hello world, this is a test."
    assert detect_language(text) == "en"

def test_detect_language_chinese():
    text = "你好，世界。"
    # langdetect might return zh-cn or zh-tw or just zh
    lang = detect_language(text)
    assert lang in ["zh-cn", "zh-tw", "zh"]

def test_detect_language_french():
    text = "Bonjour le monde."
    assert detect_language(text) == "fr"

def test_map_language_to_voice_exact_match():
    voices = [
        {"name": "en-US-Wavenet-D", "language_codes": ["en-US"]},
        {"name": "fr-FR-Wavenet-A", "language_codes": ["fr-FR"]},
    ]
    
    assert map_language_to_voice("en", voices) == "en-US-Wavenet-D"
    assert map_language_to_voice("fr", voices) == "fr-FR-Wavenet-A"

def test_map_language_to_voice_fallback():
    voices = [
        {"name": "en-US-Wavenet-D", "language_codes": ["en-US"]},
    ]
    # 'de' is not in voices, so fallback logic might kick in or return None.
    # Our logic returns None if no match.
    assert map_language_to_voice("de", voices) is None

def test_map_language_to_voice_prefix_match():
    voices = [
        {"name": "nl-NL-Wavenet-A", "language_codes": ["nl-NL"]},
    ]
    # 'nl' should match 'nl-NL'
    assert map_language_to_voice("nl", voices) == "nl-NL-Wavenet-A"
