#mongodb+srv://test:qwerty1234@cluster0.expa2ml.mongodb.net/

from pymongo import MongoClient
import datetime

client = MongoClient("mongodb+srv://test:qwerty1234@cluster0.expa2ml.mongodb.net/")

db = client.books

collection = db.test_collection

doc = post = {"author":"Mike"}

post_id = collection.insert_one(post).inserted_id