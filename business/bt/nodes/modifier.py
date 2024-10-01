import business.bt.bt as bt
import business.bt.nodes.node as node
import business.bt.nodes.type as s
import business.coordinator as c
from datetime import datetime


class UsecaseModifierNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.variable = None

    def toString(self):
        return ("USECASE MODIFIER "+str(self.status) + " " + str(self.id) + " " + str(self.variable))

    async def tick(self):
        self.start = datetime.now()
        self.co.modify_usecase(self.variable)
        val = self.co.check_usecase(self.variable)
        if val:
            self.status = s.State.SUCCESS
        else:
            self.status = s.State.FAILURE
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        if (self.status == s.State.SUCCESS):
            self.status = s.State.FAILURE


class WorldModifierNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.variable = None
        self.value = None

    def toString(self):
        return ("WORLD MODIFIER "+str(self.status) + " " + str(self.id) + " " + str(self.variable) + " " + str(self.value))

    async def tick(self):
        self.start = datetime.now()
        self.co.modify_world(self.variable, self.value)
        self.status = s.State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        if (self.status == s.State.SUCCESS):
            self.status = s.State.FAILURE
