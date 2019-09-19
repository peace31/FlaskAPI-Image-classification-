
import sys
import tensorflow as tf
from flask import *
from flask import send_from_directory
import cv2
import base64
from PIL import Image
import numpy as np
from flask import Flask
from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import boto3
import boto
from boto.s3.key import Key as key1
import json
from ast import literal_eval
from boto.file import Key
from boto.s3.connection import S3Connection
import io
import os
import shutil
import requests
import retrain
import glob

app = Flask(__name__)

access_key='AKIAJXZ46SSHE7JAXMKA'
secret_key='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'


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/')
def hello_world():
  return 'Hello from 2'
def stringToImage(base64_string):
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))
def get_image_url(fullpath):
    wow_data_bucket = "objjson-tmp"
    session = boto3.Session(access_key, secret_key)
    s3 = session.client('s3')
    file_key = fullpath
    obj = s3.get_object(Bucket=wow_data_bucket, Key=file_key)
    auctiondata = json.loads(obj['Body'].read().decode('utf-8'))
    return auctiondata

def save_image(categories):
    if(len(categories)>1):
        path = r'/home/ubuntu/flaskapp/tf_files/flower_photos/' 
        # return 'ok'
        os.chdir(path)
        for root, dirs, files in os.walk(".", topdown = False):
            for name in dirs:
                shutil.rmtree(os.path.join(path, name))
                # return os.path.join(path, name)

        conn = S3Connection(access_key,secret_key)
        bucket = conn.get_bucket('objjson-tmp')
        for i in range(len(categories)):
            fname=categories[i]
            
            for obj in bucket.list(prefix=fname+'/'):
                fullpath=obj.name.encode('utf-8')
                if('.json' in fullpath):
                    imgjson=get_image_url(fullpath)
                    imgurl=imgjson['croppedimg']
                    # return imgurl
                    response = requests.get(imgurl, stream=True)
                    response.raw.decode_content = True
                    img = Image.open(response.raw)
                    # img.save(imgname)
                    # return 'ok'
                    cropstatus=imgjson['cropped']
                    imgp=imgurl.split('/')
                    imgname=imgp[len(imgp)-1]
                    newpath=path+fname
                    if not os.path.exists(newpath):
                            os.makedirs(newpath)
                    if(cropstatus=='true'):
                        # return 'ok'
                        saved_path = newpath+'/'+imgname
                        img.save(saved_path)
                    else:

                        # x0=int(imgjson['x0'])
                        # x1=int(imgjson['x1'])
                        # y0=int(imgjson['y0'])
                        # y1=int(imgjson['y1'])
                        saved_path = newpath+'/'+imgname
                        # img1=img.crop((x0,y0, x1, y1))
                        img.save(saved_path)
                        # return saved_path
        return "success"
    return "None"                   
def save_data():

    bucketName="trainedbucket"
    fileName='/home/ubuntu/flaskapp/tf_files/retrained_graph.pb'
    file = open(fileName,'rb')

    conn = boto.connect_s3(access_key,secret_key)
    bucket = conn.get_bucket(bucketName)
    
    #Get the Key object of the bucket
    k = key1(bucket)
    
    #Crete a new key with id as the name of the file
    k.key='retrained_graph.pb'
    #Upload the file
    result = k.set_contents_from_file(file)

    fileName='/home/ubuntu/flaskapp/tf_files/retrained_labels.txt'
    file = open(fileName,'r')
    #Crete a new key with id as the name of the file
    k.key='retrained_labels.txt'
    #Upload the file
    result = k.set_contents_from_file(file)                        
                        
                    



@app.route('/train', methods=['POST'])
@crossdomain(origin='*')
def train():
    if request.method == 'POST':
        path=request.form['path']
        wow_data_bucket = "objtrainingconfig"
        session = boto3.Session(access_key, secret_key)

        s3 = session.client('s3')
        file_key = path
        obj = s3.get_object(Bucket=wow_data_bucket, Key=file_key)

        auctiondata = json.loads(obj['Body'].read().decode('utf-8'))
        # return 'ok'
        categories=auctiondata['categories']
        if(len(categories)>1):
            rtext=save_image(categories)
            # return rtext
            # return json.dumps({'category':rtext})
            if(rtext=='success'):
                xxt=retrain.app_run()
                # return json.dumps({'process':xxt})
                if(xxt=='None'):
                    return json.dumps({'process':'Failed'})
                else:
                    save_data()
                    return json.dumps({'process':'success'})
        return json.dumps({'process':'Failed'})
            
        
        # print(auctiondata)
@app.route('/main', methods=['POST'])
@crossdomain(origin='*')
def Main():
    if request.method == 'POST':

        imagebase64 = request.form['imagebase64']

        x0 = int(request.form['x0'])
        y0 = int(request.form['y0'])
        x1 =int( request.form['x1'])
        y1 = int(request.form['y1'])
        img = stringToImage(imagebase64)

        img1=img.convert('RGB')
        
        img2 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
        
        cropimg = img2[y0:y1,x0:x1]
        image_data = cv2.imencode('.jpg', cropimg)[1].tostring()
        # Loads label file, strips off carriage return
        label_lines = [line.rstrip() for line
                       in tf.gfile.GFile("/home/ubuntu/flaskapp/tf_files/retrained_labels.txt")]
        # Unpersists graph from file
        with tf.gfile.FastGFile("/home/ubuntu/flaskapp/tf_files/retrained_graph.pb", 'rb') as f:
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
    
if __name__ == '__main__':
  app.run(debug=True, port=80)