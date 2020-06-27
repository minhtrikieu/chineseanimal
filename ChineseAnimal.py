import boto3
client = boto3.client("dynamodb")
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

from datetime import datetime

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak("Welcome to Bay Max. Choose Agenda or Medicine or Help ...").set_should_end_session(False)
        return handler_input.response_builder.response    

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(exception)
        handler_input.response_builder.speak("Sorry, there was some problem. Please try again!!")
        return handler_input.response_builder.response

class AgendaAskIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AgendaAskIntent")(handler_input)   
    def handle(self, handler_input):
        year = handler_input.request_envelope.request.intent.slots['year'].value
        try:
            data = client.get_item(
                TableName="event_baymax_2",
                Key={
                    'id': {
                        'N': year
                    }
                }
            )
        except BaseException as e:
            print(e)
            raise(e)
        speech_text =  "The agenda is: "+ data['Item']['event']['S']+ " on "+data['Item']['date']['S']+" at "+data['Item']['time']['S'] + " in "+ data['Item']['place']['S']
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
        return handler_input.response_builder.response    

class MedicineAskIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("MedicineAskIntent")(handler_input)   
    def handle(self, handler_input):
        number = handler_input.request_envelope.request.intent.slots['year'].value
        try:
            data = client.get_item(
                TableName="medicine_baymax_2",
                Key={
                    'id': {
                        'N': number
                    }
                }
            )
        except BaseException as e:
            print(e)
            raise(e)
        speech_text ="The medicine is: "+data['Item']['medicine']['S'] +" amount " + data['Item']['amount']['S']+ " taken on " + data['Item']['weekday']['S']+" at "+ data['Item']['time']['S']
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
        return handler_input.response_builder.response

class HelpAskIntenttHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HelpAskIntent")(handler_input)   
    def handle(self, handler_input):
        number = handler_input.request_envelope.request.intent.slots['number'].value
        command ="Need Help"
        time =datetime.ctime(datetime.today())
        try:
            data = client.put_item(
                TableName="help_table",
                Item={
                    'id': {
                        'N': number
                    },
                    'command': {
                        'S': command 
                    },
                    'time':{
                        'S': time
                    }
                }
            )

        except BaseException as e:
            print(e)
            raise(e)
        speech_text ="Help Command is sent, waiting till the nurse responds .. " 
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
        return handler_input.response_builder.response

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_request_handler(MedicineAskIntentHandler())
sb.add_request_handler(AgendaAskIntentHandler())
sb.add_request_handler(HelpAskIntenttHandler())

def handler(event, context):
    return sb.lambda_handler()(event, context)