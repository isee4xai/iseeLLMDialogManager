import abc


class UIInterface(abc.ABC):

    @abc.abstractclassmethod
    def send(message):
        pass

    @abc.abstractclassmethod
    def send_and_receive(message):
        pass

    @abc.abstractclassmethod
    def receive():
        pass


class UIConsole(UIInterface):

    def send(self, message):
        print(message)

    def send_and_receive(self, message):
        print(message)
        return input("You: ")

    def receive(self):
        return input("You: ")


class WebSocket(UIInterface):

    def __init__(self, web_socket) -> None:
        self.web_socket = web_socket

    async def send(self, message):
        await self.web_socket.send_text(message)

    async def send_and_receive(self, message):
        await self.web_socket.send_text(message)
        return await self.web_socket.receive_text()

    async def receive(self):
        return await self.web_socket.receive_text()
