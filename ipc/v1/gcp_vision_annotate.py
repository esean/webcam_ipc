#!/usr/bin/env python
import sys
import os
import re

import io
from google.cloud import vision
from google.cloud.vision import types

#-----------------------------------
def usage():
  print
  print "USAGE:",sys.argv[0]," [picture filename]"
  print
  print "Send picture to Google Cloud Platform Vision API for annotation."
  print
  print "If [picture filename] is encoded like,"
  print "	05-20171008164313+88,281-788,374+00.jpg"
  print "using motion.conf,"
  print "   	picture_filename %v-%Y%m%d%H%M%S+%i,%j-%K,%L+%q"
  print "then assumption is this, and only that sub-section bounding box will be annotated."
  print "	...+[width],[height]-[centerX],[centerY]+..."
  print
  print "If that filename encoding is not present, the entire picture will be annotated."
  print

def main(photo_file):
    """Run a request on a single image"""

    API_DISCOVERY_FILE = 'https://vision.googleapis.com/$discovery/rest?version=v1'
    http = httplib2.Http()

    credentials = GoogleCredentials.get_application_default().create_scoped(
            ['https://www.googleapis.com/auth/cloud-platform'])
    credentials.authorize(http)

    service = build('vision', 'v1', http, discoveryServiceUrl=API_DISCOVERY_FILE)

    with open(photo_file, 'rb') as image:
        image_content = base64.b64encode(image.read())
        service_request = service.images().annotate(
                body={
                    'requests': [{
                        'image': {
                            'content': image_content
                        },
                        'features': [{
                            'type': 'LABEL_DETECTION',
                            'maxResults': 20,
                        },
                            {
                            'type': 'TEXT_DETECTION',
                            'maxResults': 20,
                            }]
                    }]
                })
    response = service_request.execute()

    return response


def parse_response(photo_file, response):
    """ Parse response into relevant fields"""
    
    response = response
    query = photo_file
    all_labels = ''
    all_text = ''
    img_labels = '**Labels Found: \n'  # For image annotation
    img_text = '**Text Found: \n'  # For image annotation

    try:
        labels = response['responses'][0]['labelAnnotations']
        for label in labels:
            label_val = label['description']
            score = str(label['score'])
            print('Found label: "%s" with score %s' % (label_val, score))

            all_labels += label_val.encode('utf-8') + ' @ ' + score + ', '
            img_labels += label_val.encode('utf-8') + ' @ ' + score + '\n'
    except KeyError:
        print("N/A labels found")

    print('\n')

    try:
        texts = response['responses'][0]['textAnnotations']
        for text in texts:
            text_val = text['description']
            print('Found text: "%s"' % text_val)

            all_text += text_val.encode('utf-8') + ', '
            img_text += text_val.encode('utf-8') + '\n'
    except KeyError:
        print("N/A text found")
        img_text += "\nN/A text found"

    print('\n= = = = = Image Processed = = = = =\n')

    # Response parsing
    response["query"] = photo_file
    csv_response = [query, all_labels, all_text]

    response = json.dumps(response, indent=3)
    store_json(response)
    store_csv(csv_response)




if os.isatty(0) == False:
  usage()
  sys.exit(1)
if len(sys.argv) < 2:
  usage()
  sys.exit(1)

# The name of the image file to annotate
file_name = sys.argv[1]
filename_base = os.path.basename(file_name)
print "#",file_name

new_fn = None
a = re.search('\+(.*),(.*)-(.*),(.*)\+',filename_base)
if a:
    # for some reason, motion makes bounding box much bigger in height
    width = float(a.group(1)) *0.9 #* 1.7
    height = float(a.group(2)) * 0.7 #0.85
    centerX = float(a.group(3))
    centerY = float(a.group(4))
    # grab out that subsection
    # convert dog.jpg -crop 78x281+756+260 dog_new.jpg
    new_fn = file_name + "crop.jpg"
    os.system("convert %s -crop %fx%f+%f+%f %s" % (file_name,width,height,centerX-width/2.0,centerY-height/2.0,new_fn))
    #print "# NEW_FN =",new_fn
    file_name = new_fn
              
# Instantiates a client
client = vision.ImageAnnotatorClient()

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations

## if we cropped the image, remove it now
#if new_fn:
#    os.remove(new_fn)

#print('Labels:')
for label in labels:
    print(label.description)


