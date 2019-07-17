import os
import logging
from sys import platform

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account

from .microphone_streaming import RATE, CHUNK, MicrophoneStream

class CloudSpeechClient:
    def __init__(self, service_accout_file=None):
        if service_accout_file is None:
            service_accout_file = os.path.expanduser(
                '~/Arcadeep-credentials.json')

        credentials = service_account.Credentials.from_service_account_file(
            service_accout_file)
        self._client = speech.SpeechClient(credentials=credentials)

    def _make_config(self, language_code):
        return speech.types.RecognitionConfig(
            encoding=speech.types.RecognitionConfig.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)

    def recognize_bytes(self, data, language_code='en-US'):
        """Data must be encoded according to the AUDIO_FORMAT."""
        streaming_config = speech.types.StreamingRecognitionConfig(
            config=self._make_config(language_code),
            single_utterance=True)
        responses = self._client.streaming_recognize(
            config=streaming_config,
            requests=[speech.types.StreamingRecognizeRequest(audio_content=data)])

        for response in responses:
            for result in response.results:
                if result.is_final:
                    return result.alternatives[0].transcript

        return None

    def recognize(self, language_code='fr-FR'):
        streaming_config = speech.types.StreamingRecognitionConfig(
            config=self._make_config(language_code),
            interim_results=True)
        
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
            responses = self._client.streaming_recognize(
                config=streaming_config, requests=requests)

            for response in responses:
                for result in response.results:
                    if result.is_final:
                        return result.alternatives[0].transcript

        return None