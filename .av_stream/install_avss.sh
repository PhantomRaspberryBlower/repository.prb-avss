#!/bin/bash
# Audio Video Streaming Service (AVSS)
# Script for installing AVSS onto a headless
# Raspberry Pi installed with buster lite

echo "-----------------------------------"
echo "        Installing updates"
echo "-----------------------------------"
sudo apt-get -y update
echo "-----------------------------------"
echo "      Upgrading installation"
echo "-----------------------------------"
sudo apt-get -y upgrade
echo "-----------------------------------"
echo "         Installing FFmpeg"
echo "-----------------------------------"
sudo apt-get -y install ffmpeg
echo "-----------------------------------"
echo "        Installing festival"
echo "-----------------------------------"
sudo apt-get -y install festival
echo "-----------------------------------"
echo "        Installing PiCamera"
echo "-----------------------------------"
sudo apt-get -y install python-picamera
sudo apt-get -y install python3-picamera
echo "-----------------------------------"
echo "         Installing PyGame"
echo "-----------------------------------"
sudo apt-get -y install python3-pygame
echo "-----------------------------------"
echo "         Installing git"
echo "-----------------------------------"
sudo apt-get -y install git
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
sudo cp /home/pi/.av_stream/asound.conf /etc/asound.conf
sudo cp /home/pi/.av_stream/av_stream.service /etc/systemd/system/av_stream.service
sudo systemctl enable /etc/systemd/system/av_stream.service
cd /.av_stream
sudo chown pi:pi *.*
echo "-----------------------------------"
echo "       Cleaning installation"
echo "-----------------------------------"
rm /home/pi/.av_stream/asound.conf
rm /home/pi/.av_stream/av_stream.service
sudo apt -y autoremove
echo "-----------------------------------"
echo "           Enable camera"
echo "-----------------------------------"
sudo raspi-config nonint do_camera 0
echo "==================================="
echo "           Completed :)"
echo "==================================="
sudo shutdown -r
echo ""
echo "-----------------------------------"
echo "           Rebooting"
echo "-----------------------------------"
