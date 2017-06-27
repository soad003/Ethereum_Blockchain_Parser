
import subprocess
import json
import requests
import networkx as nx
from collections import defaultdict
import os.path
from functools import reduce
import itertools
from collections import namedtuple

#import matplotlib.pyplot as plt

from analysis_util import getContractsCollectionMongoDB, take, sanatizeAddr, incOrAdd

#globals
STATE_FILE = "./temp/contracts_state.json"
GRAPH_FILE = "./temp/contracts.graphml"
UNKNOWNNAME = "UNKNOWN"
HARDCODED_ADDRESSES = ["0x1", "0x2", "0x3", "0x4"]

#Analysis State
DG=nx.DiGraph()

class State(object):
  def __init__(self): 
    self.calls_to_wrong_addr = defaultdict()
    self.calls_to_dead_addr = defaultdict()
    self.analysis_errors = defaultdict()
    self.calls_in_ctor = defaultdict()
    self.active_contracts = defaultdict()
    self.disabled_contracts = defaultdict()
    self.nodes_with_loops = defaultdict()
    self.has_calls_and_error = defaultdict()
    self.attack = defaultdict()

state = State()

# Methods 

def isTruestless(node_name, visited):
  if node_name in visited:
    state.nodes_with_loops[node_name] = visited 
    print(node_name + " has a dep loop")
    return False
  visited[node_name] = True
  if node_name == None: 
    return False
  node = DG.node[node_name]
  if "trustless" in node:
    return node["trustless"]
  else:
    return reduce(lambda acc, x: acc and x ,map(lambda x: isTruestless(x, visited), DG.successors(node_name)), True)

def init_state():
  # Add hardcoded lib contract addresses to active contracts
  for addr in HARDCODED_ADDRESSES:
    state.active_contracts[sanatizeAddr(addr)]=True

def handle_analysis_error(contract, block, addr):
  # special case should not happen
  if "calls" in contract:
    print(contract["calls"])
    state.has_calls_and_error[addr] = True
  state.analysis_errors[addr] = True
  inAttack = False
  if "attack" in contract:
    inAttack = contract["attack"]
  DG.add_node(addr, trustless = False, attack = inAttack,block_nr = block, trivially_not = True)

def handle_has_calls(calls, block, addr, inAttack):
  #print(calls)
  ctor = calls["ctor"]
  code = calls["code"]

  # if has call in ctor not really a violation as long as payload has fixed addresses
  if ctor:
    #soft violation of code is law?
    state.calls_in_ctor[addr] = True
    print(str(addr) + " has calls in ctor: Soft violation of code is law?")

  # considred trivially not safe if one call not static
  triviallyNotSafe = any(sanatizeAddr(call["address"]) == None for call in code)
  if triviallyNotSafe:
    DG.add_node(addr, trustless = False, attack = inAttack, block_nr = block, trivially_not = True)
  else:
    #safe until one of the successors is not safe
    DG.add_node(addr, block_nr = block, attack = inAttack)

  # ADD EDGES
  for call in code:
    call_addr = sanatizeAddr(call["address"])
    
    if call_addr == None:
      DG.add_edge(addr, UNKNOWNNAME)
    else:
      if call_addr in state.attack:
        print(call_addr + " is in attack")

      # only include calls to active contracts
      if call_addr in state.active_contracts:
        DG.add_edge(addr, call_addr)
      else:
        # not an active contract therefore a call to it is safe, because no code is executed just returns
        print(str(call_addr) + " not active")

        if not call_addr in state.disabled_contracts:
          # not active anymore but was a contract at one time (suicide)
          incOrAdd(state.calls_to_wrong_addr, call_addr)
        else:
          # not active... calls crap address?
          incOrAdd(state.calls_to_dead_addr, call_addr)
      
def create_graph():
  # MONGO
  collection = getContractsCollectionMongoDB()
  # MONGO FILTERS
  nonNullBytecode = {"bytecode": { "$not": { "$eq": None}}}
  nullBytecode = {"bytecode": None}
  #notAttack ={"attack": {"$exists": False}}
  notAttack = {}

  # INIT Active Contracts
  contracts = collection.find({ "$and": [nonNullBytecode, notAttack]})
  for c in contracts:
    state.active_contracts[sanatizeAddr(c["address"])] = True

  # INIT Disabled Contracts
  contracts = collection.find({ "$and": [nullBytecode, notAttack]})
  for c in contracts:
    state.disabled_contracts[sanatizeAddr(c["address"])] = True

  # INIT attack Contracts
  contracts = collection.find({"attack": {"$exists": True}})
  for c in contracts:
    state.attack[sanatizeAddr(c["address"])] = True

  # INIT FIXED GRAPH NODES With trustless properties
  DG.add_node(UNKNOWNNAME, attack = False, trustless = False)
  # hardcoded are assumed safe
  for adr in HARDCODED_ADDRESSES:
    DG.add_node(sanatizeAddr(adr), attack = False, trustless = True)

  # LOAD ALL ACTIVE CONTRACTS
  contracts = collection.find({ "$and": [nonNullBytecode, notAttack]}) # .limit(10000)
  nr = contracts.count()
  i = 0

  # ITER CONTRACTS AND GENERATE GRAPH
  for contract in contracts:
    i += 1
    adr = sanatizeAddr(contract["address"])
    block = int(contract["block_number"])
    inAttack = False
    if "attack" in contract:
      inAttack = contract["attack"]

    # sort out contracts with analysis errors assume we do not trust them
    if "calls_error" in contract:
      print(str(i) + "/" + str(nr) + " : " + str(adr) + ": Assume not trustless because analysis error")
      handle_analysis_error(contract, block, adr)
      continue

    calls = contract["calls"]

    if calls:
      print(str(i) + "/" + str(nr) + " : " + str(adr) + ": not Trivially trustless")
      handle_has_calls(calls, block, adr, inAttack)
    else:
      #Case Trivially trustless because no interaction.
      print(str(i) + "/" + str(nr) + " : " + str(adr) + ": Trivially trustless")
      DG.add_node(adr, trustless = True, attack = inAttack, block_nr = block, trivially = True)

def safe_state():
  with open(STATE_FILE, 'w') as file_descriptor:
    json.dump(state.__dict__, file_descriptor) 
  nx.write_graphml(DG, GRAPH_FILE)

def recover_state():
  global state, DG
  with open(STATE_FILE, 'r') as file_descriptor:
    s = json.load(file_descriptor)
    state = namedtuple("State", s.keys())(*s.values())
  DG = nx.read_graphml(GRAPH_FILE)

def compute_trustlessness():
  i = 1
  nr = len(DG.nodes())
  for node_name in DG.nodes():
    print(str(i) + "/" + str(nr) + " : " + str(node_name) + "")
    DG.node[node_name]["trustless"] = isTruestless(node_name, defaultdict())
    i+=1

def analyse_graph():
  print("trivially trustless " + str(len(list(filter(lambda x: "trivially" in DG.node[x] and DG.node[x]["trivially"], DG.nodes())))))
  print("trivially not trustless " + str(len(list(filter(lambda x: "trivially_not" in DG.node[x] and DG.node[x]["trivially_not"], DG.nodes())))))
  print("has calls and errors : " + str(len(state.has_calls_and_error)))
  print(state.has_calls_and_error)
  # assert has_calls_and_error == 0

  print("call analysis errors : " +  str(len(state.analysis_errors)))
  print("calls to dead: " + str(len(state.calls_to_dead_addr)))
  print("call to wrong: " + str(len(state.calls_to_wrong_addr)))
  print("edges: " + str(len(DG.edges())))
  print("nodes: " + str(len(DG.nodes())))
  print("loop nodes : " + str(len(state.nodes_with_loops )))
  print("self loop nodes : " + str(len(DG.nodes_with_selfloops())))
  for sl in DG.nodes_with_selfloops():
    print(sl)
  print("annotated " + str(len(list(filter(lambda x: "trustless" in DG.node[x], DG.nodes())))))
  print("annotated blocknumber " + str(len(list(filter(lambda x: "block_nr" in DG.node[x], DG.nodes())))))
  print("trustless " + str(len(list(filter(lambda x: "trustless" in DG.node[x] and DG.node[x]["trustless"], DG.nodes())))))

  print("attack annotated " + str(len(list(filter(lambda x: "attack" in DG.node[x], DG.nodes())))))
  print("attack " + str(len(list(filter(lambda x: "attack" in DG.node[x] and DG.node[x]["attack"] == True, DG.nodes())))))

  print("largest degree")
  print(list(map(lambda x: (x, DG.degree(x)),take(7, sorted(DG.nodes(), key = lambda x: DG.degree(x), reverse=True)))))

  print("largest out degree")
  print(list(map(lambda x: (x, DG.out_degree(x)),take(200, sorted(DG.nodes(), key = lambda x: DG.out_degree(x), reverse=True)))))

  print("largest in degree")
  print(list(map(lambda x: (x, DG.in_degree(x)),take(7, sorted(DG.nodes(), key = lambda x: DG.in_degree(x), reverse=True)))))
  print()

  print("the DAO")
  print(DG.node[sanatizeAddr("0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413")])
 

# MAIN
def main():
  init_state()

  if not os.path.isfile(GRAPH_FILE):
    create_graph()
    compute_trustlessness()
    safe_state()
  else:
    print("recover state...")
    recover_state()

  

  analyse_graph()


main()





  # adr = contract["address"]
  # calls = contract["calls"]
  # if calls:
  #   safe = True
  #   ctor = calls["ctor"]
  #   code = calls["code"]
  #   if ctor:
  #     #soft violation of code is law?
  #     print(str(adr) + "has calls in ctor")

  #   for call in code:
  #     adr_call = call["address"]
  #     if not adr_call:
  #       safe = False
  #     else:
  #       x=safe[adr_call]
  #       if not x:
  #         safe = False

