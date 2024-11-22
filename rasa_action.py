from rasa_sdk import Action
from rasa_sdk.events import SlotSet

class ActionRasaCook(Action):
    def name(self):
        return "action_rasa_cook"

    def run(self, dispatcher, tracker, domain):

        intent = tracker.latest_message["intent"].get("name")

        if intent == "ingredients":
            return [SlotSet("ingredients", True)]

        elif intent == "how_q":
            return [SlotSet("how_q", True)]

        elif intent == "next_step":
            return [SlotSet("next_step", True)]

        elif intent == "deny":
            return [SlotSet("deny", False)]
        return []
