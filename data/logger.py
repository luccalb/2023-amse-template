import datetime

class ETLogger:
    def __init__(self, name):
        self.name = name
    
    def log(self, message):
        print(f"{datetime.datetime.now().strftime('%H:%M:%S')} [{self.name}] {message}")