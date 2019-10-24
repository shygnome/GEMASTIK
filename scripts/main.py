#!bin/usr/python3

import logging
import random
import requests
import threading
import time

import numpy as np
import pyaudio
import wave

from picamera import PiCamera

DASHBOARD_URL = "https://pareto-iot.herokuapp.com/dashboard/"
COUNTDOWN_URL = DASHBOARD_URL + "change/stop/"

DEFAULT_COUNTDOWN = 60

def krl_arrive_routine(secs=60):
    routines = [lower_palang, start_countdown, play_announcer]
    args = [(), (secs,), (secs,)]

    logging.info("KRL_ARR : start multi thread")
    for i in range(len(routines)):
        tx = threading.Thread(target=routines[i], args=args[i])
        tx.start()
    
    logging.info("KRL_ARR : waiting for thread")
    
    for i in range(len(routines)):
        tx.join()
    
    global onRail
    onRail = False

def lower_palang():
    logging.info("Palang  : start lowering palang")
    time.sleep(5)
    logging.info("Palang  : finished lowering palang")

def raise_palang():
    logging.info("Palang  : start raising palang")
    time.sleep(5)
    logging.info("Palang  : finished raising palang")

def start_countdown(secs):
    logging.info("CntDwn  : starting GET request")
    r = requests.get(url=COUNTDOWN_URL+str(secs))
    logging.info("CntDwn  : finishing GET request with status code "+ str(r.status_code))

def play_announcer(secs):
    logging.info("Speaker : starting announcer")

    #define stream chunk   
    CHUNK = 512

    #open a wav format music  
    f = wave.open(r"/home/pi/Documents/GEMASTIK/sound/rekaman-1.wav","rb")  
    #instantiate PyAudio
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    
    for i in range(secs//5):
        #read data  
        data = f.readframes(CHUNK)  

        #play stream  
        while data:  
            stream.write(data)  
            data = f.readframes(CHUNK)  
        
        f = wave.open(r"/home/pi/Documents/GEMASTIK/sound/rekaman-1.wav","rb")

    #stop stream  
    stream.stop_stream()  
    stream.close()  

    #close PyAudio  
    p.terminate()

    logging.info("Speaker : exiting announcer")

def alarm_incoming_krl():
    logging.info("Comm    : start alarming")
    logging.info("Comm    : KERETA DATANG")
    logging.info("Comm    : finished alarming")

def recognize_sound(frame, rate):
    logging.info("RECSOUND: Calculating distance")
    return len(calculate_distance(rate, frame)) >= 2

def calculate_distance(fs, data):
    #The minimun value for the sound to be recognized as a knock
    min_val = 10000

    data_size = len(data)
    
    #The number of indexes on 0.15 seconds
    focus_size = int(0.2 * fs)
    
    focuses = []
    distances = []
    idx = 0
    
    while idx < len(data):
        if data[idx] > min_val:
            mean_idx = idx + focus_size // 2
            focuses.append(float(mean_idx) / data_size)
            if len(focuses) > 1:
                last_focus = focuses[-2]
                actual_focus = focuses[-1]
                distances.append(actual_focus - last_focus)
            idx += focus_size
        else:
            idx += 1
    return distances

def main():
    logging.info("Main    : Start PARETO Main routine")
    logging.info("Main    : Set up configuration")
    
    ## Audio
    # FORMAT = pyaudio.paInt16
    CHUNK = 512
    RATE = 44100
    FRAMERATE = RATE // CHUNK
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,rate=RATE,channels=1, input_device_index = 2, input=True, frames_per_buffer=CHUNK)

    ## Camera
    camera = PiCamera()
    camera.rotation = 270

    ## Dummy
    i = 0
    global onRail
    time.sleep(2)

    logging.info("Main    : Set up finished")

    ##
    logging.info("Main    : Start SUPERVISION routine")

    record_frame = []
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data = np.fromstring(data, dtype=np.int16)
        record_frame.append(data)
        i += 1

        if i % FRAMERATE == 0:
            audio_frame = np.concatenate(record_frame)
            
            ## audio routine
            if not onRail and recognize_sound(audio_frame, RATE):
                logging.info("Main    : Starting KRL arrive routine")
                krl_arrive_routine(DEFAULT_COUNTDOWN + random.randint(-5, 5))
                logging.info("Main    : Exiting KRL arrive routine")
            i = 0
            record_frame = []
    
    ##
    logging.info("Main    : Exiting Main routine")


if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    onRail = False
    main()
