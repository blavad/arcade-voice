import os
import dialogflow
import json

import numpy
from scipy.io.wavfile import read, write
from librosa_tools import normalize, write_wav

import logging

def detect_intent_texts(project_id, session_id, texts, language_code):
    if texts[0] is not None :
        logging.info('Input : {}'.format(texts))
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)
    
        for text in texts:
            text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
            query_input = dialogflow.types.QueryInput(text=text_input)
            response = session_client.detect_intent(session=session, query_input=query_input)
            entities = response.query_result.parameters.fields
            infos = {'entities': entities}
            return response.query_result.fulfillment_text, infos
        
def shift_sound(input_sound, offset):
    output_sound = numpy.roll(input_sound, offset)
    output_sound[0:offset] = 0
    return output_sound

def change_voice(file_name, file_name_output=None, shift=8):
    if file_name_output is None:
        file_name_output=file_name
    w = file_name
    a = read(w)
    sound = a[1]
    sample_rate = a[0]

    offset_sec = 0.01
    offset_step = int(offset_sec * sample_rate)
    input_sound = numpy.array(sound,dtype=float)
    shifted = numpy.sum([shift_sound(input_sound, i*offset_step) for i in range(shift)], axis=0)
    write_wav(file_name_output, shifted, sample_rate, norm=True)

