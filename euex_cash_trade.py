# -*- coding:utf-8 -*-

import zmq
import time
import datetime
import json
from utils.tool_util import to_decimal

context = zmq.Context()
#socket = context.socket(zmq.DEALER)
socket = context.socket(zmq.REQ)    
#socket.connect("tcp://47.91.207.218:20050")
#socket.connect("tcp://47.91.207.218:20060")
#socket.connect("tcp://172.31.6.246:20050")
#socket.connect("tcp://218.17.107.70:20050")
#socket.connect("tcp://47.75.136.2:20050")
socket.connect("tcp://xmu-centos7:20050")
#socket.connect("tcp://118.24.201.203:20055")
TRADE_SERVER_URL = 'tcp://xmu-centos7:20050'

def send_msg(str_json):
#    ret = ""
#    start_time = datetime.datetime.now()
#    socket.send(str_json)
#    ret = socket.recv()
#    print(ret)
#    end_time = datetime.datetime.now()
#    print((end_time - start_time).seconds)
    socket.send(str_json)
    socket.recv()
  
## 现货下单
#py2json = {}
#py2json['message_type'] = 1001
#py2json['appl_id'] = 1
#py2json['contract_id'] = 1
#py2json['account_id'] = 6
#py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
#py2json['side'] = 1 
#py2json['price'] = to_decimal(0.1)
#py2json['quantity'] = to_decimal(0.1)
#py2json['order_type'] = 1
#py2json['time_in_force'] = 1
#str_json = json.dumps(py2json).encode('utf-8')
#send_msg(str_json)
#
## 现货撤单
#py2json = {}
#py2json['message_type'] = 1003
#py2json['appl_id'] = 1
#py2json['account_id'] = 6
#py2json['contract_id'] = 1
#py2json['original_order_id'] = '1542217504384330'
#str_json = json.dumps(py2json).encode('utf-8')
##print(str_json)
#send_msg(str_json)
#
## 现货一键撤单
#py2json = {}
#py2json['message_type'] = 1003
#py2json['appl_id'] = 1
#py2json['account_id'] = 6
#py2json['contract_id'] = 0
#str_json = json.dumps(py2json).encode('utf-8')
##print(str_json)
#send_msg(str_json)

## 交易对挂牌、更新
#py2json = {}
#py2json['message_type'] = 5007
#py2json['appl_id'] = 1
#py2json['contract_id'] = 18
#py2json['symbol'] = 'ENTBTC'
#py2json['price_tick'] = "2000000000000000"
#py2json['lot_size'] = "2000000000000000"
#py2json['taker_fee_ratio'] = "2000000000000000"
#py2json['maker_fee_ratio'] = "2000000000000000"
#py2json['limit_max_level'] = 10
#py2json['market_max_level'] = 10
#py2json['price_limit_rate'] = "2000000000000000"
#py2json['max_num_orders'] = 100
#py2json['commodity_id'] = 1
#py2json['currency_id'] = 2
#py2json['contract_status'] = 2
#py2json['list_time'] = int(time.time() * 1000)
#py2json['type'] = 3
#str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
#send_msg(str_json)
#
## 现货交易参数更新
#py2json = {}
#py2json['message_type'] = 5004
#py2json['appl_id'] = 13
#py2json['contract_id'] = 13
#py2json['account_id'] = 7
#py2json['type'] = 1
#py2json['forbid_trade'] = 0
#py2json['taker_fee_ratio'] = to_decimal(0.002)
#py2json['maker_fee_ratio'] = to_decimal(0.001)
#str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
#send_msg(str_json)

# 转账
py2json = {}
py2json['message_type'] = 4005
py2json['account_id'] = 13
py2json['currency_id'] = 7
py2json['from_appl_id'] = 5
py2json['to_appl_id'] = 1
py2json['quantity'] = to_decimal(555)
py2json['id'] = 1540727468003
str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
send_msg(str_json)
    
## 批量转账
#last_id = int(time.time())
#while True:
#    py2json = {}
#    py2json['message_type'] = 1001
#    py2json['appl_id'] = 1
#    py2json['contract_id'] = 1
#    py2json['account_id'] = 6
#    py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
#    py2json['side'] = 1 
#    py2json['price'] = to_decimal(0.1)
#    py2json['quantity'] = to_decimal(0.1)
#    py2json['order_type'] = 1
#    py2json['time_in_force'] = 1
#    str_json = json.dumps(py2json).encode('utf-8')
#    send_msg(str_json)
#    
#    py2json = {}
#    py2json['message_type'] = 1001
#    py2json['appl_id'] = 1
#    py2json['contract_id'] = 1
#    py2json['account_id'] = 1
#    py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
#    py2json['side'] = -1 
#    py2json['price'] = to_decimal(0.1)
#    py2json['quantity'] = to_decimal(0.1)
#    py2json['order_type'] = 1
#    py2json['time_in_force'] = 1
#    str_json = json.dumps(py2json).encode('utf-8')
#    send_msg(str_json)
#
#    py2json = {}
#    py2json['message_type'] = 4007
#    py2json['transfers'] = []    
#    for account_id in range(1, 1001):
#        transfer2json = {}
#        transfer2json['account_id'] = account_id
#        transfer2json['currency_id'] = 1
#        transfer2json['from_appl_id'] = 5
#        transfer2json['to_appl_id'] = 8
#        transfer2json['quantity'] = "-11000100000000000000"
#        last_id = last_id + 1
#        transfer2json['id'] = last_id
#        py2json['transfers'].append(transfer2json)
#    str_json = json.dumps(py2json).encode('utf-8')
##    print(str_json)
#    send_msg(str_json)
##    time.sleep(0.1)

## 账号更新
#accounts = []
#py2json = {}
#py2json['account_id'] = 6
#py2json['appl_id'] = 1
#py2json['currency_id'] = 1
#py2json['total_money'] = "50000000000000000000"
#py2json['order_frozen_money'] = "40000000000000000000"
#py2json['posi_profit_loss'] = "30000000000000000000"
#accounts.append(py2json)
#py2json = {}
#py2json['account_id'] = 6
#py2json['appl_id'] = 1
#py2json['currency_id'] = 2
#py2json['total_money'] = "50000000000000000000"
#py2json['order_frozen_money'] = "40000000000000000000"
#py2json['posi_profit_loss'] = "30000000000000000000"
#accounts.append(py2json)
#py2json = {}
#py2json['message_type'] = 4006
#py2json['accounts'] = accounts 
#str_json = json.dumps(py2json).encode('utf-8')
#
## 获取系统状态
#py2json = {}
#py2json['message_type'] = 3007
#str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
#
## 更新系统状态
#py2json = {}
#py2json['message_type'] = 5001
#py2json['sys_status'] = 0
#str_json = json.dumps(py2json).encode('utf-8')
#print(str_json)
