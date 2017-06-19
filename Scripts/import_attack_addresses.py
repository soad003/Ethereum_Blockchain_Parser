from pymongo import MongoClient
import subprocess
import json
import requests
import datetime
from collections import defaultdict
from itertools import groupby

DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

s = None
with open("./temp/attack_contracts.txt", 'r') as file_descriptor:
    s = json.load(file_descriptor)

#assert len(s) > 95000


for i in s:
  collection.update({"address": i}, \
    { "$set": { "attack" : True}})