from pymongo import MongoClient
import subprocess
import json
import requests
import time
import datetime
import pytz
from bson.code import Code

def trim_trailing_zero(s):
  while s.endswith("0"):
    s = s[:-1]
  return s

DB_NAME = "blockchain"
COLLECTION_WRITE = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_contracts = db[COLLECTION_WRITE]

nonNullBytecode = {"bytecode": { "$not": { "$eq": None}}}
nullBytecode = {"bytecode": None}
nonNullInitBytecode = {"bytecode_ctor": { "$not": { "$eq": None}}}
nullInitBytecode = {"bytecode_ctor": None}


contracts = collection_contracts.find({"$and": [nonNullInitBytecode, nonNullBytecode]})

i = 0
for contract in contracts:
  bytecode = contract["bytecode"][2:]
  bytecode_ctor = contract["bytecode_ctor"]
  isSubset = bytecode in bytecode_ctor
  print(i)
  collection_contracts.update({"_id": contract["_id"]}, \
  { "$set": { "ctor_subset" : isSubset}})
  i = i + 1


contracts = collection_contracts.find({"ctor_subset": False})

i = 0
for contract in contracts:
  bytecode = trim_trailing_zero(contract["bytecode"][2:])
  bytecode_ctor = contract["bytecode_ctor"]
  isSubset = bytecode in bytecode_ctor
  print(i)
  collection_contracts.update({"_id": contract["_id"]}, \
  { "$set": { "ctor_subset_nullPadded" : isSubset}})
  i = i + 1