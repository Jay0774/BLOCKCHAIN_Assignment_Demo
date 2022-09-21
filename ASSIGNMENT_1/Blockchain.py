# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 18:48:18 2022

@author: jayga
"""


# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
import random
from urllib.parse import urlparse
import rsa  
import pandas as pd
import binascii
import ecdsa
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.transactions_hash = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = {'miner': [], 'user' : []}
        self.utxo = []
        self.utxo_hash = []
    
    def create_block(self, proof, previous_hash):
        block = {'index': str(len(self.chain) + 1),
                 'timestamp': str(datetime.datetime.now()),
                 'proof': str(proof),
                 'previous_hash': str(previous_hash),
                 'transactions': str(self.transactions),
                 'transactions_hash' : str(self.transactions_hash),
                 'merkle_root': str(self.create_merkle_root())}
        self.transactions = []
        self.transactions_hash = []
        self.chain.append(block)
        return block 

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = int(previous_block['proof'])
            proof = int(block['proof'])
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount,t_hash):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        self.transactions_hash.append(t_hash)
        return int(previous_block['index']) + 1
    
    def add_node(self, address,type_of_node):
        parsed_url = urlparse(address)
        self.nodes[type_of_node].append(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes['miner']
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get('http://'+node+'/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
    def create_merkle_root(self):
        l = len(self.transactions) 
        if  l == 0:
            return ""
        else:
            h = []
            for i in range(l):
                t1 = self.transactions[i]
                h1 = hashlib.sha256((str(t1['sender'])+str(t1['receiver'])+str(t1['amount'])).encode()).hexdigest()
                h.append(h1)
            while len(h)>1 :
                    if len(h)%2==1:
                        h.append(h[-1])
                    print(h)
                    j = 0 
                    for i in range(len(h)-1):
                        h[j]=hashlib.sha256(str(h[i]+h[i+1]).encode()).hexdigest()
                        i = i + 2
                        j = j + 1
                    index_to_delete = i-j
                    del h[-index_to_delete:]
            print(h)
            merkle_root = str(h[0])
        return merkle_root
    
    def get_wallet(self):
        signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.pk = signing_key.to_string().hex()
        verifying_key = signing_key.get_verifying_key()
        self.pb = bytes.decode(binascii.hexlify(verifying_key.to_string()))
        self.e_pb = hashlib.sha256(self.pb.encode()).hexdigest()
        self.e_pk = self.pk
        return self.pb,self.pk,self.e_pb,self.e_pk
    
    def update_utxo(self):
        transactions = blockchain.transactions
        df = pd.read_csv('transactions.csv')
        message = ""
        for i in transactions:
            print(i)
            h = hashlib.sha256((str(i['sender'])+str(i['receiver'])+str(i['amount'])).encode()).hexdigest()
            for j in range(df.shape[0]):
                if df.iloc[j]['receiver'] == i['sender']:
                    if int(i['amount']) < int(df.iloc[j]['amount']):
                        message = "Not enough amount transaction declined..."
                        blockchain.transactions.remove(i)
                    else:
                        if h in self.utxo_hash:
                            blockchain.transactions.remove(i)
                            message = "Double spending transaction declined..."
                        else:
                            message = "Transaction added in utxo..."
                            if int(df.iloc[j]['amount']) == int(i['amount']):
                                self.utxo.append({'in':i['sender'],'out':i['receiver'],'amount':i['amount'],'hash':h})
                                self.utxo_hash.append(h)
                            else:
                                self.utxo.append({'in':i['sender'],'out':i['receiver'],'amount':i['amount'],'hash':h})
                                self.utxo_hash.append(h)
                                h = hashlib.sha256((str(i['sender'])+str(i['receiver'])+str(int(df.iloc[j]['amount'])-int(i['amount'])).encode())).hexdigest()
                                self.utxo.append({'in':i['sender'],'out':i['sender'],'amount':str(int(df.iloc[j]['amount'])-int(i['amount'])),'hash': h})
                                self.utxo_hash.append(h)
        print(message)
    
# Creating a Web App
app = Flask(__name__)
host_name = "0.0.0.0"
localhost = "http://172.31.50.86"
port_number = 5001

# Creating an address for the node on Port 5001
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# generating keys
public_key, private_key , epb , epk = blockchain.get_wallet()

# printing the key pair
@app.route('/get_key_pair', methods = ['GET'])
def get_pair():
    df = pd.read_csv('nodes_data.csv')
    for i in range(df.shape[0]):
        if df.iloc[i]['nodes'] == str(localhost+':'+str(port_number)+'/'):
            df.loc[i] = [str(localhost+':'+str(port_number)+'/'),
                         df.iloc[i]['type'],
                         public_key
                         ,epb,1]
    df.to_csv('nodes_data.csv',index = False)
    print('Appended')
    response = {'public_key': epb,
                'private_key': epk }
    return jsonify(response), 200

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = int(previous_block['proof'])
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    response = {'message': 'Congratulations, you just mined a block!',
                'transactions' : []
                }
    blockchain.update_utxo()
    for i in range(len(blockchain.transactions)):
        r = {}
        r['sender'] = str(blockchain.transactions[i]['sender'])
        r['receiver'] = str(blockchain.transactions[i]['receiver'])
        r['amount'] = str(blockchain.transactions[i]['amount'])
        response['transactions'].append(hashlib.sha256((str(r['sender'])+str(r['receiver'])+str(r['amount'])).encode()).hexdigest())
    block = blockchain.create_block(proof, previous_hash)
    response['index'] = block['index']
    response['timestamp'] = block['timestamp']
    response['proof'] = block['proof']
    response['previous_hash'] = block['previous_hash']
    response['merkle_root'] = block['merkle_root']
    # blockchain.add_transaction(sender = node_address, receiver = 'LV', amount = 1)
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Getting the utx's in Blockchain
@app.route('/get_utxo', methods = ['GET'])
def get_utxo():
    response = {'chain': str(blockchain.chain),
                'utxo': str(blockchain.utxo)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain after verification
@app.route('/add_transactions', methods = ['GET'])
def add_transactions():
    df = pd.read_csv('nodes_data.csv')
    node = []
    for i in range(df.shape[0]):
        print(df.iloc[i]['nodes'][7:-1])
        if df.iloc[i]['nodes'][7:-1] in blockchain.nodes['user']:
            node.append([df.iloc[i]['nodes'],df.iloc[i]['public_key'],df.iloc[i]['hash_public']])
    print(node)
    df = pd.read_csv('transactions.csv')
    s = []
    for i in range(df.shape[0]):
        for j in range(len(node)):
            if df.iloc[i]['sender'] == node[j][2]:
                #print(d1.iloc[0]['hash_public'])
                verifying_key = binascii.unhexlify(str.encode(node[j][1]))
                pb = ecdsa.VerifyingKey.from_string(verifying_key, curve=ecdsa.SECP256k1)
                #print(binascii.unhexlify(str.encode(d2.iloc[i]['sign'])),binascii.unhexlify(str.encode(d2.iloc[i]['message'])))
                if pb.verify(binascii.unhexlify(str.encode(df.iloc[i]['sign'])),binascii.unhexlify(str.encode(df.iloc[i]['message']))):
                    s.append(str("For Transaction ID " + str(i+1) + " - Signature verified"))
                    h = hashlib.sha256((str(df.iloc[i]['sender'])+str(df.iloc[i]['receiver'])+str(df.iloc[i]['amount'])).encode()).hexdigest()
                    blockchain.add_transaction(df.iloc[i]['sender'],df.iloc[i]['receiver'],df.iloc[i]['amount'],h)
                else:
                    s.append(str("For Transaction ID " + str(i+1) + " - Signature not verified"))
    l = len(s)
    response = {'message': f'Number of transaction verified tranactions added to Block after digital signature matching are {l}',
                'responses': s}    
    return jsonify(response), 201

# Creating a new transaction
@app.route('/print_transactions', methods = ['GET'])
def print_transactions():
    response = {'message': 'Transactions in current Block are',
                }
    s = "transaction"
    for i in range(len(blockchain.transactions)):
        response[s+str(i)] = {}
        response[s+str(i)]['sender'] = str(blockchain.transactions[i]['sender'])
        response[s+str(i)]['receiver'] = str(blockchain.transactions[i]['receiver'])
        response[s+str(i)]['amount'] = str(blockchain.transactions[i]['amount'])
    print(response)
    return jsonify(response), 201


# Part 3 - Decentralizing our Blockchain

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Connecting new nodes
@app.route('/connect_node', methods = ['GET'])
def connect_node():
    blockchain.nodes = {'miner': [], 'user' : []}
    df = pd.read_csv('nodes_data.csv')
    m_nodes = []
    u_nodes = []
    for i in range(df.shape[0]):
        if df.iloc[i]['type']=='miner' and int(df.iloc[i]['available']) == 1:
            m_nodes.append(df.iloc[i]['nodes'])
        elif df.iloc[i]['type']=='user' and int(df.iloc[i]['available']) == 1:
            u_nodes.append(df.iloc[i]['nodes'])
    print(m_nodes)
    print(u_nodes)
    if m_nodes is None:
        return "No Minor node", 400
    for node in m_nodes:
        if int(node[20:24]) != port_number:
            print(node)
            blockchain.add_node(node,'miner')
    if u_nodes is None or len(u_nodes) < 2:
        return "No User nodes available", 400
    n = random.randint(2,10)
    for i in range(n):
        x = random.randint(0,len(u_nodes)-1)
        if int(u_nodes[x][20:24]) != port_number and u_nodes[x] not in blockchain.nodes['user']:
            blockchain.add_node(u_nodes[x],'user')
    response = {'message': 'All the nodes are now connected. The Blockchain now contains the following nodes:',
                'total_nodes': blockchain.nodes}
    return jsonify(response), 201

# Printing Connected nodes
@app.route('/print_node', methods = ['GET'])
def print_node():
    response = {'message': 'The Blockchain contains the following nodes:',
                'total_nodes': blockchain.nodes}
    return jsonify(response), 201


# Running the app
app.run(host = host_name, port = port_number)