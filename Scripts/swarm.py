from pymongo import MongoClient
import subprocess
import json
import requests
from collections import defaultdict

DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

notSwarmHash = {"swarm_hash": None}
swarmHash = { "swarm_hash": { "$not": { "$eq": None }} }
nonNullBytecode = {"bytecode": { "$not": { "$eq": None}}}
nullContent = { "swarm_content" : { "$exists": False }}

# contracts = collection.find({"$and" : [notSwarmHash, nonNullBytecode]})

# i = 0
# for contract in contracts:
#   code = contract["bytecode"][2:]
#   #print(code)
#   file = open("code_swarm.bin", "w")

#   file.write(code) 

#   file.close()
#   output = subprocess.check_output('./main -json -output=swarmHash < code_swarm.bin', shell=True).decode("utf-8")

#   if output:
#     #print(output)
#     hash = json.loads(output)["swarmHash"]
#     if hash: 
#       #print(len(hash))
#       collection.update({"_id": contract["_id"]}, { "$set": { "swarm_hash" : hash}})
#       print(str(i) + ": found swarm " + hash)

#   i = i + 1

notfound = defaultdict()
contracts = collection.find({"$and" : [swarmHash, nullContent]}, no_cursor_timeout=True)
#contracts = collection.find({"swarm_content": {"$not": {"$eq": None}}})

i = 0
a = contracts.count()
for contract in contracts:
  hash = contract["swarm_hash"]
  if not (hash in notfound):
    r = requests.get("http://swarm-gateways.net/bzzr:/" + hash)
    print(str(i) + "/" + str(a) + ": " + hash + " " + str(r.status_code))
    if r.status_code == 200:
      print("found")
      collection.update({"_id": contract["_id"]}, { "$set": { "swarm_content" : r.text}})
    else:
      print("nothing found")
      notfound[hash]=True
      collection.update({"_id": contract["_id"]}, { "$set": { "swarm_content" : None}})


  i = i + 1

contracts.close()
#else:
  #print("no swarm hash")