# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk.events import FollowupAction, SlotSet, AllSlotsReset
from rasa_sdk.types import DomainDict
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
import dbconnector
import yaml
import datetime

"""Load the domain file"""
with open("domain.yml") as domain:
    domain = yaml.load(domain, Loader = yaml.SafeLoader)

"""Read all Slots from domain file"""
slots = []
for i in domain:
    if i == "slots":
        for j in domain[i]:
            slots.append(j)





class extras():

    @classmethod
    def get_slot_values(cls, formName: str) -> list:
        """
        Returns all the slots that are present in the domain file under particular form
        formName: name of the form that is in the domain.yml file
        """
        list_of_values = []
        for i in domain:
            if i == "forms":
                for j in domain[i]:
                    if j == "greet":
                        for k in domain[i][j]:
                            list_of_values.append(k)
        return list_of_values
    
    @classmethod
    def stringify(cls, dict_: dict, purpose: str, statement = "Here is a brief description of you") -> str:
        """
        Returns a string with a proper format from Dictionary(JSON)
        dict_: The original dictionary/JSON that recieved from the database
        purpose: The name of the purpose that is mapped in the database to fetch the access right
        statement: The initial line in the string that is to be printed. "Default"
        """
        reply = statement + "<br>"
        supported = getattr(dbconnector.load, "getAccess")({f"{purpose}" : {'$exists' : 1}})
        for i in dict_:
            if i in supported[f'{purpose}']:
                if type(dict_[i]) == str and i != "_id":
                    reply = reply + "<b>" + i + "</b> : "+ dict_[i] + " " +"<br>"
                elif type(dict_[i] == list) and i != "_id":
                    reply = reply + f"<b> {i}: </b><br>"
                    if type(dict_[i]) != list:
                        for j in dict_[i]:
                            reply = reply + f"<b> {j} </b> <br>"
                            for k in dict_[i][j]:
                                reply = reply + f"   <b>{k}</b>: {dict_[i][j][k]} <br>"
                    else:
                        reply = reply + f"<b>{i}</b><br>"
                        for j in dict_[i]:
                            for k in j:
                                reply = reply + f"{k}: {j[k]} <br>"
                else:
                    reply = reply + f"<b> {i} </b> <br>"
                    for j in dict_[i]:
                        reply  = f"  {dict_[i][j]} <br>"
        return reply
    
    @classmethod
    def createDropdown(cls, intent: str, slot_name: str, values: list) -> list:
        """ 
        Creates a drop down menu from the recieved configuration
        intent: The intent that must be printed on the final output
        slot_name: name of the entity/slot name that needs to be on the output
        values: list of values that needs to be delivered to the UI
        final output: "/intent{'intent' : 'value(s)'}"
        """
        lst = []
        for i in values:
            temp = {}
            temp["label"] = i
            temp['value'] = "/" + intent + "{" + f'{slot_name}' + " : " + f'{i}' + "}"
            lst.append(temp)
        return lst

    @classmethod
    def createbuttons(cls, intent: str, slot_name: str, values: list) -> list:
        """ 
        Creates buttos from the recieved configuration
        intent: The intent that must be printed on the final output
        slot_name: name of the entity/slot name that needs to be on the output
        values: list of values that needs to be delivered to the UI
        final output: "/intent{'intent' : 'value(s)'}"
        """
        lst = []
        for i in values:
            temp = {}
            temp["title"] = i
            temp["payload"] = "/" + intent + "{\"" + slot_name + "\":\" "+i+" \"}"
            lst.append(temp)
        return lst

    @classmethod
    def createCardsCarousel(cls, functionName: str) -> list:
        """ 
        Creates Cards from the recieved configuration from the database for events
        functionName: The name of the function in dbconnector.py
        """
        lst = []
        events_list = getattr(dbconnector.load, f"{functionName}")()
        for i in events_list:
            dict_ = {}
            for j in i:
                if j != "_id":
                    dict_[j] = i[j]
                    if j == "title":
                        dict_[j] = f"<a href = {i[j]} target = '_blank'> {i['name']} </a> "
            lst.append(dict_)
        return lst

    @classmethod
    def changeName(cls, nameOfDepartment: str) -> str:
        """
        Helps to correct name of the department that is given by the user
        nameOfDepartment: The name of the department that is given by the user
        """
        nameOfDepartment = nameOfDepartment.split(" ")
        nameOfDepartment = nameOfDepartment[0]
        alisases = {
            "cse" : ["cse", "computer"],
            "ece" : ["ece", "electrical"],
            "civil" : ["civil", "cvc"],
            "mech" : ["mech", "mechanical"],
            "it" : ["it", "information"],
            "eee" : ["eee"]
        }
        for i in alisases:
            if nameOfDepartment in alisases[i]:
                return i
        return None


class ValidateFormGreet(FormValidationAction):
    
    def name(self) -> Text:
        return "validate_greet"

    def validate_Password(self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validating Password"""
        get_slot_values = extras.get_slot_values("greet")  #Gets the slot values of greet form
        slot_values = {} # Initializing the dictionary to append slot values
        for i in get_slot_values:
            slot_values[i] = tracker.get_slot(f"{i}")
        result, Type = getattr(dbconnector.load, self.validate_Password.__name__)(slot_values)  # Getting the result from the database

        if result is None: # If there are no one with this property restart everything
            dispatcher.utter_message(text = "Please make sure that you have added valid credentials.")
            for i in get_slot_values:
                slot_values[i] = None
            return slot_values  # Returning empty dictionary and convert everything to None
        Authenticate =  tracker.get_slot("Authenticate")
        if Authenticate is None:
            slot_values['Authenticate'] = "True"  # Setting Authenticate slot to true for Furture purpose
            slot_values['Type'] = Type #Setting Type for indicating Student or Faculty to gain access rights
            for slot in slots:
                if slot in result:
                    try:
                        slot_values[slot] = result[slot]
                    except:
                        print("Do Nothing")
                    else:
                        slot_values[slot] = result[slot]
            dispatcher.utter_message(text = "Login Successful") # Telling the user that login is sucessfull
            dispatcher.utter_message(response =  "greet") # Greeting the user with greet
            purpose = f"{Type}_login"
            stringed = extras.stringify(dict_ = result, purpose= purpose) # Making a string with user details
            dispatcher.utter_message(text = stringed, image = result['Photo']) # Sending the user with the made string and image
            dispatcher.utter_message(text = "Here are some of the <b>Latest Events</b> going in our College. Please do have a look at them..")
            message = extras.createCardsCarousel(functionName = "getEvents") #Creating a cards carousel 
            data = {
                "payload" : 'cardsCarousel',
                "data"  :message
            }
            dispatcher.utter_message(json_message = data  ) #sending the UI the cards carousel data
        else:
            #If the user is already logged in and greets the bot again, the bot replies with the greet intent
            dispatcher.utter_message(response= "utter_greet")

        return slot_values


class ActionChangeStatus(Action):

    def name(self) -> Text:
        return "action_change_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Status of the user will be changed from here"""
        intent = tracker.get_intent_of_latest_message(skip_fallback_intent = True) #Get the latest intent
        change_status = tracker.get_slot("change_status") # Value that the user wants to change
        authenticate = tracker.get_slot("Authenticate") # Checking whether thr user is logged in or not
        if authenticate is not None: # If logged in 
            if change_status is not None:  # if user already said status to be changed
                # Creating dictionary that needs to be changed
                to_change = {
                    "$set" : {
                        "Status" : change_status,
                        "last_change" : str(datetime.datetime.now())
                    }
                }
                find = {
                    "ID" : tracker.get_slot("ID")
                }
                # Sending the data to the DataBase
                initial, chenged_tp = getattr(dbconnector.load, "change_status")(change = to_change, Type = tracker.get_slot("Type"), find = find)
                dispatcher.utter_message(text = f"Status has been changed to <b>{change_status}</b>")
                #Setting the slots to required formats
                return [SlotSet("Status", change_status), SlotSet("last_change", str(datetime.datetime.now())), SlotSet("change_status", None)]
            
            else:
                #If the user didn't enter anything about the status then the bot pops up with some values from database
                #Creating dropdown menu
                data = extras.createDropdown(intent = intent, slot_name = "change_status", values = getattr(dbconnector.load, "get_extras")(intent = intent))
                message = {"payload" : "dropDown", "data":data}
                dispatcher.utter_message(text = "Please select the status that is to be changed from below list", json_message = message)
        else:
            # If the user didn't login then it doesn't allow the user to login
            dispatcher.utter_message(text = "You have not logged in. Please log in and try again", buttons = extras.createbuttons(intent = "greet", slot_name = "dummy", values = ["Login"]))
        
        return []




class ActionBye(Action):

    def name(self) -> Text:
        return "action_goodbye"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Dispatches good bye message and Clears all the slots indicating that the session is completed"""
        dispatcher.utter_message(response = "utter_goodbye")
        return [AllSlotsReset()]


class ActionlatestEvents(Action):
    
    def name(self) -> Text:
        return "action_latest_events"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Getting the list of events and seding it to the user in a Card Crousel Format"""
        dispatcher.utter_message(text = "Here are some of the <b>Latest Events</b> going in our College. Please do have a look at them..")
        message = extras.createCardsCarousel(functionName = "getEvents") # Creating cards carousel
        data = {
            "payload" : 'cardsCarousel',
            "data"  :message
        }
        dispatcher.utter_message(json_message = data  )
        return []

class ActionQuickReplies(Action):
    
    def name(self) -> Text:
        return "action_quick_replies"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Quick replies are sent from here"""
        intent = str(tracker.get_intent_of_latest_message(skip_fallback_intent = True)).lower() # Getting the intent
        if intent is not None and not intent.startswith("c_"): #Cheks that the intent is Not none and doesnot starts with c_. "c_" indicates that the intent is in confused state
            result = getattr(dbconnector.load, "getQuickReplies")(intent = intent)
            dispatcher.utter_message(text = result[0], image = result[1])
        elif intent is not None and intent.startswith("c_"):
            only_intent = intent[2:intent.rfind("_")]
            slotname = intent[intent.rfind("_")+1:]
            slotname = tracker.get_slot(slotname)
            finalName = extras.changeName(nameOfDepartment = slotname)
            if finalName is not None:
                result = getattr(dbconnector.load, "getQuickReplies")(only_intent+ "_" +finalName)
                dispatcher.utter_message(text = result[0], image = result[1])
            else:
                #If there is no proper department defined it asks for the department 
                dispatcher.utter_message(text = "Please ask the same question again with proper Department Name")
        return []


class ActionMentoring(Action):

    def name(self) -> Text:
        return "action_mentorslist"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Getting the mentor list from the database for both student and the faculty"""
        authenticate = tracker.get_slot("Authenticate")
        if authenticate is not None:  #Cheks the autherization
            Type = tracker.get_slot("Type") #Gets whether the logged in person is Student or Faculty
            ID = tracker.get_slot("ID") #Gets the ID of the user
            if Type == "Student":
                """If the user is a student then the bot replies his/her mentor details with proper access rights set by the College"""
                getMentorID = getattr(dbconnector.load, "validate_Password")({"ID" : ID})[0]['MentorId'] #getting mentor ID that is mapped in the database
                dispatcher.utter_message(text = "Here are your Mentor details") 
                getmentorDetails = getattr(dbconnector.load, "validate_Password")({"ID": getMentorID})[0] #getting the details of the mentor
                accessname = "student_asking_mentor" #Mapped in the database
                string = extras.stringify(dict_= getmentorDetails, purpose = accessname, statement = "Here are the details of your Mentor") #Converting the dictionary to a string in a readable format
                dispatcher.utter_message(text = string, image = getmentorDetails['Photo'] )  #Dispatching the message with Image and Formatted string
            else:
                """If the user is a Faculty then the he/she can get all the details of thier mentoring students"""
                getmentoringStudents = getattr(dbconnector.load, "validate_Password")({"ID" : ID}) [0]["MentoringStudents"] #Getting the student details from the database
                for i in getmentoringStudents:  #Looping through every student details that are recieved from the database
                    getStudentDetals = getattr(dbconnector.load, "validate_Password")({"ID" : i})[0] #Getting each student details from their ID
                    accessname = "faculty_asking_mentor" #mapped in database for access rights
                    string = extras.stringify(dict_= getStudentDetals, purpose = accessname, statement = "Here are the students under you:")  #Converting into beautiful string from the dictionary recieved from the database
                    dispatcher.utter_message(text = string, image = getStudentDetals['Photo']) #Dispathcing with stringed text and image
        return []

