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
echo "-----------------------------------"
echo "        Installing updates"
echo "-----------------------------------"
apt-get -y update
echo "-----------------------------------"
echo "      Upgrading installation"
echo "-----------------------------------"
apt-get -y upgrade
echo "-----------------------------------"
echo "         Installing FFmpeg"
echo "-----------------------------------"
apt-get -y install ffmpeg
echo "-----------------------------------"
echo "        Installing festival"
echo "-----------------------------------"
apt-get -y install festival
echo "-----------------------------------"
echo "        Installing PiCamera"
echo "-----------------------------------"
apt-get -y install python-picamera
apt-get -y install python3-picamera
echo "-----------------------------------"
echo "         Installing PyGame"
echo "-----------------------------------"
apt-get -y install python3-pygame
echo "-----------------------------------"
echo "         Installing git"
echo "-----------------------------------"
apt-get -y install git
echo "-----------------------------------"
echo "     Making working directory"
echo "-----------------------------------"
mkdir -p /home/pi/.av_stream
cd /home/pi/.av_stream
echo "-----------------------------------"
echo "        Getting AVSS source"
echo "-----------------------------------"
git clone https://github.com/PhantomRaspberryBlower/repository.prb-avss /home/pi/.av_stream
cp -r /home/pi/.av_stream/.av_stream/*.* /home/pi/.av_stream/
rm -r /home/pi/.av_stream/.av_stream
rm -r /home/pi/.av_stream/.git
cp /home/pi/.av_stream/asound.conf /etc/asound.conf
cp /home/pi/.av_stream/av_stream.service /etc/systemd/system/av_stream.service
systemctl enable /etc/systemd/system/av_stream.service
cd /.av_stream
chown pi:pi *.*
echo "-----------------------------------"
echo "           Enable camera"
echo "-----------------------------------"
raspi-config nonint do_camera 0
echo "-----------------------------------"
echo "       Cleanup installation"
echo "-----------------------------------"
rm /home/pi/.av_stream/asound.conf
rm /home/pi/.av_stream/av_stream.service
apt -y autoremove
echo "==================================="
echo "           Completed :)"
echo "==================================="
echo ""
echo "-----------------------------------"
echo "           Rebooting"
echo "-----------------------------------"
reboot
