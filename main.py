import logging

from voiceapp import VoiceApp
    
logging.basicConfig(level=logging.DEBUG)

app = VoiceApp(__name__)
    
if __name__ == '__main__':
    app.run()