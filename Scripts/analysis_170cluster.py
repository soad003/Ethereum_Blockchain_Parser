from pymongo import MongoClient
import subprocess
import json
import requests
import datetime
from collections import defaultdict
from itertools import groupby

DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection = db[COLLECTION]

#0x8B3B3b624c3c0397D3da8Fd861512393d51DCbac   ???? creator of all leaves


#0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e attacker of the ethereum chain

# sender suicide spree 0xD3e32594CeDbC102D739142aA70D21f4caEa5618 to 0xAA7c4Ca548FfC77A42B309AAaEa40a1bd477aC70

# also involved https://etherscan.io/address/0x3898d7580aa5b8ad8a56fcd7f7af690e97112419 ??

# clean up contract https://etherscan.io/address/0xa43ebd8939d8328f5858119a3fb65f65c864c6dd#code

#https://etherscan.io/address/0xfe16bed03055e54bffad9c9b6909db3c1835fe9b#code (over 50000 times)

clu170 =["741DCE134DF2451885D54BCEF70DF1383675538D",   # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "9380C8B721BFB43FBA899A47CE88D6D386C4492C",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "EB45D97CAD3C29CDE189853A25A310E345A8CA24",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "AEBD32FEB5A69B9B91A19F450C79B943856939F8",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e            
 "C3D3FB5AF8AED718D6CBE306A0B579C12301EE6C",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e 
 "801AD447FF951291B17A76DB123F6AFAF1608911",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "EFDA6E6260A45E718654DC793822F380913663AF",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "715DBC5D6B8EB1EB726F031FE1C5B4B5A61BB771",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "80EC502C9B0F1F62CE78925D66F00780E43A4A19",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "39D27F421FE69BF46FCF42D9796E2A558897835A",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "3F3A883A2243B00BECEFB98980E2C70A4100A946",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "3012B19174FD9C08EA0AB5E913B78F644DA206CA",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "776F44C976495F0DAA384AED979581E92FEC5975",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "43BFF311049102059F3E3FAA4F4DB48EEA464A25",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "B5C048FE09BBC79E68C50591D7A39E467AB8E12B",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "D356B6016BE344EE4F6D3401F3B9B2197E22E5A3",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "7A94E370AF7331B808008857FCE730657286FA9A",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "4AB4C177256FB1A987949907DA1FB2D3E843E217",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "183B46615A7443CEA3F00629D91C0724491D1C46",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "E9C425626FB4628B6A2D14318A768DB8D58FBF1A",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "E4033F3DF2FC41B3BDA69D9C0FE6D1906D26B216",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "89359EF3D8790EA4062D08C797A5DC1F4C665E5E",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "1C526628FC9167AD424056BDA145A72C519AC611",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "729D7A79ED1E04BF4245F4D1970D4F585B7A8EBD",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "7C6671C80147B0F34D145ADB27FE052F3BED3857",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "291662610205585E435CD47F47BF3F81B44FFDAC",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "EBDD866CFA0BB8751F671B9E83CA268F0972CC75",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "752967C0C0556F4BB4B26F62DDD9B150614D79B4",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "F6B506AE8BAB8648C89A2A176145F6F6859C5EE3",           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "F003AE24102EEC0BA6D95B126D5751F5798AB285"]           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e




clu170data = []

calling = []

calling_data = []
calling_dic = defaultdict()

null_liftime = defaultdict()

bla = collection.find({"$where": "this.block_number == this.suicide_block" })

for x in bla:
  addr = x["address"]
  null_liftime[addr]=True


for x in clu170:
  addr = "0x" + x.lower()
  contract = collection.find({"address": addr})[0]
  code = contract["calls"]["code"]
  #print(contract["block_number"])
  assert len(code) == 170
  for c in code:
    addr_call = c["address"]
    calling_dic[addr_call] = True
    calling.append(addr_call)

  clu170data.append(contract)

not_in=0

sui = 0
for x in calling:
  #print(x)
  if not x in null_liftime:
    not_in+=1
  contract = collection.find({"address": x.lower()})[0]
  if "suicide_block" in contract:
    sui+=1
  calling_data.append(contract)


g =groupby(calling_data, lambda x: x["bytecode_ctor_ETH"] )

i = 0
for key, group in g:
  #print(len(list(group)))
  i+=1

print(i)

print("Called contracts from clusters " + str(len(calling)))
print("Distinct called contracts from clusters " + str(len(calling_dic)))
print("suicided " + str(sui))
print("not in null livetime " + str(not_in))


# print(all(None != item["bytecode_ctor_ETH"] for item in calling_data))
# print(all(calling_data[0]["bytecode_ctor_ETH"] == item["bytecode_ctor_ETH"] for item in calling_data))

# print(all(clu170data[0]["bytecode_ctor_ETH"] == item["bytecode_ctor_ETH"] for item in clu170data))


# print(calling_data[0]["bytecode_ctor_ETH"] == calling_data[1]["bytecode_ctor_ETH"])

# print(collection.find({"bytecode_ctor_ETH": calling_data[0]["bytecode_ctor_ETH"]}).count())

# print(collection.find({"$and": [{"bytecode_ctor_ETH": calling_data[0]["bytecode_ctor_ETH"]},{"bytecode": {"$not": {"$eq": None}}} ]}).count())

# abcd = collection.find({"$where": "this.block_number == this.suicide_block" }).count()
# print(abcd)

# bla = collection.find({"$where": "this.block_number == this.suicide_block" })
# last = None
# for c in bla:
#   current = c["bytecode_ctor_ETH"]
#   if not last:
#     last = current
#   if current != last:
#     print("not the same")
#   last = current
