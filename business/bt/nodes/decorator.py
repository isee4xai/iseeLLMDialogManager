import business.bt.nodes.node as node
from business.bt.nodes.type import State
from datetime import datetime

class InverterNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = None

    def toString(self):

        return ("INVERTER "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        if (await self.children[0].tick() == State.SUCCESS):
            self.status = State.FAILURE
        else:
            self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE
        self.children[0].reset()


class LimitActivationNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.timesActivated = 0
        self.limit = None
        self.children = None

    def toString(self):

        return ("LIMIT "+str(self.status) + " " + str(self.id))

    async def tick(self):
        self.start = datetime.now()
        if (self.timesActivated < self.limit):
            self.timesActivated += 1
            self.status = await self.children[0].tick()
        else:
            self.status = State.SUCCESS
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE
        self.children[0].reset()


class RepeatNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = None

    def toString(self):
        return ("REPEAT "+str(self.status) + " " + str(self.id))

    async def tick(self, predecessor: "Node"):
        return self.status

    def reset(self):
        self.status = State.FAILURE
        self.children[0].reset()


class RepTillFailNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = None

    def toString(self):
        return ("REP TILL FAIL "+str(self.status) + " " + str(self.id))

    async def tick(self, predecessor: "Node"):
        self.start = datetime.now()
        if (not (predecessor in self.children[0])):

            # we check the first child (if it has one)
            if (len(self.children) > 0):
                #print("go in first child")
                self.statut = State.RUNNING
                await self.children[0].tick()

            else:
                #print("no child")
                self.statut = State.FAILURE

        else:
            self.status = State.SUCCESS
            while (self.status == State.SUCCESS):

                self.status = await self.children[0].tick()
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE
        self.children[0].reset()


class RepTillSuccNode(node.Node):
    def __init__(self, id) -> None:
        super().__init__(id)
        self.children = None

    def toString(self):
        return ("REP TILL SUCC "+str(self.status) + " " + str(self.id))

    # def tick(self, predecessor : "Node"):
        # if (not (predecessor in self.child)):
        #
        # 	#we check the first child (if it has one)
        # 	if(len(self.child)>0):
        # 		#print("go in first child")
        # 		self.statut = State.RUNNING
        # 		self.child[0].tick()
        #
        #
        # 	else:
        # 		#print("no child")
        # 		self.statut = State.FAILURE
        #
        #
        # else:
        # 	while(self.status == State.FAILURE):
        #
        # 		self.status = self.child[0].tick()
        #
        # return self.status

    async def tick(self):
        self.start = datetime.now()
        self.status = State.FAILURE
        while self.status == State.FAILURE:
            self.status = await self.children[0].tick()
        self.end = datetime.now()
        self.co.log(node=self)
        return self.status

    def reset(self):
        self.status = State.FAILURE
        self.children[0].reset()
