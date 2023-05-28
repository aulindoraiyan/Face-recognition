# starting with webcam
import os
import pickle

import cv2
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-a7af8-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-a7af8.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
# graphics are based on the following description

# cap is basically to turn on the webcam
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')
# importing the mode images into a list
folderModePath = 'Resources/Modes'
# In Python, os.listdir() is a function from the os module that returns a list of all the files and directories present in a specified directory.

modePathList = os.listdir(folderModePath)
imgModeList = []

# imread() is a function provided by the OpenCV library in Python. It is used to read and load an image from a file into a NumPy array.

# The imread() function takes the file path of the image as input and returns a NumPy array that represents the image. The array contains the pixel values of the image, which can be manipulated and processed using various OpenCV functions.

# The given code is a loop that iterates over each path in the modePathList list. For each path, it constructs a full
# file path by joining the folderModePath and the current path using the os.path.join() function.
# Then, it uses the cv2.imread() function to read the image from the constructed file path and appends the loaded image to the imgModeList list.The given code is a loop that iterates over each path in the modePathList list. For each path, it constructs a full file path by joining the folderModePath and the current path using the os.path.join() function. Then, it uses the cv2.imread() function to read the image from the constructed file path and appends the loaded image to the imgModeList list.

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))


# webcam run korar jonno code

# cap refers to a video capture object, likely created using cv2.VideoCapture(), which is used to capture video frames from a source (e.g., a webcam or a video file).
# cap.read() is a method of the video capture object that reads the next frame from the video source and returns two values:
# success: A boolean indicating whether the frame was successfully read. It will be True if a frame is available and False if the end of the video source is reached.
# img: The captured frame, stored as an image (typically a NumPy array).


# Load the encoding file
print("Loading Encode File .....")

file = open('EncodeFile.p', 'rb')  # rb is for reading

encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)

print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162: 162 + 480, 55:55 + 640] = img
    imgBackground[44: 44 + 633, 808:808 + 414] = imgModeList[modeType]
    # The cv2.imshow() function is a part of the OpenCV library in Python and is used for displaying images or videos in a
    # window on your computer screen. It stands for "Computer Vision 2 - Image Show."

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDist = face_recognition.face_distance(encodeListKnown, encodeFace)

            # print("Matches", matches)
            # print("faceDis" , faceDist)

            # argmin is a NumPy function that returns the index of the minimum value in an array.

            matchIndex = np.argmin(faceDist)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])

                # bounding box needs the face location. niche otari kaaj
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # the reason amra 4 diye multiply kortesi is becasue amra 1/4th komai nisilam
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                # bbox means bounding box
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)  # rt means rectangle thickness
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:
                if counter == 1:
                    # get the data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)
                    # get the image from storage
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                    # update data of attendance

                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                       "%Y-%m-%d %H:%M:%S")

                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secondsElapsed)

                    if secondsElapsed >30:


                       ref = db.reference(f'Students/{id}')
                       studentInfo['total_attendance'] += 1
                       ref.child('total_attendance').set(studentInfo['total_attendance'])
                       ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44: 44 + 633, 808:808 + 414] = imgModeList[modeType]

                if modeType != 3:

                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44: 44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:
                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

                        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                        cv2.putText(imgBackground, str(studentInfo['Standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        cv2.putText(imgBackground, str(studentInfo['Year:']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        resized_imgStudent = cv2.resize(imgStudent, (216, 216))
                        imgBackground[175: 175 + 216, 909:909 + 216] = resized_imgStudent

                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44: 44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
