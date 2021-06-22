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

logging.basicConfig(format='%(asctime)s - %(message)s',
                    filename='%s/avss.log' % WORK_DIR,
                    level=logging.DEBUG)

def get_settings():
    global settings_dict
    global metadata_year
    settings_dict = commontasks.get_settings(WORK_DIR + '/config.ini')
    if settings_dict['metadata_year'] == 'current year':
        metadata_year = date.today().year

get_settings()

if settings_dict['logging_level'] == 'NONE':
    logging.disable(level=logging.CRITICAL)
elif settings_dict['logging_level'] == 'DEBUG':
    logging.getLogger().setLevel(logging.DEBUG)
elif settings_dict['logging_level'] == 'INFO':
    logging.getLogger().setLevel(logging.INFO)
elif settings_dict['logging_level'] == 'WARNING':
    logging.getLogger().setLevel(logging.WARNING)
elif settings_dict['logging_level'] == 'ERROR':
    logging.getLogger().setLevel(logging.ERROR)
elif settings_dict['logging_level'] == 'CRITICAL':
    logging.getLogger().setLevel(logging.CRITICAL)

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
        t = threading.Thread(target=play_sound,
                             args=("checking_for_updates.mp3",))
        t.start()
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
    if settings_status != None:
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
    # 'v' = start_video; 'e' = end_video; 's' = shutdown; 'sos' = warning
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
        logging.warning('Unable to play sound file!')


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


def build_raspivid_cmd():
    overlay_text = ''
    raspivid_cmd = 'raspivid -t 0 -a 12'
    if len(settings_dict['video_out_overlay_text']) > 0:
        overlay_text = ' -a "%s" -ae %s,0x%s' % (settings_dict['video_out_overlay_text'].replace('~','%'),
                                                 settings_dict['video_out_overlay_text_size'],
                                                 settings_dict['video_out_overlay_text_color'].replace('#',''))
        if settings_dict['video_out_overlay_bg_color_enabled'] == 'True':
            overlay_text +=',0x%s' % settings_dict['video_out_overlay_bg_color'].replace('#', '')
        else:
            overlay_text +=',0x8080FF'
    raspivid_cmd += overlay_text
    raspivid_cmd += ' -g %s' % settings_dict['video_in_intra_refresh_period']
    raspivid_cmd += ' -roi 0,0,0.998,1'
    if settings_dict['video_image_horizontal_flip'] == 'True':
        raspivid_cmd += ' -hf'
    if settings_dict['video_image_vertical_flip'] == 'True':
        raspivid_cmd += ' -vf'
    if settings_dict['video_stabilisation'] == 'True':
        raspivid_cmd += ' -vs'
    raspivid_cmd += ' -rot %s' % settings_dict['video_image_rotation']
    raspivid_cmd += ' -br %s' % settings_dict['video_image_brightness']
    raspivid_cmd += ' -co %s' % settings_dict['video_image_contrast']
    raspivid_cmd += ' -sa %s' % settings_dict['video_image_saturation']
    raspivid_cmd += ' -sh %s' % settings_dict['video_image_sharpness']
    raspivid_cmd += ' -ex %s' % settings_dict['video_image_exposure']
    raspivid_cmd += ' -pf %s' % settings_dict['video_image_profile']
    raspivid_cmd += ' -awb %s' % settings_dict['video_image_automatic_white_balance']
    raspivid_cmd += ' -drc %s' % settings_dict['video_image_dynamic_range_compression']
    raspivid_cmd += ' -fli %s' % settings_dict['video_image_flicker_avoidance']
    raspivid_cmd += ' -ifx %s' % settings_dict['video_image_effect']
    raspivid_cmd += ' -o -'
    raspivid_cmd += ' -w %s' % settings_dict['video_in_width']
    raspivid_cmd += ' -h %s' % settings_dict['video_in_height']
    raspivid_cmd += ' -fps %s' % settings_dict['video_in_frames_per_second']
    raspivid_cmd += ' -b %s' % settings_dict['video_in_bitrate']
    return raspivid_cmd


def build_ffmpeg_cmd():
    url = ''
    port_or_key = ''
    audio_offset = ''
    video_offset = ''
    ffmpeg_cmd = 'ffmpeg -thread_queue_size 1024'
    if settings_dict['itsoffset'] != 'none':
        if settings_dict['itsoffset'] == 'audio':
            audio_offset = ' -itsoffset %s' % settings_dict['itsoffset_seconds']
        elif settings_dict['itsoffset'] == 'video':
            video_offset = ' -itsoffset %s' % settings_dict['itsoffset_seconds']

    if settings_dict['startup_udp'] == 'True':
        url = settings_dict['broadcast_url']
        port_or_key = ':' + settings_dict['broadcast_port']
        stream_codec = 'mpegts'
    else:
        url = settings_dict['facebook_url']
        stream_codec = settings_dict['video_out_codec']

    ffmpeg_cmd += ' -f %s' % settings_dict['video_in_codec']
    ffmpeg_cmd += ' -vsync 2'
    ffmpeg_cmd += video_offset
    ffmpeg_cmd += ' -i -'
    ffmpeg_cmd += ' -thread_queue_size 1024'
    ffmpeg_cmd += ' -f %s' % settings_dict['audio_in_codec']
    ffmpeg_cmd += ' -guess_layout_max 0'
    ffmpeg_cmd += audio_offset
    ffmpeg_cmd += ' -channels %s' % settings_dict['audio_in_channels']
    ffmpeg_cmd += ' -sample_rate %s' % settings_dict['audio_in_sample_rate']
    ffmpeg_cmd += ' -i %s' % settings_dict['audio_hardware']
    ffmpeg_cmd += ' -vcodec copy'
    ffmpeg_cmd += ' -f %s' % stream_codec
    ffmpeg_cmd += ' -metadata title="%s"' % settings_dict['metadata_title']
    ffmpeg_cmd += ' -metadata year="%s"' % metadata_year
    ffmpeg_cmd += ' -metadata description="%s"' % settings_dict['metadata_description']
    ffmpeg_cmd += ' -metadata copyright="%s"' % settings_dict['metadata_copyright']
    ffmpeg_cmd += ' -metadata comment="%s"' % settings_dict['metadata_comment']
    ffmpeg_cmd += ' -acodec %s' % settings_dict['audio_out_codec']
    ffmpeg_cmd += ' -ar %s' % settings_dict['audio_out_sample_rate']
    ffmpeg_cmd += ' -b:a %s' % settings_dict['audio_out_bitrate']
    ffmpeg_cmd += ' %s%s' % (url, port_or_key)
    ffmpeg_cmd += ' -hide_banner -nostats -loglevel "quiet"'
    return ffmpeg_cmd


def start_stream():
    # Speak through the headphone socket
    t = threading.Thread(target=play_sound, args=("starting_stream.mp3",))
    t.start()
    logging.info('Starting audio video stream')
    get_settings()
    kill_settings()
    cmd = '%s | %s' % (build_raspivid_cmd(), build_ffmpeg_cmd())
    os.popen(cmd)
    # Notification audio & video stream started (video)
    notification(interval=0.5, mode='v')
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(1)
    start_settings_webpage()


def startup_checks():
    # Check Camera is connected
    if si.camera_available['detected'] == 'False':
        logging.warning('No camera detected!')
        t = threading.Thread(target=play_sound,
                             args=("warning_no_camera_detected.mp3",))
        t.start()
        return True
    # Check USB sound card is connected
    if si.usb_sound_card_detected =='False':
        logging.warning('No USB sound card detected!')
        t = threading.Thread(target=play_sound,
                             args=("warning_no_usb_sound_card_detected.mp3",))
        t.start()
        return True
    # Check network is connected
    if si.network_detected == 'False':
        logging.warning('No network detected!')
        t = threading.Thread(target=play_sound,
                             args=("warning_no_network_detected.mp3",))
        t.start()
        return True
    # Check Internet is connected
    if si.internet_detected == 'False':
        logging.warning('No internet detected!')
        t = threading.Thread(target=play_sound,
                             args=("warning_no internet_detected.mp3",))
        t.start()
        return True
    return False


def stop_stream():
    # Stops audio & video stream
    # Speak through the headphone socket
    t = threading.Thread(target=play_sound, args=("ending_stream.mp3",))
    t.start()
    logging.info('Stopping audio video stream')
    kill_streams()
    kill_settings()
    # Notification audio & video stream has stopped (exit)
    notification(interval=0.4, mode='e')
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(1)
    start_settings_webpage()


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
        logging.info('*** Starting AVSS ***')
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
        # Check for updates
        t = threading.Thread(target=check_for_updates)
        t.start()
        # Perform startup checks
        while startup_checks():
            notification(0.2, 'sos')
            time.sleep(3)

        # Notification program has started (initialized)
        notification(0.3, 'i')
        t = threading.Thread(target=play_sound, args=("ready_and_waiting.mp3",))
        t.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        pass

    # Tidy up any remaining connections
    atexit.register(cleanup)
