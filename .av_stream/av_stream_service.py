#!/usr/bin/env python

# Stream video & audio to facebook or broadcast via udp on port 4569.
# Headless installation on RPi 4. Fitted an LED, switch and speaker to
# the GPIO pins for user inputs.
# Press the switch to start streaming; the LED flashes 3 times then lights
# up when connected and stream begins. If the LED repeatedly blinks this 
# indicates an error occurred.
# Press the switch again to stop the stream. To shutdown the RPi press
# and hold the switch for more than 3 seconds the LED flashes 3 times
# before the shutdown process begins.

# Written by Phantom Raspberry Blower
# Date: 21-04-2021

# Import dependencies
import RPi.GPIO as GPIO
import subprocess
import threading
import time
import os
import atexit
import socket
import logging
#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
#os.putenv('SDL_AUDIODRIVER', 'alsa')
import pygame
from datetime import date, datetime, timedelta
from resources.lib import commontasks
from resources.lib.systeminfo import SystemInfo
from resources.lib.morsecode import MorseCode

si = SystemInfo()
settings_dict = {}
metadata_year = ''

WORK_DIR = os.path.abspath(os.path.dirname(__file__))
MEDIA_DIR = WORK_DIR + '/resources/media'

loggin.basicConfig(filename=WORK_DIR + '/avss.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s')

def get_settings():
    global settings_dict
    global metadata_year
    settings_dict = commontasks.get_settings(WORK_DIR + '/config.ini')
    if settings_dict['metadata_year'] == 'current year':
        metadata_year = date.today().year

get_settings()

# Setup GPIO (general purpose input output)
LED_PIN = int(settings_dict['gpio_led_pin'])         # Default led pin 12
SWITCH_PIN = int(settings_dict['gpio_switch_pin'])   # Default swtich pin 18
SPKR_PIN = int(settings_dict['gpio_spkr_pin'])       # Default speaker pin 36
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.setup(SWITCH_PIN, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(SPKR_PIN, GPIO.OUT)
GPIO.output(SPKR_PIN, GPIO.LOW)

# Setup global variables
previous_state = False
current_state = False
toggle_switch = False
all_processes = []

# Setup morse code notifications
if settings_dict['enable_speaker'] == 'True':
    m_speaker = SPKR_PIN
else:
    m_speaker = None
mc = MorseCode(LED_PIN, m_speaker, 0.4)

settings_proc = None
settings_status = None


def check_for_updates():
    global settings_dict
    date_format = "%d/%m/%Y"
    last_updated = settings_dict['last_updated']
    update_interval_days = int(settings_dict['update_interval_days'])
    a = datetime.strptime(last_updated, date_format) + timedelta(days=update_interval_days)
    b = datetime.today()
    delta = b - a
    if a < b:
        logging.info('Checking for updates')
        play_sound("checking_for_updates.mp3")
        response = os.popen('python updateWorker.py').read()
        if settings_dict['update_os'] == 'True':
            os.popen('sudo apt-get update')
        if settings_dict['upgrade_os'] == 'True':
            os.popen('sudo apt-get upgrade')
        settings_dict.update({'last_updated':
                              date.today().strftime('%d/%m/%Y')})
        commontasks.save_settings(settings_dict, WORK_DIR + '/config.ini')


def cleanup():
    # Cleanup all processes
    timeout_sec = 5
    # Iterate currently running processes
    for p in all_processes: 
        p_sec = 0
        for second in range(timeout_sec):
            if p.poll() == None:
                time.sleep(1)
                p_sec += 1
        if p_sec >= timeout_sec:
            p.kill()
    GPIO.cleanup()


def kill_settings():
    global settings_status
    global settings_proc
    if settings_status == None:
        subprocess.Popen.terminate(settings_proc)
        settings_status = subprocess.Popen.poll(settings_proc)


def kill_streams(processes=None):
    # Kill all currently running audio & video stream processes
    if processes == None:
        processes = ['raspivid', 'ffmpeg']
    # List running processes
    subproc = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    output, error = subproc.communicate()
    # Interate audio & video streams to kill
    for process_name in processes:
        target_process = process_name
        # Iterate running processes
        for line in output.splitlines():
            # Compare running process name with audio & video stream to kill
            if target_process in str(line):
                # Discover the process id
                pid = int(line.split(None, 1)[0])
                # Kill the current process
                os.kill(pid, 9)


def notification(interval=0.3, mode=None):
    # Create audible sound (morse code) to confirm chosen option
    # 'v' = start_video; 'e' = end_video; 's' = shutdown
    if mode != None:
        mc.message(mode)


def play_sound(soundfile):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(MEDIA_DIR + '/' + soundfile)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue
    except:
        print("ERROR - sound card not present!")


def push_button(channel):
    global current_state
    current_state = GPIO.input(SWITCH_PIN)
    start_time=time.time()
    diff=0
    hold_time = 3

    while GPIO.input(SWITCH_PIN) and (diff < hold_time):
        now_time=time.time()
        diff=-start_time+now_time

    if (diff >= hold_time):
        shutdown()
    else:
        start_stop_stream()


def shutdown():
    # Shutdown the RPi
    # Speak through the headphone socket
    t = threading.Thread(target=play_sound, args=("shutting_down.mp3",))
    t.start()
    # Flash the LED three times to indicate shutdown
    notification(interval=0.4, mode='s')
    # output shutdown message
    logging.info('Shutting down')
    print('Shutting down ...')
    # Shutdown now
    os.system('sudo shutdown -h now')


def speak(msg=None):
    if msg:
      full_speech = "echo '" + msg + "' | festival --tts"
      os.popen(full_speech)


def speak_ip():
    ip = os.popen("hostname -I | sed -e 's/\./ dot /g' -e 's/[0123456789]/ & /g'")
    speech = 'Hello this is raspberry pi and my I P address is %s' % ip.read()
    full_speech = "echo '" + speech + "' | festival --tts"
    os.popen(full_speech)


def start_settings_webpage():
    global settings_proc
    global settings_status
    settings_proc = subprocess.Popen(['python3', WORK_DIR + '/av_stream_settings.py'])
    settings_status = subprocess.Popen.poll(settings_proc)


def start_stop_stream():
    global previous_state
    global toggle_switch
    global current_state

    if current_state != previous_state and current_state == True:
        if toggle_switch == True:
            # Stop the audio & video stream
            toggle_switch = False
            stop_stream()
        else:
            #Start the audio & video stream
            toggle_switch = True
            start_stream()
        previous_state = True
    else:
        previous_state = current_state


def start_stream():
    # Speak through the headphone socket
    t = threading.Thread(target=play_sound, args=("starting_stream.mp3",))
    t.start()
    logging.info('Starting audio video stream')
    print('Starting audio video stream ... ', end = '')
    get_settings()
    url = ''
    audio_offset = ''
    video_offset = ''
    port_or_key = ''
    overlay_text = ''

    if settings_dict['itsoffset'] == 'audio':
        settings_dict['audio_offset'] = '-itsoffset %s ' % settings_dict['itsoffset_seconds']
        settings_dict['video_offset'] = '-itsoffset %s ' % settings_dict['itsoffset_seconds']

    if settings_dict['startup_udp'] == 'True':
        url = settings_dict['broadcast_url']
        port_or_key = ':' + settings_dict['broadcast_port']
        stream_codec = 'mpegts'
    else:
        url = settings_dict['facebook_url']
        stream_codec = settings_dict['video_out_codec']
    
    kill_settings()

    if len(settings_dict['video_out_overlay_text']) > 0:
        overlay_text = settings_dict['video_out_overlay_text'].replace('~','%') + ' '
    cmd = ('raspivid '
           '-t 0 '
           '%s'
           '-g %s '
           '-roi 0,0,0.998,1 '
           '-o - '
           '-w %s '
           '-h %s '
           '-fps %s '
           '-b %s '
           '| ffmpeg '
           '-thread_queue_size 1024 '
           '-f %s '
           '-vsync 2 '
           '%s'
           '-i - '
           '-thread_queue_size 1024 '
           '-f %s '
           '-guess_layout_max 0 '
           '%s'
           '-channels %s '
           '-sample_rate %s '
           '-i %s '
           '-vcodec copy '
           '-f %s '
           '-metadata title="%s" '
           '-metadata year="%s" '
           '-metadata description="%s" '
           '-metadata copyright="%s" '
           '-metadata comment="%s" '
           '-acodec %s '
           '-ar %s '
           '-b:a %s '
           '%s%s '
           '-hide_banner '
           '-nostats '
           '-loglevel "quiet"') % (overlay_text,
                                   settings_dict['video_in_intra_refresh_period'],
                                   settings_dict['video_in_width'],
                                   settings_dict['video_in_height'],
                                   settings_dict['video_in_frames_per_second'],
                                   settings_dict['video_in_bitrate'],
                                   settings_dict['video_in_codec'],
                                   video_offset,
                                   settings_dict['audio_in_codec'],
                                   audio_offset,
                                   settings_dict['audio_in_channels'],
                                   settings_dict['audio_in_sample_rate'],
                                   settings_dict['audio_hardware'],
                                   stream_codec,
                                   settings_dict['metadata_title'],
                                   metadata_year,
                                   settings_dict['metadata_description'],
                                   settings_dict['metadata_copyright'],
                                   settings_dict['metadata_comment'],
                                   settings_dict['audio_out_codec'],
                                   settings_dict['audio_out_sample_rate'],
                                   settings_dict['audio_out_bitrate'],
                                   url,
                                   port_or_key)
    os.popen(cmd)
    # Notification audio & video stream started (video)
    notification(interval=0.5, mode='v')
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(1)
    start_settings_webpage()
    print('started.')


def startup_checks():
    # Check Camera is connected
    print('Startup Checks')
    if si.camera_available['detected'] == 'False':
        logging.warning('No camera detected!')
        play_sound("warning_no_camera_detected.mp3")
        return True
    # Check USB sound card is connected
    if si.usb_sound_card_detected =='False':
        logging.warning('No USB sound card detected!')
        play_sound("warning_no_usb_sound_card_detected.mp3")
        return True
    # Check network is connected
    if si.network_detected == 'False':
        logging.warning('No network detected!')
        play_sound("warning_no_network_detected.mp3")
        return True
    # Check Internet is connected
    if si.internet_detected == 'False':
        logging.warning('No internet detected!')
        play_sound("warning_no internet_detected")
        return True
    return False


def stop_stream():
    # Stops audio & video stream
    # Speak through the headphone socket
    t = threading.Thread(target=play_sound, args=("ending_stream.mp3",))
    t.start()
    logging.info('Stopping audio video stream')
    print('Stopping audio video stream ... ', end = '')
    kill_streams()
    kill_settings()
    # Notification audio & video stream has stopped (exit)
    notification(interval=0.4, mode='e')
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(1)
    start_settings_webpage()
    print('stopped.')


# Check if running stand-alone or imported
if __name__ == '__main__':
    try:
        # Display header
        print('-----------------------------------------------------')
        print('This program streams audio and video to facebook live')
        print('  or can broadcast on the LAN via udp on port 4569.  ')
        print('     Written by Phantom Raspberry Blower  (2021)     ')
        print('-----------------------------------------------------')
        print('\n')
        logging.info('Started AVSS')

        # Display settings on web page 
        start_settings_webpage()

        # At startup wait for usb sound card to be detected
        if os.getpid() < 600:
            time.sleep(20)

        # Speak current IP address through the headphone socket
        speak_ip()
        time.sleep(10)

        # Add edge triggered event to audio & video stream switch
        GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH, callback=push_button)

        # Perform startup checks
        while startup_checks():
            notification(0.2, 'sos')
            time.sleep(3)

        # Check for updates
        t = threading.Thread(target=check_for_updates)
        t.start()

        # Notification program has started (initialized)
        notification(0.3, 'i')

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass

    # Tidy up any remaining connections
    atexit.register(cleanup)
