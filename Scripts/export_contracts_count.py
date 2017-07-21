import json
from pymongo import MongoClient
import time
import sys

def printRange(f,t):  
  block_gt = {"block_number": {"$gt": f }}
  block_lt = {"block_number": {"$lt": t }}
  suicide_block_gt = {"suicide_block": {"$gt": t }}
  suicide_not_exists = {"suicide_block": {"$exists": False}}
  suicide_or_not_exists = {"$or": [suicide_block_gt, suicide_not_exists]}
  notAttack ={"attack": {"$exists": False}}
  cd = collection_contracts.find({"$and": [block_gt, block_lt, suicide_or_not_exists, notAttack]}).count()
  print('{0};{1};{2}'.format(f,t, cd))


DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_contracts = db[COLLECTION]



print("from_block;to_block;count")
last = None
MAX = 3633433
STEP = 100000
i=0
while i <= MAX:
  n_i = i + STEP
  printRange(i, min(n_i, MAX))
  i = n_i

#printRange(i, MAX)

# cd = collection_contracts.find({"$and": [block_gt, block_lt, suicide_block_gt]}).count()
# print('{0};{1};{2}'.format(i,n_i, cd))

#   if not "suicide_block" in c:
#     print("CAUTION " + c["address"])
#     exit()
#   else:
#     bn = c["suicide_block"]
#     b = c["block_number"]
#     addr = c["address"]
#     print('{0};{1};{2}'.format(b,bn, addr))
