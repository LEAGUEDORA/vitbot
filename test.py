# import yaml

# """Load the domain file"""
# with open("domain.yml") as domain:
#     domain = yaml.load(domain)



# for i in domain:
#     if i == "slots":
#         for j in domain[i]:
#             # lst.append(j)
#             print(j)
# # import dbconnector


# # class extras():

# #     @classmethod
# #     def stringify(cls, dict_: dict, purpose: str) -> str:
# #         """Returns a string with a proper format from Dictionary"""
# #         reply = "Here is a brief description of you"
# #         supported = getattr(dbconnector.load, cls.stringify.__name__)({f"{purpose}" : {'$exists' : 1}})
# #         print(supported)
# #         for i in dict_:
# #             if i in supported['Faculty_login']:
# #                 reply = reply + i + dict_[i] + " \n"
# #         return reply


# # print(extras.stringify(dict_= {"Name" : "Gera Abhishek"}, purpose = "Faculty_login"))

# def create(intent: str, slot: str, values : list) -> list:
#     lst = []
#     for i in values:
#         temp = {}
#         temp['label'] = i
#         temp['value'] = "/" + intent + "{\"" + slot + "\":\" " + i + " \"}"
#         lst.append(temp)
#     return lst

# print(create(intent = "inform", slot = "slot_name", values = ['option1', 'option2']))


a = "c_HOD_currentdept"
intent = a[2:a.rfind("_")]
slot = a[a.rfind("_")+1:]
print(intent, slot)