import itertools

DB_NAME = "blockchain"
COLLECTION = "contracts"

def getContractsCollectionMongoDB():
  from pymongo import MongoClient
  mongo = MongoClient()
  db = mongo[DB_NAME]
  return db[COLLECTION]

def take(n, iterable):
  "Return first n items of the iterable as a list"
  return list(itertools.islice(iterable, n))

def sanatizeAddr(a):
  if a == None:
    return None
  if a.startswith("0x"):
    a = a[2:]
  return a.upper()

def incOrAdd (dic, key):
  if key in dic:
    dic[key] = dic[key] + 1
  else:
    dic[key] = 1