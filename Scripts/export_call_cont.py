
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



# Methods 

def isTruestless(node_name, visited):
  if node_name in visited:
    state.nodes_with_loops[node_name] = visited 
    #print(node_name + " has a dep loop")
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
  global DG, state
  DG=nx.DiGraph()
  state = State()
  # Add hardcoded lib contract addresses to active contracts
  for addr in HARDCODED_ADDRESSES:
    state.active_contracts[sanatizeAddr(addr)]=True

def handle_analysis_error(contract, block, addr):
  # special case should not happen
  if "calls" in contract:
    #print(contract["calls"])
    state.has_calls_and_error[addr] = True
  state.analysis_errors[addr] = True
  DG.add_node(addr, trustless = False, block_nr = block, trivially_not = True)

def handle_has_calls(calls, block, addr):
  ctor = calls["ctor"]
  code = calls["code"]

  # if has call in ctor not really a violation as long as payload has fixed addresses
  if ctor:
    #soft violation of code is law?
    state.calls_in_ctor[addr] = True
    #print(str(addr) + " has calls in ctor: Soft violation of code is law?")

  # considred trivially not safe if one call not static
  triviallyNotSafe = any(sanatizeAddr(call["address"]) == None for call in code)
  if triviallyNotSafe:
    DG.add_node(addr, trustless = False, block_nr = block, trivially_not = True)
  else:
    #safe until one of the successors is not safe
    DG.add_node(addr, block_nr = block)

  # ADD EDGES
  for call in code:
    call_addr = sanatizeAddr(call["address"])
    
    if call_addr == None:
      DG.add_edge(addr, UNKNOWNNAME)
    else:
      # only include calls to active contracts
      if call_addr in state.active_contracts:
        DG.add_edge(addr, call_addr)
      else:
        # not an active contract therefore a call to it is safe, because no code is executed just returns
        #print(str(call_addr) + " not active")

        if not call_addr in state.disabled_contracts:
          # not active anymore but was a contract at one time (suicide)
          incOrAdd(state.calls_to_wrong_addr, call_addr)
        else:
          # not active... calls crap address?
          incOrAdd(state.calls_to_dead_addr, call_addr)
      
def create_graph(from_b, to_b):
  # MONGO
  collection = getContractsCollectionMongoDB()
  # MONGO FILTERS
  nonNullBytecode = {"bytecode": { "$not": { "$eq": None}}}
  nullBytecode = {"bytecode": None}

  block_gt = {"block_number": {"$gt": from_b }}
  block_lt = {"block_number": {"$lt": to_b }}
  suicide_block_gt = {"suicide_block": {"$gt": to_b }}
  suicide_not_exists = {"suicide_block": {"$exists": False}}
  suicide_or_not_exists = {"$or": [suicide_block_gt, suicide_not_exists]}

  suicide_smaller_than_to = {"suicide_block": {"$lt": to_b }}

  # INIT Active Contracts
  contracts = collection.find({"$and": [block_gt, block_lt, suicide_or_not_exists]})
  for c in contracts:
    state.active_contracts[sanatizeAddr(c["address"])] = True

  # INIT Disabled Contracts
  contracts = collection.find({ "$and": [suicide_smaller_than_to]})
  for c in contracts:
    state.disabled_contracts[sanatizeAddr(c["address"])] = True

  # INIT FIXED GRAPH NODES With trustless properties
  DG.add_node(UNKNOWNNAME, trustless = False)
  # hardcoded are assumed safe
  for adr in HARDCODED_ADDRESSES:
    DG.add_node(sanatizeAddr(adr), trustless = True)

  # LOAD ALL ACTIVE CONTRACTS
  contracts = collection.find({ "$and": [block_gt, block_lt, suicide_or_not_exists]}) # .limit(10000)
  nr = contracts.count()
  i = 0

  # ITER CONTRACTS AND GENERATE GRAPH
  for contract in contracts:
    i += 1
    adr = sanatizeAddr(contract["address"])
    block = contract["block_number"]

    # sort out contracts with analysis errors assume we do not trust them
    if "calls_error" in contract:
      #print(str(i) + "/" + str(nr) + " : " + str(adr) + ": Assume not trustless because analysis error")
      handle_analysis_error(contract, block, adr)
      continue

    calls = contract["calls"]

    if calls:
      #print(str(i) + "/" + str(nr) + " : " + str(adr) + ": not Trivially trustless")
      handle_has_calls(calls, block, adr)
    else:
      #Case Trivially trustless because no interaction.
      #print(str(i) + "/" + str(nr) + " : " + str(adr) + ": Trivially trustless")
      DG.add_node(adr, trustless = True, block_nr = block, trivially = True)

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
    #print(str(i) + "/" + str(nr) + " : " + str(node_name) + "")
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
  print("annotated " + str(len(list(filter(lambda x: "trustless" in DG.node[x], DG.nodes())))))
  print("annotated blocknumber " + str(len(list(filter(lambda x: "block_nr" in DG.node[x], DG.nodes())))))
  print("trustless " + str(len(list(filter(lambda x: "trustless" in DG.node[x] and DG.node[x]["trustless"], DG.nodes())))))

  print("largest degree")
  print(take(5, sorted(DG.nodes(), key = lambda x: DG.degree(x), reverse=True)))

  print("largest out degree")
  print(take(5, sorted(DG.nodes(), key = lambda x: DG.out_degree(x), reverse=True)))

  print("largest in degree")
  print(take(5, sorted(DG.nodes(), key = lambda x: DG.in_degree(x), reverse=True)))
  print()

def printRange(f, t):
  init_state()

  create_graph(f, t)
  
  compute_trustlessness()

  trustless = len(list(filter(lambda x: "trustless" in DG.node[x] and DG.node[x]["trustless"], DG.nodes())))
  all_nodes = len(list(filter(lambda x: "trustless" in DG.node[x], DG.nodes())))
  print("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9}".format(f,t, trustless, all_nodes, len(DG.nodes()), len(state.calls_to_dead_addr), len(state.calls_to_wrong_addr), len(state.analysis_errors), len(state.nodes_with_loops ), len(DG.nodes_with_selfloops()) ))


# MAIN
def main():
  MAX = 3633433
  STEP = 100000
  i=0
  print("from_block;to_block;count;count_all;nodes;calls_to_dead;calls_to_wrong;analysis_errors;loops;selfloops")
  while i <= MAX:
    n_i = i + STEP
    printRange(0, min(n_i, MAX))
    i = n_i



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

