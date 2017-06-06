import json
from pymongo import MongoClient
import time
import sys


DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_contracts = db[COLLECTION]

suicide = {"suicide": True}
# cd = collection_contracts.find(suicide).sort("suicide_block",1)

# print("creation_block;suicide_block;address")
# last = None
# for c in cd:
#   if not "suicide_block" in c:
#     print("CAUTION " + c["address"])
#     exit()
#   else:
#     bn = c["suicide_block"]
#     b = c["block_number"]
#     addr = c["address"]
#     print('{0};{1};{2}'.format(b,bn, addr))



grr = collection_contracts.aggregate([
  {"$group" :
    {"_id":"$suicide_block", "count":{"$sum":1}}
  },
  {"$sort":{"_id":-1}}
])

print("suicide_block;count")
for c in grr:
  print('{0};{1}'.format(c["_id"],c["count"]))