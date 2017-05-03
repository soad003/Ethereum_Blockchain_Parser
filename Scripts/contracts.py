import sys
sys.path.append("./../Preprocessing")
sys.path.append("./../Analysis")
from ContractMap import ContractMap
from pymongo import MongoClient

DB_NAME = "blockchain"

mongo = MongoClient()

db = mongo[DB_NAME]
# # try:
# #     db.create_collection(COLLECTION)
# # except:
# #     pass
# # try:
# #     # Index the block number so duplicate records cannot be made
# #     db[COLLECTION].create_index(
# #   [("address", pymongo.DESCENDING)],
# #   unique=True
# # )
# # except:
# #     pass

# mongo_client = db[COLLECTION]

ContractMap(db, last_block=0)