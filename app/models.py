from flask_login import UserMixin

class User(UserMixin):#For the flask login stuff
    def __init__(self, username):
        self.id = username
        self.username = username