import business.bt.nodes.node as node
from business.bt.nodes.type import State
from datetime import datetime

class PriorityNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("PRIORITY "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        for child in self.children:
            if (await child.tick() == State.SUCCESS):
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


class SequenceNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = []

    def toString(self):
        kids = " " + (str(len(self.children)))
        return ("SEQUENCE "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        self.status = State.SUCCESS
        for child in self.children:
            if (await child.tick() == State.FAILURE):
                self.status = State.FAILURE
                break

        # back to parents node
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE
        for child in self.children:
            child.reset()


class EvaluationStrategyNode(SequenceNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return "EVALUATION STRATEGY " + str(self.status) + " " + str(self.id)

    async def tick(self):
        self.start = datetime.now()
        self.status = State.SUCCESS
        for child in self.children:
            if (await child.tick() == State.FAILURE):
                # self.status = State.FAILURE
                break

        # back to parents node
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status


class ExplanationStrategyNode(SequenceNode):
    def __init__(self, id) -> None:
        super().__init__(id)

    def toString(self):
        return "EXPLANATION STRATEGY " + str(self.status) + " " + str(self.id)

    async def tick(self):
        self.start = datetime.now()
        self.status = State.SUCCESS
        for child in self.children:
            await child.tick()
        
        # if needs remaining, set need incomple when exit
        if self.co.get_questions() and self.co.check_usecase("selected_need") != "none":
            self.co.modify_world("need", False)
            # back to parents node
            self.status = State.FAILURE
        else:
            self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status