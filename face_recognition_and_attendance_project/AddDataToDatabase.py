import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-a7af8-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

# these are written in JSon format. data ekhane "key" and {} etar bhitore is "value"

# again inside data "name" is the key and "dwight is the value
data = {
    # "321654":
    #     {
    #         "name": "Dwight Schrute",
    #         "major": "Business",
    #         "starting_year": 2022,
    #         "total_attendance": 10,
    #         "Standing": "Good",
    #         "Year:": 3,
    #         "last_attendance_time": "2023-5-27 00:54:34"
    #
    #     },

    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2023,
            "total_attendance": 7,
            "Standing": "Good",
            "Year:": 4,
            "last_attendance_time": "2023-5-27 00:54:34"

        },
    "852741":
        {
            "name": "Emily",
            "major": "Business",
            "starting_year": 2022,
            "total_attendance": 4,
            "Standing": "Good",
            "Year:": 3,
            "last_attendance_time": "2023-5-27 00:54:34"

        },
    "136257":
        {
            "name": "Raiyan Mahfuz",
            "major": "CS",
            "starting_year": 2022,
            "total_attendance": 4,
            "Standing": "Great!",
            "Year:": 1,
            "last_attendance_time": "2023-5-27 00:54:34"
        }

}

for key, value in data.items():
    ref.child(key).set(value)
