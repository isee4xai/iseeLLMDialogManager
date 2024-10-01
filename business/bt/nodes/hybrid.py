import business.bt.nodes.node as node
from business.bt.nodes.type import State
from business.bt.nodes.action import QuestionNode
import business.storage as s
from datetime import datetime
import json

class ReplacementNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("REPLACEMENT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break
        self.end = datetime.now()            
        self.co.log(node=self)
        return self.status
        # back to parents node

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "I can also show you something completely different"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("no", "I'm okay"),s.Response("yes", "Yes, I wanted something completely different.")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if not self.co.is_positive(confirm_response["id"].lower()):
            return State.SUCCESS
        return State.FAILURE


class VariantNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("VARIANT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break

        self.end = datetime.now()            
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "Would you like to verify using a different explainer?"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("no", "No, I'm okay"),s.Response("yes", "Yes, I would like another explanation")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if not self.co.is_positive(confirm_response["id"].lower()):
            return State.SUCCESS
        return State.FAILURE


class ComplementNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("COMPLEMENT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break
        self.end = datetime.now() 
        self.co.log(node=self)           
        return self.status

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "Would you like another perspective using a different explainer?"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("no", "No, I'm okay"),s.Response("yes", "Yes, I would like another perspective")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if not self.co.is_positive(confirm_response["id"].lower()):
            return State.SUCCESS
        return State.FAILURE


class SupplementNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("SUPPLEMENT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        for idx, child in enumerate(self.children):
            await child.tick()
            # if not last child
            if idx < len(self.children)-1 and await self.navigate() == State.SUCCESS:
                self.status = State.SUCCESS
                break
        
        self.end = datetime.now()            
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()

    async def navigate(self):
        _question = "Would you like more information about this explanation?"
        q = s.Question(self.id, _question, s.ResponseType.RADIO.value, True)
        q.responseOptions = [s.Response("no", "No, I'm okay"),s.Response("yes", "Yes, I would like more information")]
        _question = json.dumps(q.__dict__, default=lambda o: o.__dict__, indent=4)
        await self.co.send_and_receive(_question, self.id)
        confirm_response = json.loads(self.co.check_world(self.id))

        if not self.co.is_positive(confirm_response["id"].lower()):
            return State.SUCCESS
        return State.FAILURE
