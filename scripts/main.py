#!bin/usr/python3

import logging
import threading
import time

# from picamera import PiCamera


def krl_arrive_routine(record_frame, secs=30):
    routines = [lower_palang, start_countdown, play_announcer]

    print(record_frame)

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
    FRAMERATE = RATE // CHUNK
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

    record_frame = []
    while True:
        # data = stream.read(CHUNK, exception_on_overflow=True)
        # record_frame.append(data)
        record_frame.append(i)
        i += 1
        

        if i % FRAMERATE == 0:
            krl_arrive_routine(record_frame)
            i = 0
            record_frame = []
    
    ##
    logging.info("Main    : Exiting Main routine")


if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    main()
