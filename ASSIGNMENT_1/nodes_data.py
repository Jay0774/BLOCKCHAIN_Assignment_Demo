# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 18:32:02 2022

@author: jayga
"""

import pandas as pd
from flask import Flask, jsonify

# Creating a Web App
app = Flask(__name__)
host_name = "0.0.0.0"
port_number = 6000

# Creating data for nodes
@app.route('/create_nodes', methods = ['GET'])
def create_nodes():
    localhost = "http://172.31.50.86"
    
    minor_nodes = [
        localhost+":5001/",
        localhost+":5002/",
        localhost+":5003/",
        localhost+":5004/",
        localhost+":5005/",
        localhost+":5006/",
        localhost+":5007/",
        localhost+":5008/",
        localhost+":5009/",
        localhost+":5010/"
        ]
    user_nodes = [
        localhost+":5011/",
        localhost+":5012/",
        localhost+":5013/",
        localhost+":5014/",
        localhost+":5015/",
        localhost+":5016/",
        localhost+":5017/",
        localhost+":5018/",
        localhost+":5019/",
        localhost+":5020/",
        localhost+":5021/",
        localhost+":5022/",
        localhost+":5023/",
        localhost+":5024/",
        localhost+":5025/",
        ]
    
    d = {}
    d['nodes'] = []
    d['type'] = []
    d['public_key'] = []
    d['hash_public'] = []
    d['available'] = []
    for i in minor_nodes:
        d['nodes'].append(i)
        d['type'].append('miner')
        d['public_key'].append('none')
        d['hash_public'].append('none')
        d['available'].append(0)
    
    for i in user_nodes:
        d['nodes'].append(i)
        d['type'].append('user')
        d['public_key'].append('none')
        d['hash_public'].append('none')
        d['available'].append(0)      
    
    print(d)  
    pd.DataFrame(d).to_csv('nodes_data.csv',index=False)
    response = {'message': 'All the nodes are now created and stored in nodes_data.csv'}
    return jsonify(response), 201

# Running the app
app.run(host = host_name, port = port_number)