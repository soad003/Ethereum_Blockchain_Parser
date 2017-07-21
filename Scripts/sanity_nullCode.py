import json
from pymongo import MongoClient
import time
import sys


def getCtorCode(contract):
  bytecode_ctor = None
  if "bytecode_ctor" in contract and contract["bytecode_ctor"] != None and contract["bytecode_ctor"] != "0x": 
    bytecode_ctor = contract["bytecode_ctor"]
  else:
    if "bytecode_ctor_ETH" in contract and contract["bytecode_ctor_ETH"] != None and contract["bytecode_ctor_ETH"] != "0x":
      bytecode_ctor = contract["bytecode_ctor_ETH"]
    else:
      print(str(contract["address"]) + "no bytecode")
  return bytecode_ctor

def isonlyzero(x):
  return all(c == '0' for c in x)



assert isonlyzero("0000000")
assert not isonlyzero("0000000100010")
DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

Error = { "calls_error" : { "$exists": True }}
noErrorOut = { "calls_error_output" : { "$exists": False }}

contracts = collection.find(no_cursor_timeout=True)

nr = contracts.count()
i = 0
for c in contracts:
  addr = c["address"]
  code = getCtorCode(c)[2:]

  if isonlyzero(code):
    # if "calls" in c:
    #   print(c["calls"])
    print(addr)
    collection.update({"_id": c["_id"]}, { "$set": { "calls" : None}, "$unset": { "calls_error" : "", "calls_error_output":"" }})

  i+=1
