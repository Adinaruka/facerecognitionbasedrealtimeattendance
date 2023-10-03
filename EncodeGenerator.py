import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-c1ccd-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendance-c1ccd.appspot.com"
})

# importing student images
folderPath = 'Images'
PathList = os.listdir(folderPath)
imgList = []
studentIDs = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # print(path)
    # print(os.path.splitext(path)[0])
    studentIDs.append(os.path.splitext(path)[0])
# print(len(imgList))
# print(studentIDs)

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)  #  bgr to rgb as opencv uses bgr and face recognition uses rgb
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownwithIDs =[encodeListKnown, studentIDs]
print("encoding complete..")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownwithIDs, file)
file.close()
print("file saved")
