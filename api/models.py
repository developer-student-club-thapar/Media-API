import os
from sqlalchemy import Column, Integer, String
from database import Base

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    # hashed password
    password = Column(String(250))

    def __init__(self, username, password):
        self.username = username
        self.password = password
