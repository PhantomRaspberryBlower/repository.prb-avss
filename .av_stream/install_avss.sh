#1/bin/bash
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
WORK_DIR=~/.av_stream
echo "-----------------------------------"
echo "     Making working directory"
echo "-----------------------------------"
mkdir -p "$WORK_DIR"
echo "-----------------------------------"
echo "        Getting AVSS source"
echo "-----------------------------------"
sudo git clone https://github.com/PhantomRaspberryBlower/repository.prb-avss ~/.av_stream
sudo cp -r /home/pi/.av_stream/.av_stream/*.* /home/pi/.av_stream/
cd .av_stream
sudo rm -r .av_stream
sudo rm -r .git
sudo cp asound.conf /etc/asound.conf
sudo cp av_stream.service /etc/systemd/system/av_stream.service
sudo systemctl enable /etc/systemd/system/av_stream.service
sudo rm asound.conf
sudo rm av_stream.service
echo "==================================="
echo "           Completed :)"
echo "==================================="
sudo reboot
