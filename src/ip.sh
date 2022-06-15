#!/bin/bash
sudo killall wpa_supplicant
sleep 5
sudo wpa_supplicant -B -c /etc/wpa_supplicant/wpa_supplicant-nl80211-wlan0.conf -i wlan0
sudo dhclient wlan0

sleep 5
wlan0=`ifconfig  wlan0 | head -n2 | grep inet | awk '{print$2}'`
eth0=`ifconfig  eth0 | head -n2 | grep inet | awk '{print$2}'`
sudo /home/ubuntu/wific.sh & 

sleep 5

if ping -c 2 -W 3 www.baidu.com &> /dev/null ;then
/home/ubuntu/mail.py striketong@163.com "Got raspberryPi IP!" "WLAN0:$wlan0||ETH0:$eth0"
fi

/home/ubuntu/mail.py striketong@163.com "Got raspberryPi IP!" "WLAN0:$wlan0||ETH0:$eth0"

sudo sed -i "21c \$CFG->wwwroot   = 'http://$wlan0:8888/moodle';" /var/www/html/moodle/config.php

/usr/bin/python3 /home/ubuntu/applysystem/moodle.py &


