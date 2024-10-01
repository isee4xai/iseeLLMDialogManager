import business.bt.nodes.node as node
from business.bt.nodes.type import State,TargetType
import business.coordinator as c
from datetime import datetime
import json
import business.storage as s
import business.bt.nodes.html_format as html
import pandas as pd

bosch_id = "65042b68a6093929a203a707"
class ActionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("ACTION "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class Failer(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.message = None

    def toString(self):
        return ("FAILER "+str(self.status) + " " + str(self.id) + " " + str(self.message))

    async def tick(self):
        self.status = State.FAILURE
        return self.status

    def reset(self):
        self.status = State.FAILURE


class Succeder(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.message = None

    def toString(self):
        return ("SUCCEDER "+str(self.status) + " " + str(self.id) + " " + str(self.message))

    async def tick(self):
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        self.status = State.FAILURE


class QuestionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.question = None
        self.variable = None

    def toString(self):
        return ("QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class ConfirmNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("CONFIRM "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No") ]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

        await self.co.send_and_receive(_question, self.variable)
        confirm_response = json.loads(self.co.check_world(self.variable))

        if self.co.is_positive(confirm_response["content"].lower()):
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class GreeterNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.greet_text = {0: "Good Morning ☀️",
                           1: "Good Afternoon",
                           2: "Good Evening"}

    def toString(self):
        return "GREETER " + str(self.status) + " " + str(self.id) + " " + str(self.variable)

    async def tick(self):
        self.start = datetime.now()
        currentTime = datetime.now()
        time_of_day = 0 if currentTime.hour < 12 else 1 if 12 <= currentTime.hour < 18 else 2

        usecase_name = self.co.check_usecase("usecase_name")
        end_user_name = self.co.check_world("user_name")

        if self.co.check_world("initialise") and not self.co.check_world("proceed"):
            _question = self.greet_text[time_of_day] + " " + end_user_name + "!<br>"
            _question += "I am the iSee Chatbot for " + usecase_name + ", "
            _question += "Would you like to proceed?"

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No") ]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

            await self.co.send_and_receive(_question, self.variable)

            proceed_response = json.loads(self.co.check_world(self.variable))

            while not self.co.is_positive(proceed_response["content"].lower()):
                _question = "Would you like to proceed?"
                q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
                q.responseOptions = [s.Response("yes", "Yes"),s.Response("no", "No") ]
                _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
                await self.co.send_and_receive(_question, self.variable)
                proceed_response = json.loads(self.co.check_world(self.variable))
        else:
            _question = "Thank you for using iSee!" +"\n"
            _question += "See you again soon!"

            q = s.Question(self.id, _question, s.ResponseType.INFO.value, False)
            q.responseOptions = None
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

            await self.co.send(_question)

        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status

    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class InitialiserNode(ActionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.variable = "prolific_id"

    def toString(self):
        return ("INITIALISER "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class KnowledgeQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("KNOWLEDGE QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " "
                + str(self.variable))

    async def tick(self):
        # data = self.co.check_ontology(self.question_data)
        # if data:
        #     _question = self.question + "\n" + \
        #         "Please select from "+", ".join(data)+"."
        #     await self.co.send_and_receive(_question, self.variable)
        # else:
        #     await self.co.send_and_receive(self.question, self.variable)

        # response = self.co.check_world(self.variable)
        # if response.lower() in data:
        #     self.co.modify_usecase(self.variable, response.lower())

        self.status = State.SUCCESS
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class NeedQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.question_data = []

    def toString(self):
        return ("NEED QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " "
                + str(self.variable) + " " + str(self.question_data))

    async def tick(self):
        self.start = datetime.now()
        questions = self.co.get_questions()
        if questions:
            q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response(k, q) for k, q in questions.items()]

            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)

            _selected_question = json.loads(self.co.check_world(self.variable))
        
            self.co.modify_usecase(self.variable, _selected_question["id"])
            self.co.modify_intent()
            self.co.modify_strategy()
            self.co.modify_evaluation()
            self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status
        # allow free-text questions?
        # else:
        #     q = s.Question(self.id, self.question, s.ResponseType.OPEN.value, True)
        #     q.responseOptions = None

        #     _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        #     await self.co.send_and_receive(_question, self.variable)

        #     _selected_question = json.loads(self.co.check_world(self.variable))

        #     predict intent based on the free-text question and do modifications


    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class PersonaQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return "PERSONA " + str(self.status) + " " + str(self.id) + " " + str(self.question)

    async def tick(self):
        self.start = datetime.now()
        q = s.Question(self.id, self.question, s.ResponseType.RADIO.value, True)
        personas = self.co.get_personas()
        q.responseOptions = [s.Response(p, html.persona(personas[p])) for p in personas]

        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        _selected_persona = json.loads(self.co.check_world(self.variable))

        self.co.modify_usecase(self.variable, _selected_persona["id"])
        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status

    def reset(self):
        if self.status == State.SUCCESS:
            self.status = State.FAILURE


class EvaluationQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.options = {}
        self.type = None
        self.dimension = None
        self.validators = dict()

    def toString(self):
        return ("EVALUATION QUESTION "+str(self.status) + " " + str(self.id) + " " 
                + str(self.question) + " " + str(self.type) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        responseType = None
        if self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#Open_Question':
            responseType = s.ResponseType.OPEN.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#Number_Question':
            responseType = s.ResponseType.NUMBER.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#MultipleChoiceNominalQuestion':
            responseType = s.ResponseType.CHECK.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#Likert_Scale_Question':
            responseType = s.ResponseType.LIKERT.value 
        elif self.type == 'http://www.w3id.org/iSeeOnto/userevaluation#SingleChoiceNominalQuestion':
            responseType = s.ResponseType.RADIO.value            

        q = s.Question(self.id, self.question, responseType, True)
        q.dimension = self.dimension
        if responseType == s.ResponseType.NUMBER.value:
            q.validators = self.validators
        elif responseType != s.ResponseType.OPEN.value: 
            q.responseOptions = [s.Response(k,v) for k,v in self.options.items()]

        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class ExplainerNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.params = None
        self.endpoint = None
        self.variable = None

    def toString(self):
        return ("EXPLAINER "+ str(self.status) + " " + str(self.id) + " " + str(self.endpoint) + " " + str(self.co))

    async def tick(self):
        self.start = datetime.now()
        random_instance = self.co.check_world("selected_target")
        explainer_query = {
            "instance":random_instance['instance'],
            "type":random_instance['type'],
            "method": self.endpoint,
            "params": self.params
        }
        explainer_result = self.co.get_secure_api_usecase_post("/model/explain", explainer_query)
        if "message" in explainer_result and explainer_result["message"]["status"]!=200:
            raise Exception("Explanation generation error!")
        
        for o in explainer_result["meta"]["output_description"]:
            output_description = explainer_result["meta"]["output_description"][o]
        if explainer_result["type"] == 'image':
            explanation_base64 = explainer_result["explanation"]
            explanation = '<img src="data:image/png;base64,'+explanation_base64+'"/>'
        if explainer_result["type"] == 'html':
            explanation_html = explainer_result["explanation"]
            explanation = explanation_html

        try:
            technique = ''.join(map(lambda x: x if x.islower() else " "+x, self.endpoint.split("/")[-1]))
        except:
            technique = self.endpoint.split("/")[-1]

        _question = '<p>Here is an explanation from '+technique+' Technique</p>'
        _question += explanation
        _question += '<br><p><strong>Explanation Description:</strong> <br>'+output_description+'</p>'

        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("okay", "Okay")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.variable)

        self.status = State.SUCCESS
        self.end = datetime.now()
        if self.co.check_world("usecase_id") == bosch_id:
            self.co.log(node=self, question="{}", variable="{}", selected_target="{}")
        else:
            self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable), selected_target=self.co.check_world("selected_target"))

        return self.status

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class TargetQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("TARGET "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        # select from data upload; data enter; and sampling
        dataset_type = self.co.check_dataset_type()
        is_sampling_response = json.loads(self.co.check_world("selected_target_type"))
        # if sampling an image
        if is_sampling_response["id"] == TargetType.SAMPLE.value and dataset_type == "image":
            random_instance = self.co.get_secure_api_usecase("/dataset/randomInstance", {})

            ai_model_query = {
                "instance":random_instance['instance'],
                "top_classes": '1',
                "type":random_instance['type']
            }

            instance_base64 = random_instance['instance'] 
            instance = '<img width="400" src="data:image/png;base64,'+instance_base64+'"/>'
            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)
            
            if "message" in ai_model_result and ai_model_result["message"]["status"]!=200:
                 raise Exception("Model prediction error!")
            
            _question = '<p>Here is your test instance:</p>'
            _question += instance
            _question += '<br><p>And here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("sampling_image_question", _question)

            # set selected target
            self.co.modify_world(self.variable, random_instance)
        # if sampling and tabular
        elif is_sampling_response["id"] == TargetType.SAMPLE.value and dataset_type == "Multivariate_tabular":
            random_instance = self.co.get_secure_api_usecase("/dataset/randomInstance", {})

            ai_model_query = {
                "instance":random_instance['instance'],
                "top_classes": '1',
                "type":random_instance['type']
            }

            instance_json = random_instance['instance'] 
            instance =  html.table(instance_json)
            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)

            if "message" in ai_model_result and ai_model_result["message"]["status"]!=200:
                 raise Exception("Model prediction error!")

            _question = '<p>Here is your test instance:</p>'
            _question += instance
            _question += '<br><p>And here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("sampling_csv_question", _question)

            # set selected target
            self.co.modify_world(self.variable, random_instance)
        # if sampling and text
        elif is_sampling_response["id"] == TargetType.SAMPLE.value and dataset_type == "text":
            random_instance = self.co.get_secure_api_usecase("/dataset/randomInstance", {})
            ai_model_query = {
                "instance":random_instance['instance'],
                "top_classes": '1',
                "type":random_instance['type']
            }

            instance_json = random_instance['instance'] 
            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)
            if "message" in ai_model_result and ai_model_result["message"]["status"]!=200:
                 raise Exception("Model prediction error!")

            _question = '<p>Here is your test instance:</p>'
            _question += instance_json
            _question += '<br><p>And here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("sampling_csv_question", _question)

            # set selected target
            self.co.modify_world(self.variable, random_instance)       
        # upload image    
        elif dataset_type == "image":
            _question = "Please upload your data instance."
            q = s.Question(self.id, _question, s.ResponseType.FILE_IMAGE.value, True)
            q.responseOptions = []
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, "upload_instance_image")

            upload_instance_image = json.loads(self.co.check_world("upload_instance_image"))
            selected_instance = {}
            selected_instance['instance'] = upload_instance_image["content"].split("base64")[1]
            selected_instance['type'] = 'image'

            ai_model_query = {
                "instance":selected_instance['instance'],
                "top_classes": '1',
                "type":selected_instance['type']
            }

            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)
            if "message" in ai_model_result and ai_model_result["message"]["status"]!=200:
                 raise Exception("Model prediction error!")
            
            _question = '<p>Here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("upload_image_question", _question)

            self.co.modify_world(self.variable, selected_instance)
        # upload csv
        elif dataset_type == "Multivariate_tabular":
            _question = "Please upload your data instance."
            q = s.Question(self.id, _question, s.ResponseType.FILE_CSV.value, True)
            q.responseOptions = []
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, "upload_instance_csv")

            upload_instance_open = json.loads(self.co.check_world("upload_instance_csv"))
            selected_instance = {}
            selected_instance['instance'] = upload_instance_open["content"]
            selected_instance['type'] = 'dict'

            ai_model_query = {
                "instance":selected_instance['instance'],
                "top_classes": '1',
                "type":selected_instance['type']
            }

            ai_model_result = self.co.get_secure_api_usecase_post("/model/predict", ai_model_query)
            if "message" in ai_model_result and ai_model_result["message"]["status"]!=200:
                 raise Exception("Model prediction error!")
            
            _question = '<br><p>Here is the outcome from the AI system:</p>'
            _question += html.table(ai_model_result)

            q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
            q.responseOptions = [s.Response("okay", "Okay")]
            _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
            await self.co.send_and_receive(_question, self.variable)
            self.co.modify_world("upload_csv_question", _question)

            self.co.modify_world(self.variable, selected_instance)
        #other types sample or upload
        else:
            raise Exception("Explanation Target is not selected!")
            
        self.status = State.SUCCESS
        self.end = datetime.now()
        if self.co.check_world("usecase_id") == bosch_id:
            self.co.log(node=self, question="{}", variable="{}")
        else:
            self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status            

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class TargetTypeQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("TARGET TYPE"+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        # select from data upload; data enter; and sampling
        dataset_type = self.co.check_dataset_type()
        _question = "<p>Would you like to upload a data instance?</p>"

        if dataset_type == "image":
            _question = '<p>Would you like to upload a data instance (.jpg, .png) or use inbuilt sampling method to select a data instance for testing?</p>'
        elif dataset_type == "Multivariate_tabular":
            _question = '<p>Would you like to upload a data instance (.csv) or use inbuilt sampling method to select a data instance for testing?</p>'
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("UPLOAD", "I would like to upload"), s.Response("SAMPLE", "I will use sampling")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)

        if dataset_type == "image" or dataset_type == "Multivariate_tabular":
            await self.co.send_and_receive(_question, self.variable)
        else:
            # other datatypes always use sampling
            self.co.modify_world(self.variable, json.dumps({"id": "SAMPLE", "content": "I will use sampling"}))
        
        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self, question=_question, variable=self.co.check_world(self.variable))
        return self.status            

    def reset(self):
        if (self.status == State.SUCCESS):
            self.status = State.FAILURE


class CompleteNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return ("COMPLETE "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE   

class UserQuestionNode(QuestionNode):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.params = None

    def toString(self):
        return ("USER QUESTION "+str(self.status) + " " + str(self.id) + " " + str(self.question) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        selected_q_id = self.co.check_usecase("selected_need")
        selected_q = self.co.get_question_by_id(selected_q_id)
        if "Question" in list(self.params.keys()) and type(self.params["Question"]) is not dict:
            questions = [self.params["Question"].lower()] if ";" not in self.params["Question"].lower() else [f.lower() for f in self.params["Question"].lower().split(";")]
        else:
            questions = [self.params["Question"]["value"].lower()] if ";" not in self.params["Question"]["value"].lower() else [f.lower() for f in self.params["Question"]["value"].lower().split(";")]
        match = selected_q.strip().lower() in [q.strip().lower() for q in questions]
        content = {
            "content": selected_q,
            "id": selected_q_id,
            "match": match
        }
        if match:
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self, variable=content)
        return self.status

    def reset(self):
        self.status = State.FAILURE   
