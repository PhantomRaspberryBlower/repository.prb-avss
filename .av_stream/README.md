![AVSS logo](https://github.com/PhantomRaspberryBlower/repository.prb-avss/blob/master/.av_stream/icon.png)

Audio Video Streaming Service (AVSS)
====================================

Turns a headless (no keyboard, no mouse or monitor) Raspberry Pi into a audio video streaming service that can live stream to Facebook, Periscope, Twitch, Ustream, Vimeo, YouTube simultaneously or multicast using UDP. The RPi needs to have Raspbian Lite installed and a few things connected to the GPIO (general purpose input output) pins; an LED, a switch and a Peizo speaker. We also need to have a PiCamera (the offical camera for the RPi) and a USB sound card with a line in. This was created for a local radio station to live stream DJ's performacnes and allow a mixing desk to be connected.

When AVSS starts it uses the audio headphone socket to speak the Pi's IP address. With this IP address AVSS can be configured using a web browser by navigating to the IP address of the Pi. For example if the Pi's IP address is 192.168.0.10 navigate to http://192.168.0.10. Here we can change the settings and set the stream keys required by live stream providers. You can optionally stream using udp on port 4569 to test before going live; using a media server: Kodi or VLC to connect to the stream. For VLC go to http://@192.168.0.10:4569 or with Kodi you can create an strm file containing http://192.168.0.10:4569

Due to the Pi being headless each time the Pi starts it beeps twice to notify the user that the Pi is ready. If the headphones are connected you will hear "Hello this is Raspberry Pi and my IP address is ...". To start a stream press the switch once; it now beeps 3 times and the LED remains on to inidicate that the Pi is streaming. You will also hear through the headphones "Starting Stream". To stop the stream press the switch again; it now beeps once, the LED goes out and you will hear "Ending Stream". To shutdown the Pi press and hold the switch for four seconds; it beeps three times indicating it is safe to unplug and also hear "Shutting Down".

To install just download install_avss.sh and allow it be executable by typing:

sudo chmod +x install_avss.sh

Then type:

sudo bash install_avss.sh