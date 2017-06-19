import json
from pymongo import MongoClient
import time
import sys
import statistics


DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_contracts = db[COLLECTION]

suicide = {"suicide": True}
notAttack ={"attack": {"$exists": False}}
cd = collection_contracts.find({"$and": [suicide, notAttack]}).sort("suicide_block",1)

# # print("creation_block;suicide_block;address")
# # last = None
# count = cd.count()
# l = []
# for c in cd:
#   if not "suicide_block" in c:
#     print("CAUTION " + c["address"])
#     exit()
#   else:
#     bn = c["suicide_block"]
#     b = c["block_number"]
#     leng = bn - b
#     l.append(leng)
#     #print('{0};{1};{2}'.format(b,bn, addr))

# print(str(statistics.mean(l)))
#print(str(statistics.median(l)))

# grr = collection_contracts.aggregate([
#   {"$group" :
#     {"_id":"$suicide_block", "count":{"$sum":1}}
#   },
#   {"$sort":{"_id":-1}}
# ])

# print("suicide_block;count")
# for c in grr:
#   print('{0};{1}'.format(c["_id"],c["count"]))


grr = collection_contracts.aggregate([
  {"$match": notAttack},
  {"$group" :
    {"_id":"$suicide_block", "count":{"$sum":1}}
  },
  {"$sort":{"_id":1}}
])

print("from;to;count")
count_all = 0
MAX = 3633433
STEP = 100000
from_block =  0
to_block = STEP
for c in grr:
  block = c["_id"]
  count = c["count"]
  if block == None:
    continue
  if block and block < to_block:
    count_all += count
  else:
    print('{0};{1};{2}'.format(from_block,to_block,count_all))
    count_all = 0
    count_all += count
    from_block+=STEP
    to_block+=STEP
  #print(block,count)

print('{0};{1};{2}'.format(from_block,to_block,count_all))