#!/bin/bash

die() { echo "ERROR:$0:$@ !"; exit 1; }
warn() { echo "WARNING:$0:$@"; }

##############################3

sudo apt-get update
sudo apt-get dist-upgrade

sudo apt-get install vim
sudo apt-get install fswebcam
sudo apt-get install imagemagick vlc
sudo apt-get install xscreensaver

sudo apt-get install motion
# cp in our /etc/motion/motion.conf

# setup dropbox
curl "https://raw.githubusercontent.com/andreafabrizi/Dropbox-Uploader/master/dropbox_uploader.sh" -o dropbox_uploader.sh
chmod +x dropbox_uploader.sh
./dropbox_uploader.sh
[ ! $? -eq 0 ] && die "./dropbox_uploader.sh DIED"

# test connection
./dropbox_uploader.sh list
[ ! $? -eq 0 ] && die "./dropbox_uploader.sh list DIED"



# TODO: config sendmail

# start motion
sudo service motion start


echo "TODO: copy off dropbox_uploader.sh & _MULTI.sh to $HOME/bin,eg"
echo "TODO: now configure crontab to fire every 5min or so, and shuttle all files to cloud"
echo "       '*/15 * * * * PATH=$PATH:/home/pi/bin /home/pi/bin/dropbox_uploader_MULTI.Sh -r garage_webcam-`date +%Y%m%d` /var/lib/motion/*.avi &> /home/pi/out'"
echo "TODO: add $HOME/bin to PATH"
echo "TODO: change /etc/default/motion to =yes, reboot. then 'sudo service motion restart' to restart if needed""
