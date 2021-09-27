from pymongo import MongoClient

myclient = MongoClient("mongodb://localhost:27017/")
liber = myclient["liber"]
book = liber["book"]

book.delete_many({})