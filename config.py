import os


class Config:
    def __init__(self):
        self.SQLALCHEMY_DB_URI = os.getenv("SQLALCHEMY_DB_URI")
        self.SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO") == "True"
        self.TGBOTTOKEN = os.getenv("TGBOT_TOKEN")


config = Config()
