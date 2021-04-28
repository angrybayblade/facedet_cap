import cv2
import base64

import numpy as np
# import tensorflow as tf

from flask import Flask, request
from flask_cors import CORS
from numpy.core.fromnumeric import size

from db import Databse, FaceDB, User, new_user, new_user_random

app = Flask(__name__)
db = Databse(root='./data/userdb')
haar = cv2.CascadeClassifier()

# db + new_user_random()

haar.load("./data/haarcascade_frontalface_default.xml")
CORS(app)

def get_face ( image:np.ndarray, pad:int=15 )->np.ndarray:
    *_,(x,y,w,h) = haar.detectMultiScale(image)
    roi =  image[y-pad:y+h, x:x+w].copy()
    roi = cv2.resize(roi,(128, 128), interpolation= cv2.INTER_AREA)
    return roi

def decode_image(string:str)->np.ndarray:
    image = string.replace("data:image/png;base64,","")
    image = np.fromstring(base64.b64decode(image,), np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_ANYCOLOR)
    return image

def encode_image(image:np.ndarray)->str:
    _, string = cv2.imencode('.png',image,)
    string = base64.b64encode(string)
    string = "data:image/png;base64," + string.decode()
    return string

@app.route("/")
def index():
    return 'Hello, World !'

@app.route("/validate", methods=['GET', 'POST'])
def detect():
    data = request.get_json()
    image = data['image']
    image = decode_image(image,)
    roi = get_face(image,)
    
    user, score = db.validate(np.random.uniform(0,1, size=(64)))
    roi_string = encode_image(roi)
    return {
        'roi':roi_string,
        'user':user
    }

@app.route("/order", methods=['GET', 'POST'])
def order():
    data = request.get_json()
    order_id = db.update_order_history( **data )
    return {
        'id':order_id,
    }

if __name__ == '__main__':
    app.run(
        host='localhost',
        port=8080,
        debug=True
    )