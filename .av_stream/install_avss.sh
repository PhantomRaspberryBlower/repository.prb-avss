#!/bin/bash
# Audio Video Streaming Service (AVSS)
# Script for installing AVSS onto a headless Raspberry Pi installed with buster lite
# Need to make it executable and run as root ie.
# sudo chmod +x install_avss.sh
# followed by
# sudo bash install_avss.sh
# Written by: Phantom Raspberry Blower
# Date May 2021

if [ "$EUID" -ne 0 ]
  then echo "Needs to be run as root! Type in: sudo bash install_avss.sh"
  exit
fi
WORK_DIR=/home/pi
echo "-----------------------------------"
echo "       Installing OS updates"
echo "-----------------------------------"
apt-get -y update
echo "-----------------------------------"
echo "     Upgrading OS installation"
echo "-----------------------------------"
apt-get -y upgrade
echo "-----------------------------------"
echo "         Installing FFmpeg"
echo "-----------------------------------"
# Encodes audio & videos files
apt-get -y install ffmpeg
echo "-----------------------------------"
echo "        Installing festival"
echo "-----------------------------------"
# Used for text to speech
apt-get -y install festival
echo "-----------------------------------"
echo "        Installing PiCamera"
echo "-----------------------------------"
# Official Raspberry Pi camera module
apt-get -y install python-picamera
apt-get -y install python3-picamera
echo "-----------------------------------"
echo "         Installing PyGame"
echo "-----------------------------------"
# Used to play audio files (mp3)
apt-get -y install python3-pygame
echo "-----------------------------------"
echo "          Installing git"
echo "-----------------------------------"
# Used to clone and update repository
apt-get -y install git
echo "-----------------------------------"
echo "          Installing pip"
echo "-----------------------------------"
# Used to install sh
apt-get -y install python-pip
apt-get -y install python3-pip
echo "-----------------------------------"
echo "           Installing sh"
echo "-----------------------------------"
pip install sh
echo "-----------------------------------"
echo "     Making working directory"
echo "-----------------------------------"
mkdir -p "$WORK_DIR"/.av_stream
cd "$WORK_DIR"/.av_stream
echo "-----------------------------------"
echo "        Getting AVSS source"
echo "-----------------------------------"
git clone --recursive https://github.com/PhantomRaspberryBlower/repository.prb-avss "$WORK_DIR"/.av_stream
mv "$WORK_DIR"/.av_stream/.av_stream/* "$WORK_DIR"/.av_stream/
mv "$WORK_DIR"/.av_stream/.git "$WORK_DIR"
mv "$WORK_DIR"/.av_stream/.gitattributes "$WORK_DIR"
rm -r "$WORK_DIR"/.av_stream/.av_stream
cp "$WORK_DIR"/.av_stream/config.bkp.ini "$WORK_DIR"/.av_stream/config.ini
cp "$WORK_DIR"/.av_stream/asound.conf /etc/asound.conf
cp "$WORK_DIR"/.av_stream/av_stream.service /etc/systemd/system/av_stream.service
cp "$WORK_DIR"/.av_stream/redirect.service /etc/systemd/system/redirect.service
systemctl enable /etc/systemd/system/av_stream.service
systemctl enable /etc/systemd/system/redirect.service
chown pi:pi -R "$WORK_DIR"
echo "-----------------------------------"
echo "           Enable camera"
echo "-----------------------------------"
raspi-config nonint do_camera 0
echo "-----------------------------------"
echo "   Enable PWM Fan pin 14 at 65'C"
echo "-----------------------------------"
raspi-config nonint do_fan 0 14 65
echo "-----------------------------------"
echo "       Cleanup installation"
echo "-----------------------------------"
apt -y autoremove
echo "==================================="
echo "           Completed :)"
echo "==================================="
echo ""
echo "==================================="
echo "           Rebooting"
echo "==================================="
reboot
