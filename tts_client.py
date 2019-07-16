import os
import logging

from google.oauth2 import service_account
from google.cloud import texttospeech

from tools import change_voice

class TextToSpeechClient(object):
    def __init__(self, service_accout_file=None, language='en-US', gender="Male"):
        if service_accout_file is None:
            service_accout_file = os.path.expanduser('./credentials/Arcadeep.json')

        credentials = service_account.Credentials.from_service_account_file(service_accout_file)
        self._client = texttospeech.TextToSpeechClient(credentials=credentials)        
        self.tmp_wav = 'assets/tmp.wav'
        
        self.set_gender(gender)
        self.set_language(language)

    def _make_config(self):
        return texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16, speaking_rate=0.7)

    def tts_wave(self, text, language=None, gender=None):
        lang = self.language if language is None else language
        gen = self.gender if gender is None else self.str2gender(gender)
        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=lang,
            ssml_gender=gen) 
        
        audio_config = self._make_config()
        response = self._client.synthesize_speech(synthesis_input, voice, audio_config)

        with open(self.tmp_wav, 'wb') as out:
            out.write(response.audio_content)
        
        return self.tmp_wav  
            
    def str2gender(self, gender_str):
        return texttospeech.enums.SsmlVoiceGender.FEMALE if gender_str.lower()=='female' else texttospeech.enums.SsmlVoiceGender.MALE        

    def set_gender(self, gender):
        self.gender = texttospeech.enums.SsmlVoiceGender.FEMALE if gender.lower()=='female' else texttospeech.enums.SsmlVoiceGender.MALE
        
    def set_language(self, language):
        self.language = language
        