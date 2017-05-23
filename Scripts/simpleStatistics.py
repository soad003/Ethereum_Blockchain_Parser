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

if len(sys.argv) > 1:
  arg1 = str(sys.argv[1])
else:
  arg1 = None

if arg1 != "sanity":
  print("last block")
  last = db.blocks.find().sort([( "_id", -1 )]).limit(1)[0]
  last_block = int(last["number"],0)
  timestamp = datetime.datetime.fromtimestamp(
          int(last["timestamp"],0)
      ).replace(tzinfo=pytz.timezone('GMT')).strftime('%Y-%m-%d %H:%M:%S')
  print("Nr: " + str(last_block))
  print("Timestamp: " + timestamp)

  print("Active Contracts without contracts without transactions")
  active = collection_contracts.find(activeContract).count()
  print(active)

  print("Active Contracts that are User Created via transaction")
  active_user = collection_contracts.find({"$and": [nonNullInitBytecode, activeContract]}).count() # or eth
  print(active_user)

  print("Contracts init transactions")
  contracts_with_init_trans = collection_contracts.find(nonNullInitBytecode).count() # or eth
  print(contracts_with_init_trans)

  print("Active Contracts created without init trans (by other contracts)")
  contracts_without_init_trans = collection_contracts.find({"$and": [nullInitBytecode, nonNullBytecode]}).count()
  print(contracts_without_init_trans)

  print("Either ran out of gas on creation, never got a transaction or selfdestruct")
  contracts_dead = collection_contracts.find({"$and": [nonNullInitBytecode, nullBytecode]}).count()
  print(contracts_dead)

  print("internal contract creations that failed")
  internal_dead = collection_contracts.find({"$and": [nullInitBytecode, nullBytecode, nonNullInitETHBytecode, notInternal]}).count() == 0 #not internal ???

  print("Active Contracts with swarm hashes")
  swarmhash = {"swarm_hash": { "$not": { "$eq": None}}}
  swarm_hashes = collection_contracts.find({"$and": [activeContract, swarmhash]}).count()
  print(swarm_hashes)

  ctor_subset= {"ctor_subset": False}
  ctor_subset_nullPadded= {"ctor_subset_nullPadded": False}

  print("bytecode is not subeset ot init bytecode")
  byinctor = collection_contracts.find(ctor_subset).count()
  print(byinctor)

  print("bytecode is not subeset ot init bytecode modulo padding (created code on deployment?)")
  byinctor_modulo_padding = collection_contracts.find({"$and": [ctor_subset_nullPadded,ctor_subset]}).count()
  print(byinctor_modulo_padding)


  contracts = collection_contracts.find(activeContract)
  bytecodesize = 0
  bytecodeinitsize = 0
  bytecodediff = 0
  for contract in contracts:
    bytecode = contract["bytecode"]
    bytecode_ctor = contract["bytecode_ctor"] 
    if bytecode:
      bytecodesize = bytecodesize + len(bytecode[2:])
    if bytecode_ctor:
      bytecodeinitsize = bytecodeinitsize +  len(bytecode_ctor[2:])
    if bytecode and bytecode_ctor:
      bytecodediff = bytecodediff + ( len(bytecode_ctor[2:]) - len(bytecode[2:]))


    
  print("avg bytecode size, with swarm hash... (active)")
  print(bytecodesize / active)

  print("avg init transaction size with swarm and params")
  print(bytecodeinitsize / contracts_with_init_trans)


  print("avg diff between init and actual code")
  print(bytecodediff / active_user)


  print("contracts with swarm hashes")
  swarm_content = collection_contracts.find({"swarm_content": {"$not": {"$eq": None}}})
  swarm_hashes = collection_contracts.find({"swarm_hash": {"$not": {"$eq": None}}})
  print("hashes: " + str(swarm_hashes.count()))
  print("content: " + str(swarm_content.count()))


  print("########################## ETH SCRIPT ADDITIONS")
  print("new by this script " + str(collection_contracts.find(eth_new).count()))
  print("internal " + str(collection_contracts.find(internal).count()))
  print("suicide " + str(collection_contracts.find(suicide).count()))



  # print(collection_contracts.aggregate([
  #    {
  #         "$project": {
  #             "code_size": { "$strLenBytes": "$bytecode" }
  #          }
  #     },
  #     {
  #           "$group": {
  #               "_id": None,
  #               "count": {
  #                   "$sum": "$code_size"
  #               }
  #           }
  #     }
  # ]))
  # map_str = Code("function map() { emit(this.bytecode.length, 1);}")
  # reduce_str = Code("function reduce(key, values) { return Array.sum(values) * key;}")
  # res = collection_contracts.map_reduce(map_str, reduce_str, "avgCodeSize")
  # for doc in res.find():
  #   print(doc)





#Sanity checks
#there should not be an entry without bytecode and constructor code... (suicide of a contract created addr?)

collection_contracts.remove({ "$and" : [{"bytecode":None}, {"bytecode_ctor":None},{"bytecode_ETH":None}, {"bytecode_ctor_ETH":None} ] })
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



