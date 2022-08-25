#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from keras.preprocessing import image
from keras_vggface.vggface import VGGFace
import numpy as np
from keras_vggface import utils
from  scipy.spatial.distance import euclidean
import cv2
import os
import glob
import pickle
import socket
import time


host="0.0.0.0"
port=5000
max_length=(2**16)+4


sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((host,port))


frame_info=None
buffer_size=None
frame=None

def load_stuff(filename):
    saved_stuff = open(filename, "rb")
    stuff = pickle.load(saved_stuff)
    saved_stuff.close()
    return stuff

def jpeg_healthy_check(buffer_size) -> bool:
    if (buffer_size[:2]==b'\xff\xd8' and buffer_size[-2:]==b'\xff\xd9'):
        return True
    else:
        return False
def list_to_string(_list):
    string=""
    string +=str(_list[0])

    return string


class FaceIdentify(object):
    """
    Singleton class for real time face identification
    """
    CASE_PATH = cv2.data.haarcascades+"haarcascade_frontalface_alt.xml"

    def __new__(cls, precompute_features_file=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FaceIdentify, cls).__new__(cls)
        return cls.instance

    def __init__(self, precompute_features_file=None):
        self.face_size = 224
        self.precompute_features_map = load_stuff(precompute_features_file)
        print("Loading VGG Face model...")
        self.model = VGGFace(model='resnet50',
                             include_top=False,
                             input_shape=(224, 224, 3),
                             pooling='avg')  # pooling: None, avg or max
        print("Loading VGG Face model done")

    @classmethod
    def draw_label(cls, image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale=1, thickness=2):
        size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        x, y = point
        cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (0, 0, 255), cv2.FILLED)
        cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness)

    def crop_face(self, imgarray, section, margin=20, size=224):
        """
        :param imgarray: full image
        :param section: face detected area (x, y, w, h)
        :param margin: add some margin to the face detected area to include a full head
        :param size: the result image resolution with be (size x size)
        :return: resized image in numpy array with shape (size x size x 3)
        """
        img_h, img_w, _ = imgarray.shape
        if section is None:
            section = [0, 0, img_w, img_h]
        (x, y, w, h) = section
        margin = int(min(w, h) * margin / 100)
        x_a = x - margin
        y_a = y - margin
        x_b = x + w + margin
        y_b = y + h + margin
        if x_a < 0:
            x_b = min(x_b - x_a, img_w - 1)
            x_a = 0
        if y_a < 0:
            y_b = min(y_b - y_a, img_h - 1)
            y_a = 0
        if x_b > img_w:
            x_a = max(x_a - (x_b - img_w), 0)
            x_b = img_w
        if y_b > img_h:
            y_a = max(y_a - (y_b - img_h), 0)
            y_b = img_h
        cropped = imgarray[y_a: y_b, x_a: x_b]
        resized_img = cv2.resize(cropped, (size, size), interpolation=cv2.INTER_AREA)
        resized_img = np.array(resized_img)
        return resized_img, (x_a, y_a, x_b - x_a, y_b - y_a)

    def identify_face(self, features, threshold=100):
        distances = []
        for person in self.precompute_features_map:
            person_features = person.get("features")
            distance = euclidean(person_features, features)
            distances.append(distance)
        min_distance_value = min(distances)
        min_distance_index = distances.index(min_distance_value) 
        if min_distance_value < threshold:
            return min_distance_value,self.precompute_features_map[min_distance_index].get("name")
            #time.sleep(0.1)
        else:
            return 0.0,"Unknown"
            #time.sleep(0.1)

    def detect_face(self,remote=False):
        face_cascade = cv2.CascadeClassifier(self.CASE_PATH)

        # 0 means the default video capture device in OS
        if remote==False:
            video_capture = cv2.VideoCapture(0)
            # infinite loop, break by key ESC
        else:
            print('Waiting for connection...')
        while True:

            if remote==False:
                if not video_capture.isOpened():
                    sleep(5)
                    # Capture frame-by-frame
                ret, frame = video_capture.read()
            else:
                data, address = sock.recvfrom(max_length)
                if len(data) < 100:
                    frame_info = pickle.loads(data)

                    if frame_info:
                        nums_of_packs = frame_info["packs"]

                        for i in range(nums_of_packs):
                            data, address = sock.recvfrom(max_length)

                            if i == 0:
                                buffer_size = data
                            else:
                                 buffer_size += data

                        if(jpeg_healthy_check(buffer_size) is False): #Detect  corrupted buffer_size then escap to the next
                            buffer_size=None
                        else:
                            frame_ = np.frombuffer(buffer_size, dtype=np.uint8)
                            buffer_size=None #To avoid stack overflowing
                            frame_= frame_.reshape(frame_.shape[0], 1)

                            frame_ = cv2.imdecode(frame_, cv2.IMREAD_COLOR)
                            frame_ = cv2.flip(frame_, 1)

                            if frame_ is not None and type(frame_)==np.ndarray:
                                frame=frame_



            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)



            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=10,
                minSize=(64, 64)
            )
            # placeholder for cropped faces
            face_imgs = np.empty((len(faces), self.face_size, self.face_size, 3))
            for i, face in enumerate(faces):
                face_img, cropped = self.crop_face(frame, face, margin=10, size=self.face_size)
                (x, y, w, h) = cropped
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 200, 0), 2)
                face_imgs[i, :, :, :] = face_img
            if len(face_imgs) > 0:
                # generate features for each face
                features_faces = self.model.predict(face_imgs)
                #results=utils.decode_predictions(features_faces)[0][0][1]
                predicted_names = [self.identify_face(features_face)[1] for features_face in features_faces]
                confidence=[self.identify_face(features_face)[0] for features_face in features_faces]
                print("Name:{} confidence {:.2f}%".format(predicted_names,float(list_to_string(confidence))))

            # draw results
            for i, face in enumerate(faces):
                label = "{}.{:.2f}%".format(predicted_names[i],confidence[i])
                self.draw_label(frame, (face[0], face[1]), label)

            cv2.imshow('DeepFlicc Window', frame)
            if cv2.waitKey(5) == 27:  # ESC key press
                break
        # When everything is done, release the capture
        video_capture.release()
        cv2.destroyAllWindows()



def main():
    face = FaceIdentify(precompute_features_file="./data/precompute_features.pickle")
    face.detect_face(remote=True)

if __name__ == "__main__":
    main()
