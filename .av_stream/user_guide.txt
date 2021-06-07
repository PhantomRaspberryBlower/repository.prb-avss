=======================================
Program: av_stream_service.py
Stream Audio & Video to Facebook or UDP
Written By: Phantom Raspberry Blower
Date: 21-04-2021
=======================================

Initial Setup Process:
----------------------
Connect the network cable, USB Soundcard, the power cable and headphones. When the Pi has started you should hear
"Hello this is the audio video streaming service and my I P address is" followed by the IP address of the device.
Using another computer connected to the network downloadand install TightVNC. Using TightVNC connect to the Pi using the IP 
address discovered earlier with port number 4569 i.e. 192.168.0.11::4569.
Type in the username (pi) and password (raspberry). OBS Studio is installed but this is for testing purposes only, as currently
(April 2021) OBS Studio can't utilize the GPU for hardware encoding, leaving only software encoding. When recording or streaming
this over-works the poor Pi which can only a manage 20fps at a resolution of 960x540; the CPU will reach 75 degrees centigrade
very rapidly. This should not be used for long periods as I say only for testing purposes. From now on you no longer need
to have a monitor, keyboard or mouse connected to the RPi. You can connect using TightVNC from another PC. :)

Startup Process:
----------------
Power up the RPi and wait until you hear 2 beeps and if headphones are connected the words "Hello this is the audio video
streaming service and my I P address is" followed by the IP address of the device. This indicates the Pi is ready to 
start streaming.

Start Stream:
-------------
Press the switch once to start streaming to facebook (using the supplied stream key) or for testing purposes broadcast using
UDP (i.e. udp://224.0.0.1:4569). The LED, speaker will flash and beep 4 times (morse code letter 'v' for videoing)
before starting the stream if headphones are connected you will also hear the words "Starting stream". Once streaming begins
the led remains on.

End Stream:
-----------
To stop the stream press the switch again the LED and speaker will flash and beep once (morse code lettr 'e' for ending)
and the words "Ending stream" can be heard through the headphones. The LED will remain off once the stream has ended.


Shutdown Process:
-----------------
To power down the RPi press and hold the switch for four seconds; the led flashes and the speaker beeps three times (morse code
letter 's' for shutdown) and the words "Shutting down" can be heard through headphones before starting the shutdown process.


Overview:
---------
1. Press switch to start/stop Stream
2. Turn on led when streaming
3. If stream fails led starts blinking:
	a. Long slow LED blinking means unable to connect
	b. Fast LED linking means connected but the stream key is incorrect
4. Long press (4 sec or more) stop current stream, flash led three times and shutdown


GPIO Pin Configuration:
-----------------------

Pin 4		Positive Cooling Fan + (red cable) 5v
Pin 6		Negative Coolog Fan - (black cable)
Pin 12		Streaming LED + (red cable)
Pin 14		Streaming LED - (white cable)
Pin 17		Streaming Switch + (red cable) 3v
Pin 18		Streaming Switch - (black cable)
Pin 30		Piezo Speaker - (black cable)
Pin 36		Piezo Speaker + (red cable)


The config file can be found in the  /home/pi/Desktop/.av_stream directory the following
options are available:

Config file:
------------
[SETTINGS]
audio_hardware = hw:CARD=CODEC,DEV=0				# Soundcard hardware device
audio_in_channels = 2						# Stereo
audio_in_codec = alsa						# Soundcard api
audio_in_sample_rate = 48000					# Soundcard sample rate
audio_out_bitrate = 128k					# Audio output sample rate
audio_out_codec = mp3						# Audio output codec
audio_out_sample_rate = 44100					# Audio output sample rate
broadcast_url = udp://224.0.0.1					# UDP broadcast url
broadcast_port = 4569						# UDP broadcast port number
enable_speaker = True						# Enable audible notifications
facebook_url = rtmps://live-api-s.facebook.com:443/rtmp/	# Facebook live streaming url
facebook_stream_key = <STREAM-KEY>				# Facebook live stream key
gpio_led_pin = 12						# GPIO LED pin number
gpio_switch_pin = 18						# GPIO switch pin number
gpio_spkr_pin = 36						# GPIO speaker pin number
itsoffset_seconds = 3.84					# Delay audio/video seconds
itsoffset = audio						# Delay audio/video (audio, video, none)
metadata_comment = Installed by Phantom Raspberry Blower	# Stream metadata comment
metadata_copyright = © Leicester Community Radio		# Stream metadata copyright
metadata_description = Leicester Community Radio started ...	# Stream metadata description
metadata_title = Leicester Community Radio			# Stream metadata title
metadata_year = current year					# Stream metadata year
startup_udp = True						# Startup using UDP (for testing)
video_in_bitrate = 1536000					# Camera bitrate
video_in_codec = h264						# Camera codec
video_in_frames_per_second = 25					# Camera frames per second
video_in_intra_refresh_period = 50				# Camera gop
video_in_height = 720						# Camera resolution height
video_in_width = 1280						# Camera reaolution width
video_out_codec = mpegts					# Stream output codec
video_out_overlay_text = -a 12 -a "Leicester Community Radio"	# Stream output text overlay




