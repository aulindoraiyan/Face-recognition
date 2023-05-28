import os
# The os module provides a way to interact with the operating system,
# allowing you to perform various operating system-dependent operations like file and directory manipulation,
# process management, environment variables, etc.

import cv2
import face_recognition
#
import pickle
#
import firebase_admin
import numpy as np
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-a7af8-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-a7af8.appspot.com"
})

# importing the student images
folderPath = 'Images'

pathList = os.listdir(folderPath)
print(pathList)
# print("********")
imgList = []

studentIds = []


for path in pathList:
    # In each iteration, the current path is assigned to the variable path.
    imgList.append(cv2.imread(os.path.join(folderPath,path)))

    studentIds.append(os.path.splitext(path)[0])
    print(path)

    # The code os.path.splitext(path)[0] is used to extract the filename without the file extension from the path variable.
    print(os.path.splitext(path)[0])
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)  # we are using blob to actually send it
    blob.upload_from_filename(fileName)



print(studentIds)


# we are gonna loop through every images and then encode it

# def is a keyword in Python used to define a function.
# findEncodings is the name of the function being defined.
# You can choose any valid name for your function.
# (imagesList) is the parameter list enclosed in parentheses.
# In this case, imagesList is a parameter that will be passed to the function. It is expected to be a list containing images.


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

# def findEncodings(imagesList):
#     encodeList = []
#     for img in imagesList:
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#         face_encodings = face_recognition.face_encodings(img)
#         if len(face_encodings) > 0:
#             encode = face_encodings[0]
#             encodeList.append(encode)
#         else:
#             print("No face detected in image:", img)
#
#     return encodeList


print("Encoding Started...")
# encodeListKnown = findEncodings(imgList)
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print(encodeListKnown)
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")