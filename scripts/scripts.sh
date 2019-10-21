#!/bin/bash

#record continously
./stream-voice.sh &
#proses sound buat python
#if sound detected

#take picture then process repeat till n
	for value in {1..20}
	do
		python3 camera.py
		#image processing program
			#if true
				python3 ../servo/max-servo.py
	done

#else keep record


