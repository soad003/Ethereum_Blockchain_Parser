from pymongo import MongoClient
import subprocess
import json
import requests

DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

contracts = collection.find()

for contract in contracts:
  code = contract["bytecode"][2:]
  #print(code)
  file = open("code_calls.bin", "w")

  file.write(code) 

  file.close()
  output = ""
  try:
    print("try ctor "  + contract["address"])
    output = subprocess.check_output('./main -ctor -json -output=calls < code_calls.bin', shell=True, stderr=subprocess.STDOUT).decode("utf-8")
  except subprocess.CalledProcessError as e:
    print("try non ctor "  + contract["address"])
    output = subprocess.check_output('./main -json -output=calls < code_calls.bin', shell=True).decode("utf-8")

  brr = json.loads(output)

  if type(brr) == list:
    #print(json.dumps(brr, indent=4))
    collection.update({"_id": contract["_id"]}, { "$set": { "calls" : output}})

  #else:
    #print("no swarm hash")