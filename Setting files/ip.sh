#!/bin/bash
sudo killall wpa_supplicant
sleep 5
sudo wpa_supplicant -B -c /etc/wpa_supplicant/wpa_supplicant-nl80211-wlan0.conf -i wlan0
sudo dhclient wlan0
sleep 20
wlan0=`ifconfig  wlan0 | head -n2 | grep inet | awk '{print$2}'`
eth0=`ifconfig  eth0 | head -n2 | grep inet | awk '{print$2}'`
 
if ping -c 2 -W 3 www.baidu.com &> /dev/null ;then
/home/ubuntu/mail.py striketong@163.com "Got raspberryPi IP!" "WLAN0:$wlan0||ETH0:$eth0"
fi