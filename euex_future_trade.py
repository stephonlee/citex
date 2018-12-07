# -*- coding:utf-8 -*-

import zmq
import time
import datetime
import json
from utils.tool_util import to_decimal

context = zmq.Context()
socket = context.socket(zmq.DEALER)
#socket.connect("tcp://47.91.207.218:20050")
#socket.connect("tcp://47.91.207.218:20060")
#socket.connect("tcp://172.31.6.246:20050")
#socket.connect("tcp://218.17.107.70:20050")
#socket.connect("tcp://47.75.136.2:20050")
socket.connect("tcp://xmu-centos7:20050")
#socket.connect("tcp://118.24.201.203:20055")

def send_msg(str_json):
    ret = ""
    start_time = datetime.datetime.now()
    socket.send(str_json)
    ret = socket.recv()
    print(ret)
    end_time = datetime.datetime.now()
    print((end_time - start_time).seconds)

## 期货下单
#py2json = {}
#py2json['message_type'] = 1001
#py2json['appl_id'] = 2
#py2json['contract_id'] = 100
#py2json['account_id'] = 6
#py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
#py2json['side'] = 1 
#py2json['price'] = to_decimal(6400)
#py2json['quantity'] = to_decimal(100)
#py2json['order_type'] = 1
#py2json['time_in_force'] = 1
#py2json['position_effect'] = 1
##py2json['margin_type'] = 2
##py2json['margin_rate'] = to_decimal(0.1)
#py2json['margin_type'] = 1
#py2json['margin_rate'] = "0"
#str_json = json.dumps(py2json).encode('utf-8')
##print(str_json)
#send_msg(str_json)
#
## 期货撤单
#py2json = {}
#py2json['message_type'] = 1003
#py2json['appl_id'] = 2
#py2json['account_id'] = 13
#py2json['contract_id'] = 100
#py2json['original_order_id'] = '11543539801800363'
#str_json = json.dumps(py2json).encode('utf-8')
##print(str_json)
#send_msg(str_json)
#    
## 期货一键撤单
#py2json = {}
#py2json['message_type'] = 1008
#py2json['appl_id'] = 2
#py2json['account_id'] = 6
#py2json['contract_id'] = 0
#str_json = json.dumps(py2json).encode('utf-8')
##print(str_json)
#send_msg(str_json)
#    
## 期货更新保证金率
#py2json = {}
#py2json['message_type'] = 1012
#py2json['appl_id'] = 2
#py2json['contract_id'] = 102
#py2json['account_id'] = 6
#py2json['margin_type'] = 2
#py2json['init_margin_rate'] = to_decimal(1)
##py2json['margin_type'] = 1
##py2json['init_margin_rate'] = "0"
#str_json = json.dumps(py2json).encode('utf-8')
##print(str_json)
#send_msg(str_json)
#
## 期货更新保证金
#py2json = {}
#py2json['message_type'] = 1013
#py2json['appl_id'] = 2
#py2json['contract_id'] = 100
#py2json['account_id'] = 6
#py2json['margin'] = to_decimal(-1)
#str_json = json.dumps(py2json).encode('utf-8')
###print(str_json)
#send_msg(str_json)

py2json = {}
py2json['message_type'] = 1001
py2json['appl_id'] = 2
py2json['contract_id'] = 100
py2json['account_id'] = 6
py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
py2json['side'] = 1 
py2json['price'] = to_decimal(6400)
py2json['quantity'] = to_decimal(80)
py2json['order_type'] = 1
py2json['time_in_force'] = 1
py2json['position_effect'] = 1
#py2json['margin_type'] = 2
#py2json['margin_rate'] = to_decimal(0.05)
py2json['margin_type'] = 1
py2json['margin_rate'] = "0"
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)

py2json = {}
py2json['message_type'] = 1001
py2json['appl_id'] = 2
py2json['contract_id'] = 100
py2json['account_id'] = 7
py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
py2json['side'] = -1 
py2json['price'] = to_decimal(6400)
py2json['quantity'] = to_decimal(80)
py2json['order_type'] = 1
py2json['time_in_force'] = 1
py2json['position_effect'] = 1
py2json['margin_type'] = 2
py2json['margin_rate'] = to_decimal(0.05)
#py2json['margin_type'] = 1
#py2json['margin_rate'] = "0"
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)

py2json = {}
py2json['message_type'] = 1001
py2json['appl_id'] = 2
py2json['contract_id'] = 100
py2json['account_id'] = 6
py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
py2json['side'] = 1 
py2json['price'] = to_decimal(6400)
py2json['quantity'] = to_decimal(10)
py2json['order_type'] = 1
py2json['time_in_force'] = 1
py2json['position_effect'] = 1
#py2json['margin_type'] = 2
#py2json['margin_rate'] = to_decimal(0.05)
py2json['margin_type'] = 1
py2json['margin_rate'] = "0"
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)

py2json = {}
py2json['message_type'] = 1001
py2json['appl_id'] = 2
py2json['contract_id'] = 101
py2json['account_id'] = 6
py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
py2json['side'] = 1 
py2json['price'] = to_decimal(6400)
py2json['quantity'] = to_decimal(10)
py2json['order_type'] = 1
py2json['time_in_force'] = 1
py2json['position_effect'] = 1
py2json['margin_type'] = 2
py2json['margin_rate'] = to_decimal(0.05)
#py2json['margin_type'] = 1
#py2json['margin_rate'] = "0"
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)

py2json = {}
py2json['message_type'] = 1001
py2json['appl_id'] = 2
py2json['contract_id'] = 102
py2json['account_id'] = 6
py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
py2json['side'] = -1 
py2json['price'] = to_decimal(6400)
py2json['quantity'] = to_decimal(10)
py2json['order_type'] = 1
py2json['time_in_force'] = 1
py2json['position_effect'] = 1
py2json['margin_type'] = 2
py2json['margin_rate'] = to_decimal(0.05)
#py2json['margin_type'] = 1
#py2json['margin_rate'] = "0"
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)

py2json = {}
py2json['message_type'] = 1001
py2json['appl_id'] = 2
py2json['contract_id'] = 103
py2json['account_id'] = 6
py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
py2json['side'] = -1 
py2json['price'] = to_decimal(6400)
py2json['quantity'] = to_decimal(10)
py2json['order_type'] = 1
py2json['time_in_force'] = 1
py2json['position_effect'] = 1
#py2json['margin_type'] = 2
#py2json['margin_rate'] = to_decimal(0.05)
py2json['margin_type'] = 1
py2json['margin_rate'] = "0"
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)

py2json = {}
py2json['message_type'] = 5008
py2json['appl_id'] = 2
py2json['commodity_id'] = 2
py2json['currency_id'] = 7
py2json['index_price'] = to_decimal(5252.4)
py2json['funding_basis'] = '0'
py2json['market_id'] = ''
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)

py2json = {}
py2json['message_type'] = 5008
py2json['appl_id'] = 2
py2json['commodity_id'] = 2
py2json['currency_id'] = 7
py2json['index_price'] = to_decimal(5169.1)
py2json['funding_basis'] = '0'
py2json['market_id'] = ''
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)
