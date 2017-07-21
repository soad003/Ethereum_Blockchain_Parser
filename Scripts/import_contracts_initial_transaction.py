from pymongo import MongoClient
import subprocess
import json
import requests
import time

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

DB_NAME = "blockchain"
COLLECTION = "blocks"
COLLECTION_WRITE = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_blocks = db[COLLECTION]
collection_contracts = db[COLLECTION_WRITE]

blocks = collection_blocks.find({"transactions.to": None })

for block in blocks:
  if block["transactions"]:
    for trans in block["transactions"]:
      if trans["to"] == None:
        code_before_ctor = trans["input"]
        bla = rpcRequest("eth_getTransactionReceipt", [trans["hash"]])
        adr = bla["contractAddress"]
        print("contract creation " + adr)
        #code_after_ctor = rpcRequest( "eth_getCode",
        #                    [adr, "latest"])
        #print()
        #print(code_after_ctor[2:] in code_before_ctor)

        collection_contracts.update({"address": adr}, \
        { "$set": { "bytecode_ctor" : code_before_ctor, "block_number": block["number"]}, \
        "$setOnInsert" : { "address": adr, "bytecode" : None, "bytecode_ctor" : code_before_ctor, "block_number": block["number"] }}, \
        upsert = True)



