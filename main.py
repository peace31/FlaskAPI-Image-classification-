import sys
import tensorflow as tf
from flask import *
from functools import wraps
from flask import send_from_directory
import cv2
import base64
from PIL import Image
import cv2
from PIL import Image
import urllib
import io
import numpy as np
app=Flask(__name__)
app.config.from_object(__name__)
# Take in base64 string and return PIL image
def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))



@app.route('/', methods=['POST'])
def Main():
    if request.method == 'POST':
        imagebase64 = request.form['imagebase64']
        x0 = int(request.form['x0'])
        y0 = int(request.form['y0'])
        x1 =int( request.form['x1'])
        y1 = int(request.form['y1'])
        # url_response = urllib.urlopen(imgpath)
        # img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
        # oimg =   cv2.imdecode(img_array, -1)
        img = stringToImage(imagebase64)
        img.convert('RGB').save('original.jpg')
        oimg=cv2.imread('original.jpg')
        cropimg = oimg[y0:y1,x0:x1]
        cv2.imwrite('crop.jpg', cropimg)
        # Read in the image_data
        image_data = tf.gfile.FastGFile('crop.jpg', 'rb').read()

        # Loads label file, strips off carriage return
        label_lines = [line.rstrip() for line
                       in tf.gfile.GFile("./tf_files/retrained_labels.txt")]

        # Unpersists graph from file
        with tf.gfile.FastGFile("./tf_files/retrained_graph.pb", 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

        with tf.Session() as sess:
            # Feed the image_data as input to the graph and get first prediction
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

            predictions = sess.run(softmax_tensor, \
                                   {'DecodeJpeg/contents:0': image_data})

            # Sort to show labels of first prediction in order of confidence
            top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
            num = 0
            listitem = []
            scoreitem = []
            for node_id in top_k:
                human_string = label_lines[node_id]
                score = predictions[0][node_id]
                listitem.append(human_string)
                scoreitem.append(str(score))
                num += 1
                if (num >= 10):
                    break
        app.config['listitem'] = listitem
        app.config['scoreitem'] = scoreitem
        print(listitem)
        print(scoreitem)
        json_data = json.dumps({'category':listitem,'scoreitem':scoreitem})
        return json_data
    else:
        return None
if __name__=='__main__':
    app.run(debug=True)