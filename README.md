# webcam_ipc
Using 2 RaspberryPi w/ webcams, and running Linux motion utility and Google Vision API, these scripts can alert a main server computer with spoken text and sound alerts when motion has been detected.

The motion app detects motion from the webcams, and a subsection of that webcam picture where motion was detected is analyzed by Google Vision API to get a list of words of what it sees in the picture.

This information from the RPi is then relayed across a simple client/server "IPC" to the server computer which makes the announcements, using different computer voices for the various RPi doing the reporting. In other words, each RPi appears to have it's own voice.
