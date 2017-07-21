import json
from pymongo import MongoClient
from ethjsonrpc import ParityEthJsonRpc




c = ParityEthJsonRpc('127.0.0.1', 8545)
print(c.net_version())
print(c.web3_clientVersion())

#print c.trace_get("0x7e9b346798bb9b91f9fd0fb2a91882ee253affa6873bc8be23c80d1e31ca5aa6", "0x0")
#block = c.trace_block(1720547)

DB_NAME = "blockchain"
COLLECTION = "contracts"

mongo = MongoClient()

db = mongo[DB_NAME]
collection_contracts = db[COLLECTION]

def StoreTransaction(adr, init, code, blocknr, internal):
    collection_contracts.update({"address": adr}, \
        { "$set": { "bytecode_ctor_ETH" : init, "bytecode_ETH": code, "block_number": blocknr, "internal": internal}, \
        "$setOnInsert" : { "address": adr, "bytecode" : None, "bytecode_ctor" : None, "ETH_new": True}}, \
        upsert = True)

def FlagSuicide(adr):
    bla = collection_contracts.update({"address": adr}, \
        { "$set": { "suicide" : True}})
    if(bla["nModified"] != 1):
        print("could not flag suicide on " + str(adr))


contracts = []
allContractCreations = 0
for i in range(0,3633433):
    
    debug = False
    if i%10000 == 0:
        print("Parsing Block %i"%(i))
    #     with open('contracts.txt', 'a') as outfile:
    #         json.dump(contracts, outfile)
    #         outfile.write(",")
    #         contracts = []
    #     print("Written to file")
    #block = c.trace_block(1720551)
    block = c.trace_block(i)
    s = set()
    internalTx = 0
    totalTx = 0
    errorCount = 0

    dTx = dict() # tx hash -> (from, to, contractAddress)
    # There could be several internal transactions, we therefore need a counter for those
    dInternalTx = dict() # (tx hash, number) -> (from, to, contractAddress)

    contractCreationTransactions = []
    suicideTransactions = 0

    for tx in block:
        h = tx['transactionHash']
        if tx.has_key('error'):
            if debug: print("Transaction %s resulted in error: %s" %(h ,tx['error']))
            errorCount += 1
            continue

        totalTx += 1
        if h in s: # Already existed, potential candidate for internal transaction
            internalTx += 1
            if tx['action'].has_key('to'): # Regular transaction
                dInternalTx[(h,internalTx)] = (tx['action']['from'], tx['action']['to'])
            else:
                if debug: print("Contract creation/suicide from internal transaction")
                if tx['type'] == 'suicide':
                    dInternalTx[(h,internalTx)] = (0, 0, 0)
                    suicideTransactions += 1

                    print(json.dumps(tx, indent=4))

                    FlagSuicide(tx['action']['address'])
                    if debug: print("Internal transaction %s has type %s and result address %s"% (h,tx['type'], tx['result']))
                else:
                    # checking resulting contract address
                    contractAddress = tx['result']['address']
                    dInternalTx[(h,internalTx)] = (tx['action']['from'], 0, contractAddress)
                    if debug: print("Internal transaction %s has type %s and result address %s"% (h,tx['type'], tx['result']['address']))
                    contractCreationTransactions.append(h)

                    init = tx['action']['init']
                    code = tx['result']['code']
                    #contracts.append({'contractAddress': contractAddress, 'init': init, 'code': code})
                    StoreTransaction(contractAddress, init, code, i, True)
        else: # Likely regular transaction
            if tx['action'].has_key('to'):
                dTx[h] = (tx['action']['from'], tx['action']['to'])
            else: # Contract creation transaction
                if tx.has_key('result'):
                    contractAddress = tx['result']['address']
                    dTx[h] = (tx['action']['from'], 0, contractAddress)
                    contractCreationTransactions.append(h)
                    
                    init = tx['action']['init']
                    code = tx['result']['code']
                    #contracts.append({'contractAddress': contractAddress, 'init': init, 'code': code})
                    StoreTransaction(contractAddress, init, code, i, False)
                else:
                    if debug: print("Contract creation transaction %s resulted in no result??" %(h))
                    exit(0)
                
            s.add(h)
                

    if debug: print("")
    if debug: print("Regular Transactions")
    for h in dTx:
        if dTx[h][1] == 0:
            if debug: print("%s : %s -> %s --contract-> %s "%(h, dTx[h][0], dTx[h][1], dTx[h][2]))
        else:
            if debug: print("%s : %s -> %s "%(h, dTx[h][0], dTx[h][1]))
    if debug: print("")
    if debug: print("Internal Transactions")
    for h_i in dInternalTx:
        if len(dInternalTx[h_i]) == 3:
            if debug: print("%s, idx %i : %s -> %s --contract-> %s"%(h_i[0], h_i[1], dInternalTx[h_i][0], dInternalTx[h_i][1], dInternalTx[h_i][2]))
        else:
            if debug: print("%s, idx %i : %s -> %s"%(h_i[0], h_i[1], dInternalTx[h_i][0], dInternalTx[h_i][1]))

    if debug: print("")
    if debug: print("Internal Transactions: %i" %(internalTx))
    if debug: print("Total Transactions: %i" %(totalTx-internalTx))
    if debug: print("Contract Creation Transactions: %i" % (len(contractCreationTransactions)))
    if debug: print("-----------------------------------------------------------------")
    allContractCreations += len(contractCreationTransactions)

print("Contract Creation transactions: %i"%(allContractCreations))


