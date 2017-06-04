from pymongo import MongoClient
import subprocess
import json
import requests

DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

nonNullBytecode = {"bytecode": { "$not": { "$eq": None}}} #verified that all
noCalls = { "calls" : { "$exists": False }}
noError = { "calls_error" : { "$exists": False }}

contracts = collection.find({ "$and": [nonNullBytecode, noCalls, noError]})

def getCtorCode(contract):
  bytecode_ctor = None
  if "bytecode_ctor" in contract and contract["bytecode_ctor"] != None:
    bytecode_ctor = contract["bytecode_ctor"]
  else:
    if "bytecode_ctor_ETH" in contract:
      bytecode_ctor = contract["bytecode_ctor_ETH"]
  return bytecode_ctor


nr = contracts.count()

i = 1
for contract in contracts:
  code = contract["bytecode"][2:]
  init = getCtorCode(contract)[2:]
  #print(code)
  file = open("code_calls.bin", "w")

  file.write(init) 

  file.close()
  output = ""
  try:
    print(str(i) + "/" + str(nr) + ": try ctor "  + contract["address"])
    i = i + 1
    output = subprocess.check_output('timeout 5 ./main -ctor -json -output=calls < code_calls.bin', shell=True, timeout=5).decode("utf-8")
  except subprocess.CalledProcessError as e:
    print("error")
    collection.update({"_id": contract["_id"]}, { "$set": { "calls_error" : True}})
    continue
  except subprocess.TimeoutExpired:
    print("timeout")
    collection.update({"_id": contract["_id"]}, { "$set": { "calls_error" : True}})
    continue
    # file = open("code_calls.bin", "w")

    # file.write(code) 

    # file.close()
    # print("AAAAAAAAAHHHH ?? try non ctor "  + contract["address"])
    # output = subprocess.check_output('./main -json -output=calls < code_calls.bin', shell=True).decode("utf-8")

  brr = json.loads(output)
  if len(brr["code"]) > 0 or len(brr["ctor"]) > 0:
    collection.update({"_id": contract["_id"]}, { "$set": { "calls" : brr}})
  else:
    collection.update({"_id": contract["_id"]}, { "$set": { "calls" : None}})

  # if type(brr) == list:
  #   print(json.dumps(brr, indent=4))
  #   if len(brr) == 0: 
  #     collection.update({"_id": contract["_id"]}, { "$set": { "calls" : None}})
  #   else:
      


  #else:
    #print("no swarm hash")