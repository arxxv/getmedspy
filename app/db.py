import pymongo
from pymongo import MongoClient
import os


def create_db():
    try:
        CONNECTION_STRING = os.environ['CONNECTION_STRING']
        client = MongoClient(CONNECTION_STRING)
        db=client.test
        return client['getmeds']

    except Exception as e:
        print(e)

