import os
import re
import sys
import logging
from sys import platform

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account

from .microphone_streaming import RATE, CHUNK, MicrophoneStream

class CloudSpeechClient:
    def __init__(self, avoice, service_accout_file=None):
        if service_accout_file is None:
            service_accout_file = os.path.expanduser(
                '~/Arcadeep-credentials.json')

        credentials = service_account.Credentials.from_service_account_file(
            service_accout_file)
        self._client = speech.SpeechClient(credentials=credentials)
        self.avoice = avoice

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

    def listen_get_loop(self, responses):
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)
            
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting Dialog..')
                    if self.avoice.is_running:
                        self.avoice.stop()
                    break

                num_chars_printed = 0
                return transcript + overwrite_chars

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

            return self.listen_get_loop(responses)

        return None