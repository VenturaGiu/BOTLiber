from pymongo import MongoClient
from pymongo.message import _EMPTY

myclient = MongoClient("mongodb://localhost:27017/")
liber = myclient["liber"]
book = liber["book"]
stock = liber["stock"]