# -*- coding:utf-8 -*-

import zmq
import json

quot_pub_context = zmq.Context()
quot_pub_socket = quot_pub_context.socket(zmq.SUB)
quot_pub_socket.connect("tcp://xmu-centos7:20051")
#quot_pub_socket.connect("tcp://118.24.201.203:20061")
#quot_pub_socket.connect("tcp://10.1.1.200:20051")
#quot_pub_socket.connect("tcp://218.17.107.70:20051")
quot_pub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
while True:
    message = quot_pub_socket.recv().decode('utf-8')
    data = json.loads(message)
    print(data)
    if data['message_type'] == 4 and data['contract_id'] == 25:
        print(message)
        break
    
#    if 'range' in data:
#        if data['message_type'] == 7 and data['contract_id'] == 1 and data['range'] == "60000":
#            print(message)
#            break
