from collections import defaultdict
import requests
import json
import pickle
import os
import time
from pymongo import MongoClient

DB_NAME = "blockchain"
COLLECTION_WRITE = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_contracts = db[COLLECTION_WRITE]

def rpcRequest(method, params):
  url = "{}:{}".format("http://localhost", "8545")
  headers = {"content-type": "application/json"}
  delay = 0.0001
  """Make an RPC request to geth on port 8545."""
  payload = {
      "method": method,
      "params": params,
      "jsonrpc": "2.0",
      "id": 0
  }
  time.sleep(delay)
  res = requests.post(
        url,
        data=json.dumps(payload),
        headers=headers).json()
  return res["result"]

nullBytecode = {"bytecode": None}

contracts = collection_contracts.find({"$and": [nullBytecode]})

counter = 0
for contract in contracts:
    code = rpcRequest("eth_getCode",
                        [contract["address"], "latest"])
    if code != "0x":
        collection_contracts.update({"_id": contract["_id"]}, \
        { "$set": { "bytecode" : code}})
    counter = counter + 1
    if counter % 10000 == 0:
        print("Done with " + str(counter))




notInvalInitBytecode = {"bytecode_ctor": "0x"}
notInvalBytecode = {"bytecode": "0x"}
notInvalInitBytecode_ETH = {"bytecode_ctor_ETH": "0x"}
notInvalBytecode_ETH = {"bytecode_ETH": "0x"}
contracts = collection_contracts.find({"$or": [notInvalInitBytecode, notInvalBytecode, notInvalInitBytecode_ETH, notInvalBytecode_ETH]})

counter = 0
for contract in contracts:
    if contract["bytecode"] == "0x":
        collection_contracts.update({"_id": contract["_id"]}, \
            { "$set": { "bytecode" : None}})
    if contract["bytecode_ctor_ETH"] == "0x":
        collection_contracts.update({"_id": contract["_id"]}, \
            { "$set": { "bytecode_ctor_ETH" : None}})
    if contract["bytecode_ETH"] == "0x":
        collection_contracts.update({"_id": contract["_id"]}, \
            { "$set": { "bytecode_ETH" : None}})
    if contract["bytecode_ctor"] == "0x":
        collection_contracts.update({"_id": contract["_id"]}, \
            { "$set": { "bytecode_ctor" : None}})
    counter = counter + 1
    if counter % 10000 == 0:
        print("Done with " + str(counter))