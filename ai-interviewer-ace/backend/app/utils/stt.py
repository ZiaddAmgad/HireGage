from google.cloud import speech


def speech_to_text_google(audio_bytes: bytes) -> str:
    # Initialize the Google Cloud Speech client
    client = speech.SpeechClient()

    # Load the audio bytes
    audio = speech.RecognitionAudio(content=audio_bytes)

    # Set up the configuration for the recognition request
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Modify if using other formats
        sample_rate_hertz=16000,  # Adjust to match the sample rate of your audio
        language_code="en-US",  # Specify language
    )

    # Perform speech recognition
    response = client.recognize(config=config, audio=audio)

    # Extract the recognized text from the response
    for result in response.results:
        return result.alternatives[0].transcript