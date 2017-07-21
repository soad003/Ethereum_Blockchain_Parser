from pymongo import MongoClient
import subprocess
import json
import requests
import datetime
from collections import defaultdict

DB_NAME = "blockchain"
COLLECTION = "blocks"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

blocks = collection.find(None, {"number": 1, "timestamp": 1})

dic = defaultdict()

for b in blocks:
  block = int(b["number"], 16)
  timestamp =  int(b["timestamp"], 16)
  ts = datetime.datetime.utcfromtimestamp(timestamp)
  tss = ts.strftime('%Y-%m-%d')
  if tss in dic:
    l=dic[tss]
    l.append(block)
  else:
    dic[tss] = [block]

l=[]
for key, value in dic.items():
  l.append((key, value[0], value[-1]))


l = sorted(l, key=lambda x: x[1])


print("day;from;to")
for v in l:
  d, f, t = v
  print("{0};{1};{2}".format(d,f,t))





# for b in blocks:
#   block = int(b["number"], 16)
#   timestamp =  int(b["timestamp"], 16)
#   print("{0};{1}".format(block, datetime.datetime.utcfromtimestamp(timestamp)))