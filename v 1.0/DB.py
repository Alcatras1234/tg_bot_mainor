from pymongo import MongoClient

cluster = MongoClient("mongodb://localhost:27017")

db = cluster["db_tg_bot"]
collection = db["tg_bot"]

name = "KABYBA"

collection.delete_many({})