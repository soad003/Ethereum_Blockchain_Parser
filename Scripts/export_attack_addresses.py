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


clu170 =["0x741DCE134DF2451885D54BCEF70DF1383675538D".lower(),   # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x9380C8B721BFB43FBA899A47CE88D6D386C4492C".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xEB45D97CAD3C29CDE189853A25A310E345A8CA24".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xAEBD32FEB5A69B9B91A19F450C79B943856939F8".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e            
 "0xC3D3FB5AF8AED718D6CBE306A0B579C12301EE6C".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e 
 "0x801AD447FF951291B17A76DB123F6AFAF1608911".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xEFDA6E6260A45E718654DC793822F380913663AF".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x715DBC5D6B8EB1EB726F031FE1C5B4B5A61BB771".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x80EC502C9B0F1F62CE78925D66F00780E43A4A19".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x39D27F421FE69BF46FCF42D9796E2A558897835A".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x3F3A883A2243B00BECEFB98980E2C70A4100A946".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x3012B19174FD9C08EA0AB5E913B78F644DA206CA".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x776F44C976495F0DAA384AED979581E92FEC5975".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x43BFF311049102059F3E3FAA4F4DB48EEA464A25".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xB5C048FE09BBC79E68C50591D7A39E467AB8E12B".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xD356B6016BE344EE4F6D3401F3B9B2197E22E5A3".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x7A94E370AF7331B808008857FCE730657286FA9A".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x4AB4C177256FB1A987949907DA1FB2D3E843E217".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x183B46615A7443CEA3F00629D91C0724491D1C46".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xE9C425626FB4628B6A2D14318A768DB8D58FBF1A".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xE4033F3DF2FC41B3BDA69D9C0FE6D1906D26B216".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x89359EF3D8790EA4062D08C797A5DC1F4C665E5E".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x1C526628FC9167AD424056BDA145A72C519AC611".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x729D7A79ED1E04BF4245F4D1970D4F585B7A8EBD".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x7C6671C80147B0F34D145ADB27FE052F3BED3857".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x291662610205585E435CD47F47BF3F81B44FFDAC".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xEBDD866CFA0BB8751F671B9E83CA268F0972CC75".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0x752967C0C0556F4BB4B26F62DDD9B150614D79B4".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xF6B506AE8BAB8648C89A2A176145F6F6859C5EE3".lower(),           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e
 "0xF003AE24102EEC0BA6D95B126D5751F5798AB285".lower()]           # only creation, no transaction, no comments, no ether, creator 0x1fa0e1dfa88b371fcedf6225b3d8ad4e3bacef0e

clu170_2 =  ["0x0DD8FD64FDF64DABCFEEF92807F6D5DED9AF6EEF".lower(), 
 "0x839041839824CC9F7B696CBACA63E1A4DA80E989".lower(), 
 "0x66A3740176EB58DA4F27D1EDB533F292CC737F89".lower(), 
 "0x3DD1C32566A8AE3E393D6CDC95A58842B0B3A187".lower(), 
 "0xC58A57621E7C4F734C05A59928B6A991B73045EB".lower(), 
 "0xFCAB9D259839E93296D0835138AF51D6F9785BBB".lower(), 
 "0xBD49BB10DD86E8EBBF2D80134823269D4EB814E8".lower(), 
 "0xC52F74C25F279856706E3F7DF252E1F03D2FC060".lower(), 
 "0x08572D0C2E67B54E6A4EEA22DB9BC4E9D4CFD824".lower(), 
 "0x423FF818D1E8147213FDAE99793610CDAEA3504D".lower(), 
 "0x01E75581E95BF883BE700688D408AC463636E0CE".lower(), 
 "0x1CD89E0739750A246AAAB8EF0E67E7DBF274AD30".lower(), 
 "0x64D584676F6D4D21DA74FE276529262F1CCA682D".lower(), 
 "0x0E49A4DBCB48CEC7CB152F92459BF97A3FBA9C2F".lower(), 
 "0x7F0607BCC934124DDF5796C7C3812810DC055F72".lower()]

# bla = list(map(lambda x: x.lower(),set(clu170+clu170_2)))
# print(len(bla))
# for a in bla:
#   c = collection.find({"address": a})[0]
#   #print(c)
#   assert len(c["calls"]["code"]) == 170
#   assert not "suicide_block" in c
#   assert not "calls_error" in c
#   assert c["bytecode_ctor"] != None
#   assert c["bytecode_ctor_ETH"] != None
#   assert c["bytecode"] != None
#   assert c["bytecode_ETH"] != None
#   for b in c["calls"]["code"]:
#     assert b["address"] != None
bla = collection.find()
death_star = 0
for a in bla:
  if "calls" in a and a["calls"]:
    c = a["calls"]
    if "code" in c:
      if len(c["code"]) == 170:
        if all(b["address"] != None and b["callType"] == "DELEGATECALL" for b in c["code"]):
          death_star += 1



print(death_star)






# sui = ["0xAA7c4Ca548FfC77A42B309AAaEa40a1bd477aC70".lower()]

# # check if 0xAA7c4Ca548FfC77A42B309AAaEa40a1bd477aC70 in ...


# martin =  ["0xd8509212d1464d483680d4c0f4d832a75a2ddedb",
#   "0x185a0aac0839ca3b34eb3af93d8cab62bcb5b431",
#   "0x8428ce12a1b6aaecfcf2ac5b22d21f3831949da3",
#   "0xd6a64d7e8c8a94fa5068ca33229d88436a743b14",
#   "0xa303c48a96a85caef9b588387e7f39f82edddcb6",
#   "0x3cd00e309e14b3008ad46775703376b8b89006fe",
#   "0x6a0a0fc761c612c340a0e98d33b37a75e5268472",
#   "0xb8fba0b596870010b306df0eb599ae9517d94f82",
#   "0x1e621321e99f3d632ad9e84d956c10a348d42559",
#   "0x2213d4738bfec14a2f98df5e428f48ebbde33e12",
#   "0x7a3090bf686465a47bfff5ca2b084fdded5c6732",
#   "0xd8ce0fbcabb206a743917aadf2c409c8eb3c45cf",
#   "0xb6389d6575966f946e190b9d538c3259857ed2c7",
#   "0xe0ca2ec1648f4fc94d5ecaad5caa9fa6799ebb28",
#   "0xe8fe02317abec8a084bfa8202e4bc958b791ef06",
#   "0x7c1cf1f9809c527e5a6becaab56bc34fbe6f2023",
#   "0xd502d0a7df49658734aaec3ab1529861ff6dad3a",
#   "0xbd37ee00e47c0fe0def80bd95c498698b4a15235",
#   "0x2f2f0afcfc5383d3585b148e22e5ad31c528f398",
#   "0x15841ce7660aac949dff19e46889b20ca615414a",
#   "0x8332d2bbb053fbb68af6c5a472c40dd8492177cf",
#   "0xdcfce7ddba377d23d34c761b18a899c25725396c",
#   "0xdb8955af669618642176befc1dc98e4e39bc43a0",
#   "0xdaae6514b4381de27c794bb6d55e28916ea03869",
#   "0xe30c68bf57296c7418eda6f81b05b4dc2a32bcaa",
#   "0xdf4ce5547129c5517f53a751ee397c5edb0f808b",
#   "0x8a2e29e7d66569952ecffae4ba8acb49c1035b6f",
#   "0x874ea4d0b8080984b0974062428c9c929af03c6b",
#   "0x52d77b07e65697551d4b1ade631546b89be6260f",
#   "0x7c20218efc2e07c8fe2532ff860d4a5d8287cb31",
#   "0x9b0bf122afb53c256eb4c3b01e18defe4d0f0b8c",
#   "0xe25e422e3f9e9374a3d8a75451c790d48fb33218",
#   "0x9f58ef5d703973ba98dfa7a9bdecabecf13a0ec3",
#   "0xb09f8a62c6681b0c739dfde7221bfe8f2da3f128"]

# def findChildren(addr):
#   res = []
#   contract_query = collection.find({"address": addr})
#   if contract_query.count() > 0:
#     contract = contract_query[0]
#     if "calls" in contract and contract["calls"] != None :
#       if "code" in contract["calls"]:
#         code = contract["calls"]["code"]
#         for c in code:
#           addr_call = c["address"]
#           if addr_call != None:
#             addr_call = addr_call.lower()
#             res.append(addr_call)
#             res += findChildren(addr_call)
#       #else:

#         #print("no code " + str(addr))
#   #else:
#     #print("not found " + str(addr))
#   return res


# null_liftime = defaultdict()

# bla = collection.find({"$where": "this.block_number == this.suicide_block" })

# for x in bla:
#   addr = x["address"]
#   if x["block_number"] < 2463000 and x["block_number"] > 1434393:
#     null_liftime[addr]=True


# all_start = set(clu170)
# #all_start = set()
# all_start.update(clu170_2)
# all_start.update(sui)
# all_start.update(martin)
# all_start.update(null_liftime.keys())

# all=[]

# #print(len(all_start))

# for a in all_start:
#   all.append(a)
#   all += findChildren(a)


# #print(len(set(all)))

# for i in set(all):
#   print("\"" + str(i) + "\",")
