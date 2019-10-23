#!bin/usr/python3

import logging
import threading
import time

# from picamera import PiCamera


def krl_arrive_routine(secs=30):
    routines = [lower_palang, start_countdown, play_announcer]

    print("Masuk pak eko")

def lower_palang():
    logging.info("Palang  : start lowering palang")
    time.sleep(5)
    logging.info("Palang  : finished lowering palang")

def raise_palang():
    logging.info("Palang  : start raising palang")
    time.sleep(5)
    logging.info("Palang  : finished raising palang")

def start_countdown():
    logging.info("CntDwn  : starting")
    time.sleep(3)
    logging.info("CntDwn  : finishing")

def play_announcer():
    logging.info("Speaker : starting")
    time.sleep(3)
    logging.info("Speaker : finishing")

def alarm_incoming_krl():
    logging.info("Comm    : start alarming")
    logging.info("Comm    : KERETA DATANG")
    logging.info("Comm    : finished alarming")

def supervise():
    pass

def main():
    logging.info("Main    : Start PARETO Main routine")
    logging.info("Main    : Set up configuration")
    
    ## Audio
    # FORMAT = pyaudio.paInt16
    CHUNK = 512
    RATE = 44100
    # p = pyaudio.PyAudio()
    # stream = p.open(format = pyaudio.paInt16,rate=RATE,channels=1, input_device_index = 2, input=True, frames_per_buffer=CHUNK)

    ## Camera
    # camera = PiCamera()
    # camera.rotation = 270

    ## Dummy
    i = 0
    onRail = False
    time.sleep(2)

    logging.info("Main    : Set up finished")

    ##
    logging.info("Main    : Start SUPERVISION routine")
    while True:
        time.sleep(0.5)
        i += 1

        if i % 30 == 0:
            krl_arrive_routine()
    
    ##
    logging.info("Main    : Exiting Main routine")


if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    main()
