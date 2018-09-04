import os


class Config:
    def __init__(self):
        self.SQLALCHEMY_DB_URI = "sqlite:////data/tgbot/tgbot.db"
        self.SQLALCHEMY_ECHO = False
        self.TGBOTTOKEN = os.getenv("TGBOT_TOKEN")


config = Config()
