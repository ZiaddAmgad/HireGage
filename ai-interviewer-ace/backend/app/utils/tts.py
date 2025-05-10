from google.cloud import texttospeech

def text_to_opus_google(text: str, output_path: str = "output.opus"):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
    )

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # with open(output_path, "wb") as out:
    #     out.write(response.audio_content)
    return response.audio_content
