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
import json
from ast import literal_eval
from boto.file import Key
from boto.s3.connection import S3Connection
import io
import urllib.request as urp