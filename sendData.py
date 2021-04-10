import pymongo
import settings
import json


client = pymongo.MongoClient(settings.mongo_client_url)
DataBase = client[settings.Databse]
facultyData = DataBase[settings.facultyData]
studentData = DataBase[settings.studentData]
accessRights = DataBase[settings.accessRights]


class sendData():

    @classmethod
    def sendFacultyData(cls, dict_: dict):
        facultyData.insert_one(dict_)
    
    @classmethod
    def sendStudentData(cls, dict_: dict):
        studentData.insert_one(dict_)



with open("student_model.json") as student_model:
    student_model = json.load(student_model)
sendData.sendStudentData(student_model)