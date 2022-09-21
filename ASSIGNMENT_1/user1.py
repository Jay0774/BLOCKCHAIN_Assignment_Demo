# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 18:30:33 2022

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
import pandas as pd
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography import exceptions
import binascii
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import ecdsa

class User:
    
    def __init__(self):
        self.pk = None
        self.pb = None
        self.e_pb = None
        self.e_pk = None
        self.transactions = {}
        
    def get_wallet(self):
        signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.pk = signing_key.to_string().hex()
        verifying_key = signing_key.get_verifying_key()
        self.pb = bytes.decode(binascii.hexlify(verifying_key.to_string()))
        self.e_pb = hashlib.sha256(self.pb.encode()).hexdigest()
        self.e_pk = self.pk
        return self.pb,self.pk,self.e_pb,self.e_pk
    
    def create_transaction(self,receiver,amount):
        df = pd.read_csv('nodes_data.csv')
        print(df)
        r = receiver
        for i in range(df.shape[0]):
            print(df.iloc[i]['nodes'],r)
            if df.iloc[i]['nodes'] == receiver:
                r = df.iloc[i]['hash_public']
        self.transactions['sender'] = self.e_pb
        self.transactions['receiver'] = r
        self.transactions['amount'] = str(amount)
        message = hashlib.sha256(str(self.transactions['sender']+self.transactions['receiver']+self.transactions['amount']).encode()).hexdigest().encode() 
        signing_keyk = ecdsa.SigningKey.from_string(bytes.fromhex(self.pk), curve=ecdsa.SECP256k1)
        signature = signing_keyk.sign(message)
        self.transactions['message'] = bytes.decode(binascii.hexlify(message))
        self.transactions['sign'] = bytes.decode(binascii.hexlify(signature))
        #print(type(signature),type(self.e_pb))
        return self.transactions

    def flood_transaction(self,receiver,amount):
        t = self.create_transaction(receiver,str(amount))
        #print(t)
        data = []
        for i in t:
            #print(t[i])
            data.append(t[i])
        #print(data)
        df = pd.read_csv('transactions.csv')
        df.loc[df.shape[0]] = data 
        df.to_csv('transactions.csv',index=False)
        return t
    
        
    
# Creating a Web App
app = Flask(__name__)
host_name = "0.0.0.0"
localhost = "http://172.31.50.86"
port_number = 5013

# Creating user object
u = User()

# generating keys
public_key, private_key , epb , epk = u.get_wallet()


# Creating an address for the node on Port 5001
node_address = str(uuid4()).replace('-', '')

# Adding a new transaction to the Blockchain after verification
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    d = request.get_json()
    transaction_keys = ['receiver', 'amount']
    if not all(key in d for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    t = u.flood_transaction(d['receiver'], d['amount'])
    response = {'message': 'The transaction created as',
                'transaction' : t }    
    return jsonify(response), 201


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

# Running the app
app.run(host = host_name, port = port_number)