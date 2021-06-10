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
echo "          Installing git"
echo "-----------------------------------"
apt-get -y install git
echo "-----------------------------------"
echo "          Installing pip"
echo "-----------------------------------"
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
git clone https://github.com/PhantomRaspberryBlower/repository.prb-avss "$WORK_DIR"/.av_stream
mv "$WORK_DIR"/.av_stream/.git "$WORK_DIR"
mv "$WORK_DIR"/.av_stream/.gitattributes "$WORK_DIR"
cp -r "$WORK_DIR"/.av_stream/.av_stream/*.* "$WORK_DIR"/.av_stream
rm -r "$WORK_DIR"/.av_stream/.av_stream
cp "$WORK_DIR"/.av_stream/asound.conf /etc/asound.conf
cp "$WORK_DIR"/.av_stream/av_stream.service /etc/systemd/system/av_stream.service
systemctl enable /etc/systemd/system/av_stream.service
cd "$WORK_DIR"
chown pi:pi *.*
echo "-----------------------------------"
echo "           Enable camera"
echo "-----------------------------------"
raspi-config nonint do_camera 0
echo "-----------------------------------"
echo "       Cleanup installation"
echo "-----------------------------------"
#rm "$WORK_DIR"/.av_stream/asound.conf
#rm "$WORK_DIR"/.av_stream/av_stream.service
apt -y autoremove
echo "==================================="
echo "           Completed :)"
echo "==================================="
echo ""
echo "-----------------------------------"
echo "           Rebooting"
echo "-----------------------------------"
sleep 3
reboot
