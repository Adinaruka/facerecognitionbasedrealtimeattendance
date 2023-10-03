import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-c1ccd-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-c1ccd.appspot.com"
})

bucket = storage.bucket()


cap = cv2.VideoCapture(0)
cap.set(3, 640)  # height of webcam image
cap.set(4, 480)  # width of webcam image

imgBackground = cv2.imread('Resources/background.png')
# importing modes in a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
# print(modePathList) for checking elements in list
for Path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, Path)))

# print(len(imgModeList)) # for checking number of elements in list


# load the encoding file
# print("Loading Encode File.. ")
file = open('EncodeFile.p', 'rb')
encodeListKnownwithIDs = pickle.load(file)
file.close()
encodeListKnown, studentIDs = encodeListKnownwithIDs
# print(studentIDs)  for testing the import of ids
# print("Encode file loaded...")

modeType = 0
counter = 0
id = 0
modeType = 0

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_RGB2BGR)

    faceCurFrame = face_recognition.face_locations(imgS)  # current image encodings
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)  # matching saved with current encoding

    # cv2.imshow("Webcam", img) #for capturing the image from webcam

    imgBackground[162:162 + 480, 55:55 + 640] = img  # that much part of background will be considered as image
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]  # that much part for attaching modes
    # cv2.imshow("Face Attendance", imgBackground)  # background of our attendance project
    if faceCurFrame:
        for encodeFace, FaceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                # print("known face Detected")
                # print(studentIDs[matchIndex])  for checking the id of face
                y1, x2, y2, x1 = FaceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIDs[matchIndex]
                if counter == 0:
                    counter = 1
                    modeType = 1
                    imgStudent = []
        if counter != 0:

            if counter ==1:
                # get the data
                studentInfo = db.reference(f'students/{id}').get()
                print(studentInfo)
                # get the images
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # Update the data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'students/{id}')
                    studentInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if modeType !=3:
            if 10<counter<20:
                modeType = 2

            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if counter<=10:

               cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

               cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
               cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
               cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
               cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
               cv2.putText(imgBackground, str(studentInfo['starting_attendance']), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

               # for making name centered
               (w, h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX, 1, 1)
               offset = (414-w)//2
               cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

            imgBackground[175:175+216, 909:909+216] = imgStudent

            counter += 1

            if counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

