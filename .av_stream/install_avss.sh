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
WORK_DIR=~/.av_stream
echo "-----------------------------------"
echo "     Making working directory"
echo "-----------------------------------"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
echo "-----------------------------------"
echo "        Getting AVSS source"
echo "-----------------------------------"
git clone --recursive https://github.com/PhantomRaspberryBlower/repository.prb-avss/tree/main/.av_stream
sudo copy asound.conf /etc/asound.conf
sudo copy av_stream.service /etc/systemd/system/av_stream.service
sudo systemctl enable av_stream.service
sudo rm asound.conf
sudo rm av_stream.service
echo "==================================="
echo "           Completed :)"
echo "==================================="
