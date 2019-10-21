import imutils
import cv2
import matplotlib.pyplot as plt
import numpy as np
import pyaudio

from picamera import PiCamera
from time import sleep

def take_pic(camera):
    for i in range(5):
        camera.capture('../img/pic-'+str(i)+'.jpg')
        sleep(0.2)

def load_template(filename):
    #Open template and get canny
    template = '../img/' + filename
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
    min_thresh = 0.011
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
    #Get information from temp_found to cqompute x,y coordinate
    if val_max > min_thresh:
        print(val_max)
        (_, loc_max, r) = temp_found
        (x_start, y_start) = (int(loc_max[0] * r), int(loc_max[1] * r))
        (x_end, y_end) = (int((loc_max[0] + width) * r), int((loc_max[1] + height) * r))
        #Draw rectangle around the template
        result = cv2.rectangle(main_image, (x_start, y_start), (x_end, y_end), (153, 22, 0), 5)
    else:
        result = image
    return val_max > min_thresh, val_max, result

def img_routine():
    template = load_template('template.png')
    summary = 0
    for i in range(5):
        img = cv2.imread('../img/pic-'+str(i)+'.jpg')
        res, val_max, res_img = template_match(template, img)
        print(res, val_max)
        cv2.imwrite('../img/pic-'+'recognized-'+str(i)+'.png', res_img)
        summary += int(res)
    return summary

def audio_routine():
    #The following code comes from markjay4k as referenced below

    chunk=4096
    RATE=44100

    p=pyaudio.PyAudio()

    #input stream setup
    stream=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, input_device_index = 2, input=True, frames_per_buffer=chunk)

    # #the code below is from the pyAudio library documentation referenced below
    # #output stream setup
    # player=p.open(format = pyaudio.paInt16,rate=RATE,channels=1, output=True, frames_per_buffer=chunk)


    plt.ion() # Stop matplotlib windows from blocking

    # Setup figure, axis and initiate plot
    fig, ax = plt.subplots()
    xdata, ydata = [], []
    ln, = ax.plot([], [], 'ro-')

    while True:            #Used to continuously stream audio
        
        data=np.fromstring(stream.read(chunk,exception_on_overflow = False),dtype=np.int16)
        # print(data.shape)

        data = data * np.hanning(len(data)) # smooth the FFT by windowing data
        fft = abs(np.fft.fft(data).real)
        fft = fft[:int(len(fft)/2)] # keep only first half
        freq = np.fft.fftfreq(chunk,1.0/RATE)
        freq = freq[:int(len(freq)/2)] # keep only first half
        freqPeak = freq[np.where(fft==np.max(fft))[0][0]]+1
        print("peak frequency: %d Hz"%freqPeak)

        # uncomment this if you want to see what the freq vs FFT looks like
        plt.plot(freq,fft)
        plt.axis([0,4000,None,None])
        plt.show()
        plt.close()
        
        # player.write(data,chunk)
        
    #closes streams
    stream.stop_stream()
    stream.close()
    p.terminate

camera = PiCamera()
camera.rotation = 270
# take_pic(camera)
# img_routine()
audio_routine()
