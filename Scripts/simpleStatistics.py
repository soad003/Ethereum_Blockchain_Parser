from pymongo import MongoClient
import subprocess
import json
import requests
import time
import datetime
import pytz
from bson.code import Code

DB_NAME = "blockchain"
COLLECTION = "blocks"
COLLECTION_WRITE = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_blocks = db[COLLECTION]
collection_contracts = db[COLLECTION_WRITE]

print("last block")
last = db.blocks.find().sort([( "_id", -1 )]).limit(1)[0]
last_block = int(last["number"],0)
timestamp = datetime.datetime.fromtimestamp(
        int(last["timestamp"],0)
    ).replace(tzinfo=pytz.timezone('GMT')).strftime('%Y-%m-%d %H:%M:%S')
print("Nr: " + str(last_block))
print("Timestamp: " + timestamp)

nonNullBytecode = {"bytecode": { "$not": { "$eq": None}}}
nullBytecode = {"bytecode": None}
nonNullInitBytecode = {"bytecode_ctor": { "$not": { "$eq": None}}}
nullInitBytecode = {"bytecode_ctor": None}

print("Active Contracts without contracts without transactions")
active = collection_contracts.find(nonNullBytecode).count()
print(active)

print("Active Contracts that are User Created via transaction")
active_user = collection_contracts.find({"$and": [nonNullInitBytecode, nonNullBytecode]}).count()
print(active_user)

print("Contracts init transactions")
contracts_with_init_trans = collection_contracts.find(nonNullInitBytecode).count()
print(contracts_with_init_trans)

print("Active Contracts created without init trans (by other contracts)")
contracts_without_init_trans = collection_contracts.find({"$and": [nullInitBytecode, nonNullBytecode]}).count()
print(contracts_without_init_trans)

print("Either ran out of gas on creation, never got a transaction or selfdestruct")
contracts_dead = collection_contracts.find({"$and": [nonNullInitBytecode, nullBytecode]}).count()
print(contracts_dead)

print("Active Contracts with swarm hashes")
swarm_hashes = collection_contracts.find({"swarm_hash": { "$not": { "$eq": None}}}).count()
print(swarm_hashes)

ctor_subset= {"ctor_subset": False}
ctor_subset_nullPadded= {"ctor_subset_nullPadded": False}

print("bytecode is not subeset ot init bytecode")
byinctor = collection_contracts.find(ctor_subset).count()
print(byinctor)

print("bytecode is not subeset ot init bytecode modulo padding (created code on deployment?)")
byinctor_modulo_padding = collection_contracts.find({"$and": [ctor_subset_nullPadded,ctor_subset]}).count()
print(byinctor_modulo_padding)

#there should not be an entry without bytecode and constructor code... (suicide of a contract created addr?)
assert collection_contracts.find({"$and": [nullInitBytecode, nullBytecode]}).count() == 0


contracts = collection_contracts.find()
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

  
print("avg bytecode size, with swarm hash...")
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
