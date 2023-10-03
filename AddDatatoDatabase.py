import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-c1ccd-default-rtdb.firebaseio.com/"
})


ref = db.reference('students')  # reference path for database

data = {
    "32145":
        {
            "name": "Elon Musk",
            "major": "Robotics",
            "starting_attendance": 2018,
            "total_attendance": 6,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:22:34"
        },
    "32146":
        {
            "name": "Mark",
            "major": "Metaverse",
            "starting_attendance": 2018,
            "total_attendance": 5,
            "standing": "B",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:22:34"
        },
    "32147":
        {
            "name": "Aditya Singh",
            "major": "IT",
            "starting_attendance": 2020,
            "total_attendance": 10,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:22:34"
        }

}

for key, value in data.items():
    ref.child(key).set(value)