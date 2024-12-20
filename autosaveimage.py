# -*- coding: utf-8 -*-
"""autosaveimage.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/gist/ChuDuyAnh1307/015685ebc4b1254d94fedd9a3371bfc8/autosaveimage.ipynb
"""

!pip install requests
!pip install requests pymongo
!pip install "pymongo[srv]"

import requests
import time
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import io
from PIL import Image
import hashlib
import pymongo
import threading

uri = "mongodb+srv://2480101001:duyanh123@cluster0.kpoif.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client.camera_db
images_collection = db.images

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def generate_image_url(cam_id):
    return f"http://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx?id={cam_id}"

def save_images_to_mongodb(cam_id, interval=5):
    while True:
        try:
            image_url = generate_image_url(cam_id)
            response = requests.get(image_url)

            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='JPEG')
                timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")

                image_document = {
                    'id': f"image_{timestamp_str}",
                    'url': image_url,
                    'image_base64': image_bytes.getvalue()
                }

                result = images_collection.insert_one(image_document)
                print(f"Camera {cam_id}: Save image {image_document['url']} to MongoDB")
            else:
                print(f"Camera {cam_id} {response.status_code}")

            time.sleep(interval)

        except Exception as e:
            print(f"Camera {cam_id} {e}")
            time.sleep(interval)

def start_camera_threads(camera_ids, interval):
    threads = []
    for cam_id in camera_ids:
        thread = threading.Thread(target=save_images_to_mongodb, args=(cam_id, interval))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        print(f"Start {cam_id}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stop")

# List camera ID
camera_ids = [
    "65e0552f6b18080018db6647",
    "5d8cdc57766c88001718896e",
    "63b66035bfd3d90017eaa48e",
]

start_camera_threads(camera_ids, interval=5)
