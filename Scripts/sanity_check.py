from pymongo import MongoClient
import subprocess
import json
import requests
import time
import datetime
import pytz
import sys
from bson.code import Code

DB_NAME = "blockchain"
COLLECTION = "blocks"
COLLECTION_WRITE = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_blocks = db[COLLECTION]
collection_contracts = db[COLLECTION_WRITE]

nonNullBytecode = {"bytecode": { "$not": { "$eq": None}}}
nullBytecode = {"bytecode": None}
nullETHBytecode = {"bytecode_ETH": None}
nonNullInitBytecode = {"bytecode_ctor": { "$not": { "$eq": None}}}
nullInitBytecode = {"bytecode_ctor": None}
nullInitETHBytecode = {"bytecode_ctor_ETH": None}
nonNullInitETHBytecode = {"bytecode_ctor_ETH": { "$not": { "$eq": None}}}
suicide = {"suicide": True}
internal = {"internal": True}
eth_new =  {"ETH_new": True}

notInvalInitBytecode = {"bytecode_ctor": "0x"}
notInvalBytecode = {"bytecode": "0x"}
notInvalInitBytecode_ETH = {"bytecode_ctor": "0x"}
notInvalBytecode_ETH = {"bytecode": "0x"}
notInternal = {"internal": False}

activeContract = nonNullBytecode

has_init = {"$or": [nonNullInitBytecode, nonNullInitETHBytecode]}

swarmhash = {"swarm_hash": { "$not": { "$eq": None}}}

ctor_subset= {"ctor_subset": False}
ctor_subset_nullPadded= {"ctor_subset_nullPadded": False}

hasCalls = {"calls": {"$not": {"$eq": None}}}
callsExists = {"calls": {"$exists": True}}
errors = {"calls_error": True}

noblockNrExists = {"block_number": {"$exists": False}}


#Sanity checks
#there should not be an entry without bytecode and constructor code... (suicide of a contract created addr?)

print("running sanity checks")
#collection_contracts.remove({ "$and" : [{"bytecode":None}, {"bytecode_ctor":None},{"bytecode_ETH":None}, {"bytecode_ctor_ETH":None} ] })
assert collection_contracts.find({"$and": [nonNullBytecode, noblockNrExists]}).count() == 0
assert collection_contracts.find({"$and": [nullInitBytecode, nullBytecode, nonNullInitETHBytecode, nullInitETHBytecode]}).count() == 0
assert collection_contracts.find({"$and": [nullInitBytecode, nullBytecode, nullInitETHBytecode, nullETHBytecode]}).count() == 0
assert collection_contracts.find({"$or": [notInvalInitBytecode, notInvalBytecode, notInvalInitBytecode_ETH, notInvalBytecode_ETH]}).count() == 0
assert collection_contracts.find({"$and": [suicide, nonNullBytecode]}).count() == 0
assert collection_contracts.find({"$and": [nullInitBytecode, nonNullBytecode, notInternal]}).count() == 0
# assert collection_contracts.find({"$and": [nonNullBytecode, nullInitBytecode, ]}).count() == 0
contracts = collection_contracts.find()
for contract in contracts:
  bytecode = contract["bytecode"]
  bytecode_ctor = contract["bytecode_ctor"]
  if "bytecode_ETH" in contract:
    bytecode_ETH = contract["bytecode_ETH"]
  else: 
      bytecode_ETH = None
  if "bytecode_ctor_ETH" in contract:
    bytecode_ctor_ETH = contract["bytecode_ctor_ETH"]  
  else:
      bytecode_ctor_ETH = None
  if bytecode and bytecode_ETH:
    if bytecode != bytecode_ETH:
      print(contract["address"])
  if bytecode_ctor and bytecode_ctor_ETH:
     if bytecode_ctor != bytecode_ctor_ETH:
       print(contract["address"])



