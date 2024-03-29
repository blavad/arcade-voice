import numpy as np
from flask import Flask, request, render_template

from voice.avoice import ArcadeepVoice

class VoiceApp(Flask):

    def __init__(self, name, language='fr-FR', gender='Male', service_accout_file=None):
        Flask.__init__(self, name)
        self.arcadeep = arcadeep= ArcadeepVoice(language=language, gender=gender, service_accout_file=service_accout_file)
        self.tests_sample = []
        self.qr_sample = {}

        @self.route('/')
        def intro():
            return render_template('testSpeech.html', log_tests=self.tests_sample, responses=self.qr_sample)
        
        @self.route('/startDialog')
        def startDialog():        
            self.arcadeep.say('Bonjour')
            self.arcadeep.start()
            return 'Dialog start' 
        
        @self.route('/stopDialog')
        def stopDialog():        
            self.arcadeep.say('Au revoir')
            self.arcadeep.stop()
            return 'Dialog start'

        
        @self.route('/say', methods = ['POST', 'GET'])
        def say():
            self.say_request()            
            return 'Ok'    
        
        @self.route('/testSpeech', methods = ['POST', 'GET'])
        def testSpeech():
            self.say_request()
            return render_template('testSpeech.html', log_tests=self.tests_sample, responses=self.qr_sample)
        
        @self.route('/testReponse', methods = ['POST', 'GET'])
        def testResponse():
            if request.method == 'POST':
                if request.form['speech_r']:
                    speech = request.form['speech_r']
            else:
                if request.form['speech_r']:    
                    speech = request.args.get('speech_r')
            self.qr_sample[speech] = self.arcadeep.response(speech)
            self.arcadeep.say(self.qr_sample[speech])
            self.arcadeep.run_action()
            return render_template('testSpeech.html', log_tests=self.tests_sample, responses=self.qr_sample)
        
    def say_request(self):
        if request.method == 'POST':
            if request.form['speech']:
                speech = request.form['speech']
                gender = request.form['gender'] if request.form['gender'] else None
                language = request.form['language'] if request.form['language'] else None
                shift = request.form['shift'] if request.form['shift'] else 8
        else:
            if request.form['speech']:
                speech = request.args.get('speech') 
                gender = request.args.get('gender') if request.form['gender'] else None
                language = request.args.get('language') if request.form['language'] else None
                shift = request.args.get('shift') if request.form['shift'] else 8
        self.tests_sample= np.append(self.tests_sample, "Arcadeep ({} | {}) dit : {}".format(gender,language, speech))
        self.arcadeep.say(speech, gender=gender,language=language, shift=int(shift))
        