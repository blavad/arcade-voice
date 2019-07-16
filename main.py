import logging
from flask import Flask

from avoice import ArcadeepVoice
from app import VoiceApp

import aiy_tools
    
logging.basicConfig(level=logging.DEBUG)

app = VoiceApp(__name__, ArcadeepVoice())
    
if __name__ == '__main__':
    app.run()