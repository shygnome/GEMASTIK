#!bin/usr/python3

import logging
import random
import requests
import threading
import time

import cv2
import imutils
import numpy as np
import pyaudio
import wave

from gpiozero import Servo
from picamera import PiCamera

# Dashboard URL
DASHBOARD_URL = "https://pareto-iot.herokuapp.com/dashboard/"
STOP_COUNTDOWN_URL = DASHBOARD_URL + "change/stop/"
ADA_COUNTDOWN_URL = DASHBOARD_URL + "change/ada/"
SAFE_COUNTDOWN_URL = DASHBOARD_URL + "change/safe/"

# Countdown
DEFAULT_COUNTDOWN = 30

# Camera
PATH_IMG = '../img/'
TEMPLATE_IMG = 'template.png'

# GPIO
#MY_GPIO = 4
#MY_SERVO = Servo(MY_GPIO)

def krl_arrive_routine(secs=60, stop):
    global onRail
    onRail = True
    
    routines = [lower_palang, start_countdown, play_announcer]
    args = [(), (secs,), (secs-15,)]

    logging.info("KRL_ARR : start multi thread")
    for i in range(len(routines)):
        tx = threading.Thread(target=routines[i], args=args[i])
        tx.start()
    
    logging.info("KRL_ARR : waiting for thread")
    
    for i in range(len(routines)):
        if stop():
            break
        tx.join()
    
    onRail = False

def krl_passby_routine(secs=60):
    # onRail
    global stopArrive
    global onRail
    onRail = False
    stopArrive = False

    routines = [raise_palang, stop_countdown]
    args = [(), (0,)]

    logging.info("KRL_PASS: start multi thread")
    for i in range(len(routines)):
        tx = threading.Thread(target=routines[i], args=args[i])
        tx.start()
    
    logging.info("KRL_PASS: waiting for thread")
    
    for i in range(len(routines)):
        tx.join()
    
    r = requests.get(url=SAFE_COUNTDOWN_URL+str(0))

def lower_palang():
    logging.info("Palang  : start lowering palang")
    servo = Servo(4)
    servo.min()
    time.sleep(1)
    logging.info("Palang  : finished lowering palang")

def raise_palang():
    logging.info("Palang  : start raising palang")
    servo = Servo(4)
    servo.max()
    time.sleep(1)
    logging.info("Palang  : finished raising palang")

def start_countdown(secs):
    logging.info("CntDwn  : starting GET request")
    r = requests.get(url=STOP_COUNTDOWN_URL+str(secs))
    logging.info("CntDwn  : finishing GET request with status code "+ str(r.status_code))

def stop_countdown(secs):
    logging.info("CntDwn  : starting GET request")
    r = requests.get(url=ADA_COUNTDOWN_URL+str(0))
    logging.info("CntDwn  : finishing GET request with status code "+ str(r.status_code))

def play_announcer(secs):
    global onRail

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
        if (not onRail):
            break
        
        f = wave.open(r"/home/pi/Documents/GEMASTIK/sound/rekaman-{0}.wav".format((i % 4)),"rb")

        #read data  
        data = f.readframes(CHUNK)  

        #play stream  
        while data:  
            stream.write(data)  
            data = f.readframes(CHUNK)  

    #stop stream  
    stream.stop_stream()  
    stream.close()  

    #close PyAudio  
    p.terminate()

    logging.info("Speaker : exiting announcer")


def take_pic(camera):
    for i in range(5):
        camera.capture(PATH_IMG+'pic-'+str(i)+'.jpg')

def load_template(filename):
    #Open template and get canny
    template = PATH_IMG + filename
    template = cv2.imread(template)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 10, 25)
    return template

def template_match(template, image):
    (height, width) = template.shape[:2]
    #open the main image and convert it to gray scale image
    main_image = image
    gray_image = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
    temp_found = None
    min_thresh = 0.015
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        #resize the image and store the ratio
        resized_img = imutils.resize(gray_image, width = int(gray_image.shape[1] * scale))
        ratio = gray_image.shape[1] / float(resized_img.shape[1])
        if resized_img.shape[0] < height or resized_img.shape[1] < width:
            break
        #Convert to edged image for checking
        e = cv2.Canny(resized_img, 10, 25)
        match = cv2.matchTemplate(e, template, cv2.TM_CCOEFF_NORMED)
        (val_min, val_max, _, loc_max) = cv2.minMaxLoc(match)
        if temp_found is None or val_max>temp_found[0]:
            temp_found = (val_max, loc_max, ratio)
    return val_max > min_thresh, val_max

def img_routine():
    template = load_template(TEMPLATE_IMG)
    summary = 0
    for i in range(5):
        img = cv2.imread(PATH_IMG+'pic-'+str(i)+'.jpg')
        res, val_max = template_match(template, img)
        print(res, val_max)
        summary += int(res)
    return summary
    
def recognize_image(thread):
    logging.info("RECIMAGE: Take pictures")
    global cameraOnUse
    cameraOnUse = True

    ## Camera
    camera = PiCamera()
    camera.rotation = 270

    take_pic(camera)
    if img_routine() >= 2:
        logging.info("RECIMAGE: Kereta recognized")
        thread.start()
    logging.info("RECIMAGE: Exiting RECIMAGE")

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

    ## Dummy
    i = 0
    global stopArrive
    global onRail
    global cameraOnUse
    cnt_dwn = DEFAULT_COUNTDOWN + random.randint(-5, 5)
    arrive_routine = threading.Thread(target=krl_arrive_routine, args=(cnt_dwn, stopArrive))
    passingby_routine = threading.Thread(target=krl_passby_routine, args=(0, ))
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

            ## camera routine
            if onRail and not cameraOnUse:
                camera_t = threading.Thread(target=recognize_image, args=(passingby_routine,))
                camera_t.start()

            ## audio routine
            if not onRail and recognize_sound(audio_frame, RATE):
                logging.info("Main    : Starting KRL arrive routine")
                arrive_routine.start()
                logging.info("Main    : Exiting KRL arrive routine")
            elif onRail and not recognize_sound(audio_frame, RATE):
                logging.info("Main    : Starting KRL passing by routine")
                passingby_routine.start()
                logging.info("Main    : Exiting KRL passing by routine")
            i = 0
            record_frame = []
    
    ##
    logging.info("Main    : Exiting Main routine")


if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    stopArrive = False
    onRail = False
    cameraOnUse = False
    main()
