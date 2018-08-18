#!/usr/local/bin/python
import socket
from socket import error as socket_error
import os,sys
import subprocess
from datetime import datetime
import re

port = 9876

# how many items from GCP Vision should we splurt out
MAX_NUMBER_LOOKS_LIKE_THINGS_TO_SAY = 3

#-----------------------------------
def voice_from_ipaddr(ip_addr):
    # default
    voice = 'Alex'
    ding = '/System/Library/Sounds/Tink.aiff'
    alias = 'unknown'
    if ip_addr == '10.0.0.200': # 'side'
        #voice = 'Mei-Jia'   # zh_TW
        #voice = 'Daniel'   # en_GB    # Hello, my name is Daniel. I am a British-English voice
        voice = 'Kanya'    # th_TH
        ding = '/System/Library/Sounds/Pop.aiff'
        alias = 'side'
    elif ip_addr == '10.0.0.201':   # 'garage'
        #voice = 'Kyoko'     # ja_JP    
        voice = 'Tessa'    # en_ZA    # Hello, my name is Tessa. I am a South African-English voice.
        #voice = 'Veena'    # en_IN    # Hello, my name is Veena. I am an Indian-English voice.
        #voice = 'Fiona'    # en-scotland # Hello, my name is Fiona. I am a Scottish-English voice.
        #voice = 'Allison'  # en_US    # Hello, my name is Allison. I am an American-English voice.
        ding = '/System/Library/Sounds/Purr.aiff'
        alias = 'garage'
    return voice,ding,alias

#-----------------------------------
class Re(object):
    def __init__(self):
        self.last_match = None
    # match = starts with...
    def match(self,pattern,text):
        self.last_match = re.match(pattern,text)
        return self.last_match
    # search = somewhere in there
    def search(self,pattern,text):
        self.last_match = re.search(pattern,text)
        return self.last_match

#-----------------------------------
# RETURNS 0 on success
def run_subprocess(cmdtxt,runCmdInBackground = False):
    #  print "\n# DBG:SUBPROCESS:%s(%d)" % (cmdtxt,runCmdInBackground)
    # if we want to run in the background, just launch the cmd and return
    #---------
    if runCmdInBackground:
        os.system("%s &" % cmdtxt)
        return (0,"No output from background os.system(%s) call" % cmdtxt)
    # else this is a blocking call, use Popen
    #---------
    try:
        p = subprocess.Popen(cmdtxt, stdout=subprocess.PIPE, shell=True,stderr=subprocess.STDOUT)
    except KeyboardInterrupt:
        #    print "...got ctrl-c..."
        pid = p.pid
        p.terminate()
        p.send_signal(signal.SIGKILL)
        # Check if the process has really terminated & force kill if not.
        try:
            os.kill(pid, signal.SIGKILL)
            p.kill()
            print "Forced kill"
        except OSError, e:
            print "Terminated gracefully"
    (output, err) = p.communicate()
    p_status = p.wait()
    outtxt = output.strip()
    #  print "# >>>> SUBPROCESS_INFO_START(%s) >>>>" % cmdtxt
    #  app = cmdtxt.split(' ', 1)[0]
    #  for ln in outtxt.splitlines():
    #    print " +%s+> %s" % (app,ln)
    #  print "# <<<< SUBPROCESS_INFO_END(%s) <<<< " % cmdtxt
    if p_status > 0:
        print "ERROR: error returned from following command,"
        print "ERROR:      $ ",cmdtxt
    #  print "# DBG:  SUBPROCESS END:%s retcode=%d" % (cmdtxt,p_status)
    return (p_status,outtxt)

#-----------------------------------
def make_a_ding(ding_name):
    (p_status,outtxt) = run_subprocess("afplay %s" % ding_name,True)

#-----------------------------------
def say_text_in_voice(msg,voice,rate):
    cmd = "say -r %f -v %s %s" % (rate,voice,msg)
    # kick off saying text in background, this speeds up server response
    (p_status,outtxt) = run_subprocess(cmd,True)
    return p_status

#-----------------------------------
def massage_looks_like_text(msg):
    the_things = msg.split(':')[1]
    phrases = the_things.split('\'')
    my_str = ''
    # find first 3 interesting things to say, ie ignore certain things
    for phrase in phrases:
        # remove any backslashes
        phrase = phrase.replace("\\","")
        # if string is empty, or by removing spaces it became empty, go to next phrase
        is_blank = phrase.replace(" ","")
        if not is_blank:
            continue
        # now we have the phrase ready, ignore colors
        color_words = ['white','green','red','blue','line']
        if any(i in phrase for i in color_words):
#            print "SKIP color:%s" % phrase
            continue

        my_str += "%s " % phrase

    # only vocalize the first 3 words
#    what_to_say = the_things.split(' ')[:MAX_NUMBER_LOOKS_LIKE_THINGS_TO_SAY]
    what_to_say = my_str.split(' ')[:MAX_NUMBER_LOOKS_LIKE_THINGS_TO_SAY]
    # putting '-' between words makes speech smoother
    return what_to_say #"-".join(what_to_say)

#-----------------------------------
def process_incoming_text(from_ip,msg):
    # find out details about incoming host
    voice,ding_name,alias = voice_from_ipaddr(from_ip)
    timenow = str(datetime.now())
    display_txt = "[%s] %s(%s): %s" % (timenow,from_ip,alias,msg)
    print display_txt
    c.send(display_txt)
    
    # TEXT-2-SPEECH
    # 'SAY' msg: only speak a 'msg' that starts with 'say:', ignore the rest
    what_to_say = ''
    rate = 150
    gre = Re()
    if gre.match(r'say:',msg):
        what_to_say = msg.split(':')[1]
    
    # 'LOOKS_LIKE' msg:
    if gre.match(r'looks_like:',msg):
        what_to_say = massage_looks_like_text(msg)
        print "LOOKS_LIKE >>> %s <<<" % what_to_say
        # and make the speech much faster
        rate *= 1.5

    # 'PIC' msg:
    if gre.match(r'pic:',msg):
        the_pic = msg.split(':')[1]
        print "  >> cmd># scp pi@%s:%s ." % (from_ip,the_pic)
        # make a sound
        make_a_ding(ding_name)

        #        # grab out the sizes of bounding box around motion
        #        #=========================================
        #        #   From motion.conf:
        #        #   #------------------
        #        #   # %i and %J = width and height of motion area,
        #        #   # %K and %L = X and Y coordinates of motion center
        #        #   #------------------
        #        # assumption is motion.conf has configured picture output name like,
        #        #
        #        #   picture_filename %v-%Y%m%d%H%M%S+%i,%j-%K,%L+%q
        #        #       - AND -
        #        #   target_dir /var/lib/motion
        #        #
        #        # so it writes out the filename like this,
        #        #   /var/lib/motion/11-20171008150307+66,281-883,249+00.jpg
        #        #=========================================
        #        a = re.match('.*\+(.*),(.*)-(.*),(.*)\+[0-9][0-9].jpg$',the_pic)
        #        if a:
        #            Dwidth = float(a.group(1))
        #            Dheight = float(a.group(2))
        #            Dx = float(a.group(3))
        #            Dy = float(a.group(4))
        #            #print "OK @ (x,y) = (%f,%f), (w/h) = (%f,%f)" % (Dx,Dy,Dwidth,Dheight)

    # say any text we have
    if what_to_say:
        #print "#DBG:SAY:%s" % what_to_say
        say_text_in_voice(what_to_say,voice,rate)

#-----------------------------------
def resolve_host_ip(host):
    try:
        remote_ip = socket.gethostbyname( host )
    except socket_error, msg:
        print "ERROR:resolve_host_ip():caught exception socket.error : %s" % msg
        return None
    return remote_ip

#-----------------------------------
#-----------------------------------
mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(socket.getfqdn())
if host == "127.0.1.1":
#    host = commands.getoutput("hostname")
    print "ERROR: failed to get hostname"
    sys.exit(1)
print "STARTING server @ " + host
#print "google = %s" % resolve_host_ip('fpSean.local')
#sys.exit(0)

#Prevent socket.error: [Errno 98] Address already in use
mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mysocket.bind((host, port))
mysocket.listen(5)

while True:

  # waiting for new connection
  c, addr = mysocket.accept()

  while True:

    data = c.recv(1024)
    data = data.replace("\r\n", '') #remove new line character

    # if we got nothing, or tranaction is done, exit out and go back to waiting
    if not data:
      break
    
    # process incoming data
    process_incoming_text(addr[0],data)

c.send("Server stopped\n")
print "Server stopped"
c.close()

