import business.bt.nodes.node as node
from business.bt.nodes.type import State
import business.coordinator as c
from datetime import datetime
import json 

class ConditionNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.variables = {}

    def toString(self):
        return ("CONDITION "+str(self.status) + " " + str(self.id) + " " + str(self.variables))

    async def tick(self):
        self.start = datetime.now()
        bool = True
        for k, v in self.variables:
            bool = bool and self.co.check_world(self.k) == v

        if bool:
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE


class EqualNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.variables = {}

    def toString(self):
        return ("EQUAL "+str(self.status) + " " + str(self.id) + " " + str(self.variables))

    async def tick(self):
        self.start = datetime.now()
        bool = True
        for k, v in self.variables.items():
            bool = bool and self.co.check_world(k) == v

        if bool:
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE


class EqualValueNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.variables = {}

    def toString(self):
        return ("EQUAL VALUE "+str(self.status) + " " + str(self.id) + " " + str(self.variables))

    async def tick(self):
        self.start = datetime.now()
        bool = True
        for k, v in self.variables.items():
            stored_val = json.loads(self.co.check_world(k))['id']
            bool = bool and stored_val == v

        if bool:
            self.status = State.SUCCESS
        else:
            self.status = State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE