from http import client
import business.storage as storage
import business.bt.bt as bt
import ui.interface as interface
import business.log as log
import json
from ml.nlp import SentimentAnalyser
import business.api as api

API_BASE = "https://api-dev.isee4xai.com/api/"


class Coordinator:

    def __init__(self, client_id, socket) -> None:
        self.client_id = client_id
        self.history = dict()
        self.interface = interface.WebSocket(socket)
        self.world = storage.World()
        self.logger = log.Logger()
        self.ontology = storage.Ontology(self)
        self.bt = bt.BehaviourTree(self)
        self.sentiment = SentimentAnalyser.get()

    def init(self, j_data):
        self.world.store("user_token", j_data["user"]["token"])
        self.world.store("usecase_id", j_data["usecase_id"])
        self.world.store("user_name", j_data["user"]["name"])
        # self.user = storage.User(j_data["user"], self)
        self.usecase = storage.Usecase(j_data["usecase_id"], self)

    async def start(self):
        await self.bt.run()

    async def send(self, message):
        await self.interface.send(message)

    async def send_and_receive(self, message, answer_slot):
        answer = await self.interface.send_and_receive(message)
        self.world.store(answer_slot, answer)

    def modify_world(self, _variable, _value):
        self.world.store(_variable, _value)

    def check_world(self, _variable):
        return self.world.get(_variable)

    def modify_usecase(self, _variable, _value=None):
        self.usecase.store(_variable, _value)

    def check_usecase(self, _variable):
        return self.usecase.get(_variable)

    def check_ontology(self, _variable):
        return self.ontology.get(_variable)

    def check_dataset_type(self):
        return self.usecase.dataset_type()

    def get_personas(self):
        return self.usecase.get_personas()

    def get_questions(self):
        return self.usecase.get_questions()

    def get_question_by_id(self, q_id):
        return self.usecase.get_question(q_id)

    def modify_strategy(self):
        new_exp_strategy = self.usecase.get_persona_intent_explanation_strategy()
        self.bt.plug_strategy(new_exp_strategy, "Explanation Strategy")

    def modify_intent(self):
        self.usecase.modify_intent()

    def modify_evaluation(self):
        new_eval_strategy = self.usecase.get_persona_evaluation_strategy()
        self.bt.plug_strategy(new_eval_strategy, "Evaluation Strategy")

    def log(self, node=None, **kwargs):
        self.logger.log(node, **kwargs)

    def get_api(self, url, params):
        return api.request(url, params, {})

    def get_secure_api_usecase(self, path, params):
        headers = {
            "Content-Type": "application/json",
            "x-access-token": self.world.storage.get("user_token")
        }

        url = API_BASE + "usecases_shared/" + self.world.get("usecase_id") + path

        return api.request(url, params, headers)

    def get_secure_api_usecase_post(self, path, body):
        headers = {
            "Content-Type": "application/json",
            "x-access-token": self.world.storage.get("user_token")
        }
        url = API_BASE + "usecases_shared/" + self.world.get("usecase_id") + path
        return api.requestPOST(url, body, headers)

    def get_secure_api_interaction(self):
        headers = {
            "Content-Type": "application/json",
            "x-access-token": self.world.storage.get("user_token")
        }
        url = API_BASE + "interaction/usecase/" + self.world.get("usecase_id")
        data = api.request(url, {}, headers)
        with open('history_all.json', 'w') as f:
            json.dump(data, f)

    def get_secure_api_interaction_post(self, body):
        headers = {
            "Content-Type": "application/json",
            "x-access-token": self.world.storage.get("user_token")
        }
        url = API_BASE + "interaction/usecase/" + self.world.get("usecase_id")
        return api.requestPOST(url, body, headers)

    def reset(self):
        self.world = storage.World()
        self.logger = log.Logger()
        self.ontology = storage.Ontology(self)
        self.bt = bt.BehaviourTree(self)

    def save_conversation(self):
        history = self.logger.json_history()
        body = {
            "interaction": history,
            "usecase_version": self.usecase.get("usecase_version")
        }
        self.get_secure_api_interaction_post(body)

    def is_positive(self, value):
        return self.sentiment.is_positive(value)
