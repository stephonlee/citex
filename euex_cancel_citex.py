# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 8:21:05 2018

@author: Muxin
"""

import json
import zmq

TRADE_FRONT_URL = 'tcp://match01.citex.io:20050'

if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(TRADE_FRONT_URL)

    accounts = [10641, 10634, 10632, 10635, 10646, 10647, 10648]

    # 全部撤单
    for account_id in accounts:
        py2json = {}
        py2json['message_type'] = 1003
        py2json['appl_id'] = 1
        py2json['account_id'] = account_id 
        py2json['contract_id'] = 0
        cancel_order = json.dumps(py2json).encode('utf-8')
        socket.send(cancel_order)
        socket.recv()
        print('cancel all success')
    
