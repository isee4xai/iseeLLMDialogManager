import datetime


class Logger:
    def __init__(self):
        self.file = open("log.txt", "a")
        self.file.write("\r\r" + str(datetime.datetime.now()) + "\r")

    def log(self, message):
        self.file.write(str(datetime.datetime.now()) + " : " + message + "\r")
        pass
