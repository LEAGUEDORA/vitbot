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


dict_ = {
    # '_id': ObjectId('6071df516cade8e4763fc8de'), 
        'Photo': '', 'ID': '19PA1A050I',
        'Name': 'Aremanda Sandy', 
        'Father Name': 'Chilakala Bala Mahesh',
        'Year': 'II', 'DOB': '21-06-2020', 
        'Department': 'CSE', 
        'Mobile': '9515391831', 
        'Email': 'balamahesh.ch@vishnu.edu.in',
        'Status': ' In Lab 308', 'Certificates': {'ML thopu': {'Date': '27-Mar-2021'}, 'Data Science': {'Date': '27-Mar-2021'}},
        'Achievements': {'WiDS': {'Achieved': 'Semi-Finalists', 'Date': '27-Mar-2021', 'Prize': '$500 Cash prize'}, 'EY Hackathon': {'Achieved': 'Finalists', 'Date': '27-Mar-2021', 'Prize': '$5000000000 Cash prize'}},
        'Address': 'Nsrpet, Guntur', 'Mentor': 'Mr. Aremanda Abhijeeth', 'MentorId': 'CSE01', 'DH': 'H', 'Password': '19PA1A0534', 'Clubs': ['NSS', 'NCC', 'IIT', 'JEE', 'AI', 'MUSIC'],
        'Permission Requests': [{'Date': '27-Mar-2021', 'Type': 'Outing', 'To': 'Mentor', 'Status': 'Approved'}], 
        'last_change': '2021-04-09 19:06:41.217482'
        }
import dbconnector
purpose = "faculty_asking_mentor"
supported = getattr(dbconnector.load, "getAccess")({f"{purpose}" : {'$exists' : 1}})
reply = ""
for i in dict_:
    if i in supported[f'{purpose}']:
        if type(dict_[i]) == str and i != "_id":
            reply = reply + "<b>" + i + "</b> : "+ dict_[i] + " " +"<br>"
        elif type(dict_[i] == list) and i != "_id":
            if type(dict_[i]) != list:
                for j in dict_[i]:
                    reply = reply + f"<b> {j} </b>"
                    for k in dict_[i][j]:
                        reply = reply + f"   <b>{k}</b>: {dict_[i][j][k]}"
            else:
                print(i)
                for j in dict_[i]:
                    for k in j:
                        reply = reply + f"{k}: {j[k]}"
                        print(k, j[k])
        else:
            # print(i, dict_[i])
            reply = reply + f"<b> {i} </b> <br>"
            for j in dict_[i]:
                reply  = f"  {dict_[i][j]}"
print(reply)
