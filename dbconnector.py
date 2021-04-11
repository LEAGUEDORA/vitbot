import pymongo
import json
import settings
import datetime
import pickle

mapped = False
load = None


class extras():
    @classmethod
    def set_mapped(cls, status: str):
        with open("picke.pk") as pickle_file:
            pickle.dump(mapped)



class StaggingDetails():
    client = pymongo.MongoClient(settings.mongo_client_url)
    DataBase = client[settings.Databse]
    facultyData = DataBase[settings.facultyData]
    studentData = DataBase[settings.studentData]
    accessRights = DataBase[settings.accessRights]
    extras = DataBase[settings.extraData]
    events = DataBase[settings.eventsData]
    quickreplies = DataBase[settings.quickreplies]

    @classmethod
    def getFacultyData(cls, dictionary: dict):
        result = cls.facultyData.find_one(dictionary)
        return result
    
    @classmethod
    def validate_Password(cls, dict_ : dict):
        """Sending ID and Password to the database to get the required information."""
        global mapped
        role = None
        result = cls.facultyData.find_one(dict_)
        if result is None:
            result = cls.studentData.find_one(dict_)
            mapped = cls.studentData
            return result, "Student"
        mapped = cls.facultyData
        return result, "Faculty"
    
    @classmethod
    def getAccess(cls, dict_: dict) -> list:
        result = cls.accessRights.find_one(dict_)
        return result
    
    @classmethod
    def change_status(cls, change: dict, Type: str, find: dict) -> dict:
        initial = mapped.find_one(find)
        mapped.update_one(initial, change)
        changed = mapped.find_one(find)
        return initial, changed

    @classmethod
    def get_extras(cls, intent: str) -> list:
        values = cls.extras.find_one({f"{intent}" : {'$exists' : 1}})[intent]
        return values
    
    @classmethod
    def getEvents(cls) -> list:
        list_of_events = []
        for i in cls.events.find():
            list_of_events.append(i)
        return list_of_events
    
    @classmethod
    def getQuickReplies(cls, intent: str) -> list:
        result = cls.quickreplies.find_one({f"{intent}" : {'$exists' : 1}})
        # print(intent, result)
        if result is None:
            return ["Please re-phrase the sentence with proper Department", ""]
        return result[intent]

exec(f"load = {'StaggingDetails'}()")







# (load.validate_Password(dict_ = {"ID" : "CSE01", "Password" : "vit123"}))
# for i in load.getEvents():
#     for j in i:
#         print(j, i[j])
# print(mapped)
# ini, final = load.change_status(find = {"ID" : "19PA1A0534"}, dict_ = {
#     "$set" : {"Status" : "Offline", "last_change": str(datetime.datetime.now())}}, Type = "Student")

# print(ini, final)