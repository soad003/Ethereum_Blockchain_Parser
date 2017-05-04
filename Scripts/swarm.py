from pymongo import MongoClient
import subprocess
import json
import requests

DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

contracts = collection.find({"swarm_hash": { "$exists": False }})

i = 0
for contract in contracts:
  code = contract["bytecode"][2:]
  #print(code)
  file = open("code_swarm.bin", "w")

  file.write(code) 

  file.close()
  output = subprocess.check_output('./main -json -output=swarmHash < code_swarm.bin', shell=True).decode("utf-8")

  if output:
    #print(output)
    hash = json.loads(output)["swarmHash"]
    if hash: 
      'print(len(hash))
      collection.update({"_id": contract["_id"]}, { "$set": { "swarm_hash" : hash}})
      print(str(i) + ": found swarm " + hash)
      r = requests.get("http://swarm-gateways.net/bzz:/" + hash)
      if r.status_code == 200:
        collection.update({"_id": contract["_id"]}, { "$set": { "swarm_content" : r.text}})

  i = i + 1

  #else:
    #print("no swarm hash")