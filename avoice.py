import logging
from threading import Thread
import requests

from stt_client import CloudSpeechClient
# from aiy.voice.audio import play_wav

from tools import detect_intent_texts, change_voice, play_wav
from tts_client import TextToSpeechClient

import params
import wave

class ArcadeepVoice(Thread):

    def __init__(self, language='fr-FR', gender='Male'):
        Thread.__init__(self)
        self.client = CloudSpeechClient()
        self.client_speaker = TextToSpeechClient(language=language,gender=gender)
        
        self.last_sentence_heard = None
        self.is_running = False
        self.language = language
        
        self.arcade_url = 'http://{}:{}/'.format(params.IP_BORNE, params.PORT_COM)
        
        self.game = None
        self.mode = None
    
    def run(self):
        self.is_running = True
        while self.is_running:
            logging.info("#> Interaction with Arcadeep is running. ", self.is_running)
            request = self.listen()
            self.say(self.response(request))
            self.run_action()
    
    def stop(self):
        self.is_running = False
        
    def say(self, message, language=None, gender=None, shift=8):
        out_wav = 'assets/out.wav'        
        if message is not None:
            file_tmp = self.client_speaker.tts_wave(message, language=language, gender=gender)
            change_voice(file_tmp, out_wav, shift=shift)
            play_wav(out_wav)

    def response(self, request):
        response, infos = detect_intent_texts("arcadeep","unique",[request], self.language)
        self.check_action(infos['entities'])
        return response

    def check_action(self, entities):
        self.game = entities['Games'].string_value if entities['Games'].string_value !='' else self.game
        self.mode = entities['GameMode'].string_value if entities['GameMode'].string_value !='' else self.mode
        
    def run_action(self):
        if self.game is not None and self.mode is not None: 
            url_start_game = "{}runGame".format(self.arcade_url)
            requests.get(url_start_game, params={'game': self.game, 'mode': self.mode })
            self.game = None
            self.mode = None

    def listen(self):
        text = None
        while (text is None):
            text = self.client.recognize(language_code=self.language,
                                     hint_phrases=None)
        return text

''' 
class ArcadeepVoiceButton(ArcadeepVoice):
    
    def __init__(self, board, language='fr-FR', gender='Male'):
        ArcadeepVoice.__init__(self,language,gender)
        self.board = board
    
    def listen(self):
        aiy_tools.record_while_pushed(self.board, 'assets/request.wav')
        with open('assets/request.wav', 'rb') as fd:
            audio = fd.read()
            text = self.client.recognize_bytes(audio, language_code=self.language,
                                     hint_phrases=None)
            return text '''