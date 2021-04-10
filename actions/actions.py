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
        """Returns all the slots that are present in the domain file under particular form"""
        list_of_values = []
        for i in domain:
            if i == "forms":
                for j in domain[i]:
                    if j == "greet":
                        for k in domain[i][j]:
                            list_of_values.append(k)
        return list_of_values
    
    @classmethod
    def stringify(cls, dict_: dict, purpose: str) -> str:
        """Returns a string with a proper format from Dictionary"""
        reply = "Here is a brief description of you  <br>"
        supported = getattr(dbconnector.load, cls.stringify.__name__)({f"{purpose}" : {'$exists' : 1}})
        for i in dict_:
            if i in supported[f'{purpose}']:
                reply = reply + "<b>" + i + "</b> : "+ dict_[i] + " " +"<br>"
        return reply
    
    @classmethod
    def createDropdown(cls, intent: str, slot_name: str, values: list) -> list:
        lst = []
        for i in values:
            temp = {}
            temp["label"] = i
            temp['value'] = "/" + intent + "{" + f'{slot_name}' + " : " + f'{i}' + "}"
            lst.append(temp)
        return lst

    @classmethod
    def createbuttons(cls, intent: str, slot_name: str, values: list) -> list:
        lst = []
        for i in values:
            temp = {}
            temp["title"] = i
            temp["payload"] = "/" + intent + "{\"" + slot_name + "\":\" "+i+" \"}"
            lst.append(temp)
        return lst

    @classmethod
    def createCardsCarousel(cls):
        lst = []
        events_list = getattr(dbconnector.load, "getEvents")()
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
    def changeName(cls, nameOfDepartment):
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
            dispatcher.utter_message(text = "Login Successful")
            dispatcher.utter_message(response =  "greet")
            purpose = f"{Type}_login"
            stringed = extras.stringify(dict_ = result, purpose= purpose)
            dispatcher.utter_message(text = stringed, image = result['Photo'])
            dispatcher.utter_message(text = "Here are some of the <b>Latest Events</b> going in our College. Please do have a look at them..")
            message = extras.createCardsCarousel()
            data = {
                "payload" : 'cardsCarousel',
                "data"  :message
            }
            dispatcher.utter_message(json_message = data  )
        else:
            dispatcher.utter_message(response= "utter_greet")
            dispatcher.utter_message(text = "Here are some of the <b>Latest Events</b> going in our College. Please do have a look at them..")
            message = extras.createCardsCarousel()
            data = {
                "payload" : 'cardsCarousel',
                "data"  :message
            }
            dispatcher.utter_message(json_message = data)

        return slot_values


class ActionChangeStatus(Action):

    def name(self) -> Text:
        return "action_change_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message(skip_fallback_intent = True)
        change_status = tracker.get_slot("change_status")
        authenticate = tracker.get_slot("Authenticate")
        if authenticate is not None:
            if change_status is not None:
                to_change = {
                    "$set" : {
                        "Status" : change_status,
                        "last_change" : str(datetime.datetime.now())
                    }
                }
                find = {
                    "ID" : tracker.get_slot("ID")
                }
                initial, chenged_tp = getattr(dbconnector.load, "change_status")(change = to_change, Type = tracker.get_slot("Type"), find = find)
                dispatcher.utter_message(text = f"Status has been changed to <b>{change_status}</b>")
                return [SlotSet("Status", change_status), SlotSet("last_change", str(datetime.datetime.now())), SlotSet("change_status", None)]
            
            else:
                data = extras.createDropdown(intent = intent, slot_name = "change_status", values = getattr(dbconnector.load, "get_extras")(intent = intent))
                message = {"payload" : "dropDown", "data":data}
                dispatcher.utter_message(text = "Please select the status that is to be changed from below list", json_message = message)
        else:
            dispatcher.utter_message(text = "You have not logged in. Please log in and try again", buttons = extras.createbuttons(intent = "greet", slot_name = "dummy", values = ["Login"]))
        
        return []




class ActionBye(Action):

    def name(self) -> Text:
        return "action_goodbye"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response = "utter_goodbye")
        return [AllSlotsReset()]


class ActionlatestEvents(Action):
    
    def name(self) -> Text:
        return "action_latest_events"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text = "Here are some of the <b>Latest Events</b> going in our College. Please do have a look at them..")
        message = extras.createCardsCarousel()
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
        intent = str(tracker.get_intent_of_latest_message(skip_fallback_intent = True)).lower()
        if intent is not None and not intent.startswith("c_"):
            result = getattr(dbconnector.load, "getQuickReplies")(intent = intent)
            dispatcher.utter_message(text = result[0], image = result[1])
        elif intent is not None and intent.startswith("c_"):
            only_intent = intent[2:intent.rfind("_")]
            slotname = intent[intent.rfind("_")+1:]
            slotname = tracker.get_slot(slotname)
            print(only_intent, slotname)
            finalName = extras.changeName(nameOfDepartment = slotname)
            if finalName is not None:
                result = getattr(dbconnector.load, "getQuickReplies")(only_intent+ "_" +finalName)
                dispatcher.utter_message(text = result[0], image = result[1])
            else:
                dispatcher.utter_message(text = "Please ask the same question again with proper Department Name")
        return []