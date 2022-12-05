# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 16:05:33 2022

@author: jayga
"""


import pandas as pd
from flask import Flask, jsonify, request
import hashlib

# Creating a Web App
app = Flask(__name__)
host_name = "0.0.0.0"
port_number = 6001

# Creating queries
@app.route('/get_genesis_directly', methods = ['GET'])
def get_genesis():
    response = {}
    df = pd.read_csv('block_data.csv')
    for i in range(df.shape[0]):
        if df.iloc[i]['previous_block_hash'] == "0":
            print("Block hash of genesis block is : "+str(df.iloc[i]['block_hash']))
            print("Block index of genesis block is : "+str(df.iloc[i]['block_index']))
            response["Block hash of genesis block is : "] = str(df.iloc[i]['block_hash'])
            response["Block index of genesis block is : "] = str(df.iloc[i]['block_index'])
    return jsonify(response), 201

# Creating queries
@app.route('/get_genesis_transaction', methods = ['POST'])
def get_genesis_transaction():
    response = {}
    d = request.get_json()
    transaction_keys = ['transaction_hash']
    if not all(key in d for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    df = pd.read_csv('block_transactions_data.csv')
    for i in range(df.shape[0]):
        if df.iloc[i]['transaction_hash'] == d['transaction_hash']:
            block_hash = str(df.iloc[i]['block_hash'])
    df = pd.read_csv('block_data.csv')
    for i in range(df.shape[0]):
        if df.iloc[i]['previous_block_hash'] == "0" and df.iloc[i]['block_hash'] == block_hash:
            print("Block hash of genesis block is for given transaction hash : "+block_hash)
            response["Block hash of genesis block is : "] = str(df.iloc[i]['block_hash'])
    if len(response)==0:
        response = {
            "Error":"No genesis block found"
            }
    return jsonify(response), 201

# Creating queries
@app.route('/get_transaction_details', methods = ['GET'])
def get_transaction_details():
    h = []
    response = {}
    df = pd.read_csv('transactions.csv')
    for i in range(df.shape[0]):
        h.append([str(df.iloc[i]['sender']),str(df.iloc[i]['receiver']),str(df.iloc[i]['amount']),hashlib.sha256((str(df.iloc[i]['sender'])+str(df.iloc[i]['receiver'])+str(df.iloc[i]['amount'])).encode()).hexdigest()])
    df = pd.read_csv('block_transactions_data.csv')
    for i in range(df.shape[0]):
        for j in range(len(h)):
            if h[j][3] == df.iloc[i]['transaction_hash']:
                s = 'For transaction hash with hash as - '+str(df.iloc[i]['transaction_hash'])
                response[s] = {
                    "sender" : h[j][0],
                    "receiver" : h[j][1],
                    "amount" : h[j][2],
                    "block hash" : str(df.iloc[i]['block_hash']),
                    "transaction hash" : str(df.iloc[i]['transaction_hash'])
                    }
    return jsonify(response), 201

# Creating queries
@app.route('/get_block_details', methods = ['POST'])
def get_block_details():
    d = request.get_json()
    block_keys = ['block_hash']
    if not all(key in d for key in block_keys):
        return 'Some elements of the block are missing', 400
    response = {}
    df = pd.read_csv('block_data.csv')
    for i in range(df.shape[0]):
        if df.iloc[i]['block_hash'] == d['block_hash']:
            t = []
            df1 = pd.read_csv('block_transactions_data.csv')
            for j in range(df1.shape[0]):
                if df1.iloc[j]['block_hash'] == df.iloc[i]['block_hash']:
                    t.append(df1.iloc[j]['transaction_hash'])
            s = 'Given hash is in block index - '+str(df.iloc[i]['block_index'])
            response[s] = {
                "index" : str(df.iloc[i]['block_index']),
                "merkle root" : str(df.iloc[i]['merkle_root']),
                "previous block hash" : str(df.iloc[i]['previous_block_hash']),
                "block hash" : str(df.iloc[i]['block_hash']),
                "transaction hash" : str(t)
            }
    return jsonify(response), 201

# Creating queries
@app.route('/get_block_recent', methods = ['GET'])
def get_block_recent():
    response = {}
    df = pd.read_csv('block_data.csv')
    for i in range(df.shape[0]):
        if df.iloc[i]['block_index'] == max(df['block_index']):
            t = []
            df1 = pd.read_csv('block_transactions_data.csv')
            for j in range(df1.shape[0]):
                if df1.iloc[j]['block_hash'] == df.iloc[i]['block_hash']:
                    t.append(df1.iloc[j]['transaction_hash'])
            s = 'Recent block Height - '+str(df.iloc[i]['block_index'])
            response[s] = {
                "index" : str(df.iloc[i]['block_index']),
                "merkle root" : str(df.iloc[i]['merkle_root']),
                "previous block hash" : str(df.iloc[i]['previous_block_hash']),
                "block hash" : str(df.iloc[i]['block_hash']),
                "transaction hash" : str(t)
            }
    return jsonify(response), 201

# Creating queries
@app.route('/get_recent', methods = ['GET'])
def get_recent():
    response = {}
    df = pd.read_csv('block_data.csv')
    for i in range(df.shape[0]):
        if df.iloc[i]['block_index'] == max(df['block_index']):
            s = 'Recent Block Height'
            response[s] = str(df.iloc[i]['block_index'])
    return jsonify(response), 201

# Creating queries
@app.route('/get_average', methods = ['GET'])
def get_average():
    response = {}
    count_blocks = 0
    count_transactions = 0
    #df1 = pd.read_csv('block_data.csv')
    df2 = pd.read_csv('block_transactions_data.csv')
    transaction_count = {}
    for i in range(df2.shape[0]):
        if df2.iloc[i]['block_hash'] not in transaction_count:
            transaction_count[df2.iloc[i]['block_hash']] = [df2.iloc[i]['transaction_hash']]
        else:
            if df2.iloc[i]['transaction_hash'] not in transaction_count[df2.iloc[i]['block_hash']]:
                transaction_count[df2.iloc[i]['block_hash']].append(df2.iloc[i]['transaction_hash'])
    for i in transaction_count:
        count_transactions+=len(transaction_count[i])
        count_blocks+=1
    response["Block-hashes with transaction-hashes as per block"] = transaction_count
    response["Average number of transactions per block in complete blockchain is"] = str(count_transactions/count_blocks)
    return jsonify(response), 201

# Creating queries
@app.route('/get_summary', methods = ['GET'])
def get_summary():
    response = {}
    height = 3
    df1 = pd.read_csv('block_data.csv')
    block_hash = ""
    for i in range(df1.shape[0]):
        if df1.iloc[i]['block_index'] == height:
            block_hash = df1.iloc[i]['block_hash']
    df2 = pd.read_csv('block_transactions_data.csv')
    transaction_count = []
    for i in range(df2.shape[0]):
        if df2.iloc[i]['block_hash'] == block_hash:
            if df2.iloc[i]['transaction_hash'] not in transaction_count:
                transaction_count.append(df2.iloc[i]['transaction_hash'])
    df = pd.read_csv('transactions.csv')
    h = []
    sum_btc = 0
    for i in range(df.shape[0]):
        if hashlib.sha256((str(df.iloc[i]['sender'])+str(df.iloc[i]['receiver'])+str(df.iloc[i]['amount'])).encode()).hexdigest() in transaction_count:
            sum_btc+=int(df.iloc[i]['amount'])
            h.append([str(df.iloc[i]['amount']),hashlib.sha256((str(df.iloc[i]['sender'])+str(df.iloc[i]['receiver'])+str(df.iloc[i]['amount'])).encode()).hexdigest()])
    s = "Number of input transactions for height "+str(height)
    response[s] = str(len(transaction_count))
    response["Total Bitcoins in inputs"] = str(sum_btc)
    response["Summary"] = h
    return jsonify(response), 201

# Running the app
app.run(host = host_name, port = port_number)