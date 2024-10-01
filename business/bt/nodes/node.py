from abc import abstractmethod
from business.bt.nodes.type import State
from enum import Enum

class Node:
    def __init__(self, id) -> None:
        self.id = id
        self.status = State.FAILURE
        self.co = None
        self.start = None
        self.end = None

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    async def tick(self):
        pass

    @abstractmethod
    def toString(self):
        pass


class RootNode(Node):
    def __init__(self, id):
        super().__init__(id)
        self.status = 'Success'
        self.children = []        

    def toString(self):
        return ("Node : " + str(self.id) + " |  Type : ROOT")

    async def tick(self):
        # set all states to failure
        self.children[0].reset()

        # run tree
        await self.children[0].tick()
        self.co.save_conversation()
