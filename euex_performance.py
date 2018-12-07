# -*- coding: utf-8 -*-

import zmq
import time
import datetime
import json
#import random

def SendOrder(accountid, contractid, side, price, qty, ordertype):
    py2json = {}
    py2json['message_type'] = 1001
    py2json['appl_id'] = 1
    py2json['contract_id'] = contractid
    py2json['account_id'] = accountid
    py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
    py2json['side'] = side  # random.choice([1, -1])
    py2json['price'] = str(price  * 1000000000000000000)
    py2json['quantity'] = str(qty * 1000000000000000000)
    py2json['order_type'] = ordertype
    py2json['time_in_force'] = 1
    str_json = json.dumps(py2json).encode('utf-8')
    # print(str_json)
    ret = ""

    socket.send(str_json)
    ret = socket.recv()
    # print(ret)
    json1 = ''
    if b'"code":0' in ret:
        json1 = (str(ret[37:len(ret) - 2]))
    else:
        json1 = 'ERROR'
        return json1
    return json1[2: len(json1) - 1]

def CancelOrder(account_id,contract_id, original_order_id):
    py2json = {}
    py2json['message_type'] = 1003
    py2json['appl_id'] = 1
    py2json['contract_id'] = contract_id
    py2json['account_id'] = account_id
    py2json['original_order_id'] = original_order_id
        # py2json['side'] = 1
    str_json = json.dumps(py2json).encode('utf-8')

    # print(str_json)
    socket.send(str_json)
    ret = socket.recv()
    # print(ret)
    return ret 

def CheckEqual(myret, expectedret):
    if expectedret in myret:
        return True
    else:
        pass 
        # print (b"!!!!!!!!!!!!!!!!!!!!" + myret + b" != " + expectedret)

def CheckNotEqual(myret, expectedret):
    if expectedret not in myret:
        return True
    else:
        pass
        # print (b"!!!!!!!!!!!!!!!!!!!!" + myret + b" == " + expectedret)

def CancelAndCehck(is_equal, account_id,contract_id,orig_idx, cancel_succ_reason):
    if 'ERROR' not in orig_idx:
        reason = CancelOrder(account_id,contract_id, orig_idx)
        if is_equal:
            CheckEqual(reason, cancel_succ_reason)
        else:
            CheckNotEqual(reason, cancel_succ_reason)
    else:
        # print ("!!!!!!!!!!!!!!!!!!!!Send Order ERROR!!!")
        pass

cancel_succ_reason = b'cancel order success'

# 测试内容
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:20067")

# 80 * 100
start_time = datetime.datetime.now()
print(start_time)

for i in range(50000):
	# 下单
	ret1 = SendOrder(6, 1, 1, 1, 1, 1)
	ret2 = SendOrder(1, 1, -1, 1, 1, 1)
	ret3 = SendOrder(1, 1, 1, 1, 1, 1)
	CancelAndCehck(True, 1, 0, ret3, cancel_succ_reason)

end_time = datetime.datetime.now()
duration = ((end_time - start_time).seconds)

performance = 50000 * 4 / duration

print("Performance: %d", performance)
