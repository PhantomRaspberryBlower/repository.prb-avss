#!/usr/bin/env python
 
# Encode message to Morse code and
# flash the led. 
 
import RPi.GPIO as GPIO
import time
 
TURN_ON = 1
TURN_OFF = 0
 
CODE = {' ': ' ',
        "'": '.----.',
        '(': '-.--.-',
        ')': '-.--.-',
        ',': '--..--',
        '-': '-....-',
        '.': '.-.-.-',
        '/': '-..-.',
        '0': '-----',
        '1': '.----',
        '2': '..---',
        '3': '...--',
        '4': '....-',
        '5': '.....',
        '6': '-....',
        '7': '--...',
        '8': '---..',
        '9': '----.',
        ':': '---...',
        ';': '-.-.-.',
        '?': '..--..',
        'A': '.-',
        'B': '-...',
        'C': '-.-.',
        'D': '-..',
        'E': '.',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
        '_': '..--.-'}
 
 
class MorseCode():
 
    def __init__(self, led_pin, speaker_pin=None, dot_length=0.2):
        self.LED_PIN = led_pin
        self.SPKR_PIN = speaker_pin
        self.DOT_LENGTH = dot_length
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        # Setup all the pins
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        if speaker_pin is not None:
            GPIO.setup(self.SPKR_PIN, GPIO.OUT)
 
    def _dot(self):
        GPIO.output(self.LED_PIN, TURN_ON)
        if self.SPKR_PIN:
            GPIO.output(self.SPKR_PIN, TURN_ON)
        time.sleep(self.DOT_LENGTH)
        GPIO.output(self.LED_PIN, TURN_OFF)
        if self.SPKR_PIN:
            GPIO.output(self.SPKR_PIN, TURN_OFF)
        time.sleep(self.DOT_LENGTH)
 
    def _dash(self):
        GPIO.output(self.LED_PIN, TURN_ON)
        if self.SPKR_PIN:
            GPIO.output(self.SPKR_PIN, TURN_ON)
        time.sleep(self.DOT_LENGTH * 3)
        GPIO.output(self.LED_PIN, TURN_OFF)
        if self.SPKR_PIN:
            GPIO.output(self.SPKR_PIN, TURN_OFF)
        time.sleep(self.DOT_LENGTH)
 
    def message(self, msg_txt):
        for letter in msg_txt:
            for symbol in CODE[letter.upper()]:
                if symbol == '-':
                    self._dash()
                elif symbol == '.':
                    self._dot()
                else:
                    time.sleep(self.DOT_LENGTH * 7)
 
# Check if running stand-alone or imported
if __name__ == '__main__':
    LED_PIN = 12
    SPKR_PIN = 36
    DOT_LENGTH = 0.2
    mc = MorseCode(LED_PIN, SPKR_PIN, DOT_LENGTH)
    try:
        while True:
            input = input('What message would you like to send? ')
            if input:
                mc.message(input)
            else:
                print('\nQuit')
                quit()
    except KeyboardInterrupt:
        print('\nQuit')
 
    # Tidy up and remaining connections.
    GPIO.cleanup()