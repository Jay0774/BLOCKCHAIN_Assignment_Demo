# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 19:36:38 2022

@author: jayga
"""

import pandas as pd
from flask import Flask, jsonify
from cryptography import exceptions
import binascii
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import ecdsa

# Creating a Web App
app = Flask(__name__)
host_name = "0.0.0.0"
port_number = 6001

# Creating data for nodes
@app.route('/verify', methods = ['GET'])
def verify():
    d1 = pd.read_csv('nodes_data.csv')
    d2 = pd.read_csv('transactions.csv')
    s = []
    for i in range(d2.shape[0]):
        for j in range(d1.shape[0]):
            if d2.iloc[i]['sender'] == d1.iloc[j]['hash_public']:
                #print(d1.iloc[0]['hash_public'])
                verifying_key = binascii.unhexlify(str.encode(d1.iloc[j]['public_key']))
                pb = ecdsa.VerifyingKey.from_string(verifying_key, curve=ecdsa.SECP256k1)
                #print(binascii.unhexlify(str.encode(d2.iloc[i]['sign'])),binascii.unhexlify(str.encode(d2.iloc[i]['message'])))
                if pb.verify(binascii.unhexlify(str.encode(d2.iloc[i]['sign'])),binascii.unhexlify(str.encode(d2.iloc[i]['message']))):
                    s.append(str("For Transaction ID " + str(i+1) + " - Signature verified"))
                else:
                    s.append(str("For Transaction ID " + str(i+1) + " - Signature not verified"))
                #print(s)
    response = {'message': s}
    return jsonify(response), 201

# Running the app
app.run(host = host_name, port = port_number)