#!/bin/bash

arecord --format=S16_LE --rate=16000 --file-type=raw ../sound/stream-voice.wav
