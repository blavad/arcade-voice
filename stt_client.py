import os
import logging
from sys import platform

from google.cloud import speech
from google.oauth2 import service_account

from recorder import Recorder, AudioFormat

END_OF_SINGLE_UTTERANCE = speech.types.StreamingRecognizeResponse.END_OF_SINGLE_UTTERANCE
AUDIO_SAMPLE_RATE_HZ = 16000
AUDIO_FORMAT = AudioFormat(sample_rate_hz=AUDIO_SAMPLE_RATE_HZ,
                           num_channels=1,
                           bytes_per_sample=2)

logger = logging.getLogger(__name__)


class CloudSpeechClient:
    def __init__(self, service_accout_file=None):
        if service_accout_file is None:
            service_accout_file = os.path.expanduser(
                './credentials/Arcadeep.json')

        credentials = service_account.Credentials.from_service_account_file(
            service_accout_file)
        self._client = speech.SpeechClient(credentials=credentials)

    def _make_config(self, language_code, hint_phrases):
        return speech.types.RecognitionConfig(
            encoding=speech.types.RecognitionConfig.LINEAR16,
            sample_rate_hertz=AUDIO_SAMPLE_RATE_HZ,
            language_code=language_code,
            speech_contexts=[speech.types.SpeechContext(phrases=hint_phrases)])

    def recognize_bytes(self, data, language_code='en-US', hint_phrases=None):
        """Data must be encoded according to the AUDIO_FORMAT."""
        streaming_config = speech.types.StreamingRecognitionConfig(
            config=self._make_config(language_code, hint_phrases),
            single_utterance=True)
        responses = self._client.streaming_recognize(
            config=streaming_config,
            requests=[speech.types.StreamingRecognizeRequest(audio_content=data)])

        for response in responses:
            for result in response.results:
                if result.is_final:
                    return result.alternatives[0].transcript

        return None

    def recognize(self, language_code='en-US', hint_phrases=None):
        streaming_config = speech.types.StreamingRecognitionConfig(
            config=self._make_config(language_code, hint_phrases),
            single_utterance=True)

        with Recorder() as recorder:
            if platform == "linux" or platform == "linux2":
                chunks = recorder.record(AUDIO_FORMAT,
                                         chunk_duration_sec=0.1,
                                         on_start=self.start_listening,
                                         on_stop=self.stop_listening)
            elif platform == "darwin":
                chunks = recorder.record(AUDIO_FORMAT,
                                         chunk_duration_sec=0.1,
                                         filename='test.wav',
                                         on_start=self.start_listening,
                                         on_stop=self.stop_listening)#reSpeakerRecord()

            requests = (speech.types.StreamingRecognizeRequest(
                audio_content=data) for data in chunks)
            responses = self._client.streaming_recognize(
                config=streaming_config, requests=requests)

            for response in responses:
                if response.speech_event_type == END_OF_SINGLE_UTTERANCE:
                    recorder.done()

                for result in response.results:
                    if result.is_final:
                        return result.alternatives[0].transcript

        return None

    def start_listening(self):
        logger.info('Start listening.')

    def stop_listening(self):
        logger.info('Stop listening.')
