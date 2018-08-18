#!/bin/bash

cd $HOME
dropbox_uploader.sh upload bin/ scripts/
dropbox_uploader.sh upload /etc/motion/motion.conf scripts/bin
crontab -l > crontab.txt
dropbox_uploader.sh upload crontab.txt scripts/bin

