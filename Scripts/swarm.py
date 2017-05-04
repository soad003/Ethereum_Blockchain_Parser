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
  file = open("code_swarm.bin", "w")

  file.write(code) 

  file.close()
  output = subprocess.check_output('./main -json output=swarmHash < code.bin', shell=True).decode("utf-8")

  if output:
    hash = json.loads(output).decode('utf-8')["swarmHash"]
    print("found swarm " + hash)
    r = requests.get("http://swarm-gateways.net/bzz:/" + hash)
    if r.status_code == 200:
      collection.update({"_id": contract["_id"]}, { "swarm": { "calls" : r.text}})

  #else:
    #print("no swarm hash")