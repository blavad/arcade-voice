''' from aiy import board
import threading
import time

from aiy.board import Board, Led
from aiy.voice.audio import AudioFormat, play_wav, record_file, Recorder

def record_while_pushed(board, filename):
    board.button.wait_for_press()
    board.led.state = Led.ON    
    done = threading.Event()
    board.button.when_released = done.set
    def wait():
        start = time.monotonic()
        while not done.is_set():
            duration = time.monotonic() - start
            print('Recording: %.02f seconds [Press button to stop]' % duration)
            time.sleep(0.5)
    record_file(AudioFormat.CD, filename=filename, wait=wait, filetype='wav')
    board.led.state = Led.OFF    
    

def wait_to_be_activated(board):
    board.led.state = Led.ON
    board.button.wait_for_press()
    board.button.wait_for_release()
    board.led.state = Led.OFF '''