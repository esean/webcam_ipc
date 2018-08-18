# upload all *.avi and *.jpg to Dropbox under datestamped directory
export PATH=$PATH:/home/pi/bin
dropbox_uploader_MULTI.Sh -r `date +%Y%m%d`-garage_webcam-AVI /var/lib/motion/*.avi
dropbox_uploader_MULTI.Sh -r `date +%Y%m%d`-garage_webcam-JPG /var/lib/motion/*.jpg
