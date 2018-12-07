# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 8:21:05 2018

@author: Muxin
"""

import json
import time
from utils.logger import logger
from utils.tool_util import get_day, to_decimal, to_float
import zmq
import threading
import copy
import random
import csv

# 全局变量
global golbal_quot_book
golbal_quot_book = {}
quot_lock = threading.Lock()

ROBOT_USER_ID = 10640

#TRADE_FRONT_URL = 'tcp://218.17.107.70:20050'
#QUOT_FRONT_URL = 'tcp://218.17.107.70:20051'
#TRADE_FRONT_URL = 'tcp://10.1.1.200:20050'
#QUOT_FRONT_URL = 'tcp://10.1.1.200:20051'
TRADE_FRONT_URL = 'tcp://match01.citex.io:20050'
QUOT_FRONT_URL = 'tcp://quot01.citex.io:20051'

global max_level_num
max_level_num = 20

contract_id_dic = {14:'ctteth'}
price_precision_dic = {14:8}
qty_precision_dic = {14:3}
qty_size_dic = {14:0.001}

class Quot:

    #定义基本属性
    def __init__(self):
        self.contract_id = 0
        self.market_id = ''
        self.symbol = ''
        self.last_price = 0.0
        self.bid_price = []
        self.bid_qty = []
        self.ask_price = []
        self.ask_qty = []
        self.volume = 0.0
        self.turnover = 0.0
        self.time = 0

    def to_json(self):
        py2json = {}
        py2json['type'] = 'quot'
        py2json['security'] = self.symbol
        py2json['date'] = get_day()
        py2json['time'] = str(time.strftime('%H:%M:%S.000'))
        py2json['price'] = float(self.last_price)
        py2json['match_qty'] = float(self.volume)
        py2json['turnover'] = float(self.turnover)
        py2json['buy_price'] = [float(x) for x in self.bid_price[0:min(max_level_num, len(self.bid_price))]]
        py2json['buy_qty'] = [float(x) for x in self.bid_qty[0:min(max_level_num, len(self.bid_qty))]]
        py2json['sell_price'] =[float(x) for x in self.ask_price[0:min(max_level_num, len(self.ask_price))]]
        py2json['sell_qty'] = [float(x) for x in self.ask_qty[0:min(max_level_num, len(self.ask_qty))]]
        py2json['market'] = self.market_id
        py2json['interest'] = 0
        py2json['limit_up'] = 0
        py2json['limit_down'] = 0
#        logger.debug(json.dumps(py2json).encode('utf-8'))
        return json.dumps(py2json).encode('utf-8')

class Order:

    #定义基本属性
    def __init__(self):
        self.message_type = 1001
        self.contract_id = 0
        self.appl_id = 1
        self.account_id = ROBOT_USER_ID
        self.client_order_id = ''
        self.side = 1
        self.price = '0.0'
        self.quantity = '0.0'
        self.order_type = 1
        self.time_in_force = 1

    def to_json(self):
        py2json = {}
        py2json['message_type'] = self.message_type
        py2json['appl_id'] = self.appl_id
        py2json['contract_id'] = self.contract_id
        py2json['account_id'] = self.account_id
        py2json['client_order_id'] = str(time.strftime('%H:%M:%S.000'))
        py2json['side'] = self.side
        py2json['price'] = self.price
        py2json['quantity'] = self.quantity
        py2json['order_type'] = self.order_type
        py2json['time_in_force'] = self.time_in_force
#        logger.debug(json.dumps(py2json))
        return json.dumps(py2json).encode('utf-8')

class LevelParam:

    #定义基本属性
    def __init__(self):
        self.contract_id = 0
        self.max_level = 0
        self.bid_price = 0.0
        self.ask_price = 0.0
        self.step_price = []
        self.step_qty = []

class LineParam:

    #定义基本属性
    def __init__(self):
        self.contract_id = 0
        self.step_perid = []
        self.min_qty = []
        self.max_qty = []
        self.rate = 0.0

        self.next_time = 0
        self.scope_qty = []

class ExchangeQuot(threading.Thread):

    #定义基本属性
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(QUOT_FRONT_URL)
        socket.setsockopt_string(zmq.SUBSCRIBE, "")
        while True:
            message = socket.recv().decode('utf-8')
            data = json.loads(message)
#            print(data)
            if data['message_type'] == 4:
                if data['contract_id'] not in contract_id_dic:
                    continue
                contract_id = data['contract_id']
                quot = Quot()
                quot.market_id = 'ex'
                quot.contract_id = contract_id
                quot.time = time.time()
                for i in range(len(data['bids'])):
                    quot.bid_price.append(to_float(data['bids'][i]['price']))
                    quot.bid_qty.append(to_float(data['bids'][i]['quantity']))
                for i in range(len(data['asks'])):
                    quot.ask_price.append(to_float(data['asks'][i]['price']))
                    quot.ask_qty.append(to_float(data['asks'][i]['quantity']))
                quot_lock.acquire()
                golbal_quot_book[contract_id] = quot
                quot_lock.release()

class MarketMaker(threading.Thread):

    #定义基本属性
    def __init__(self):
        threading.Thread.__init__(self)
        self.levels_params = {}
        self.lines_params = {}
        self.orders = {}

        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(TRADE_FRONT_URL)

    def __send_order(self, order):
        self.socket.send(order.to_json())
        ret = self.socket.recv()
        data = json.loads(ret.decode('utf-8'))
        if 0 != data['code']:
            logger.debug(order.to_json())
            logger.debug(data['msg'])
            return False
        else:
            if order.contract_id not in self.orders:
                self.orders[order.contract_id] = []
            self.orders[order.contract_id].append((to_float(order.price), order.side, data['msg']))
            return True

    def __cancel_order(self, contract_id, original_order_id):
        py2json = {}
        py2json['message_type'] = 1003
        py2json['appl_id'] = 1
        py2json['account_id'] = ROBOT_USER_ID
        py2json['contract_id'] = contract_id
        py2json['original_order_id'] = original_order_id
        cancel_order = json.dumps(py2json).encode('utf-8')
        self.socket.send(cancel_order)
        ret = self.socket.recv()
        data = json.loads(ret.decode('utf-8'))
        if 0 != data['code']:
#            logger.debug(data)
            return False
        return True

    def __cancel_all_order(self, contract_id):
        py2json = {}
        py2json['message_type'] = 1003
        py2json['appl_id'] = 1
        py2json['account_id'] = ROBOT_USER_ID
        py2json['contract_id'] = contract_id
        cancel_order = json.dumps(py2json).encode('utf-8')
        self.socket.send(cancel_order)
        self.socket.recv()
        if contract_id in self.orders:
            self.orders[contract_id].clear()

    def __init_levels(self):
        for contract_id in self.levels_params:
            while True:
                if contract_id in golbal_quot_book:
                    break

            quot = Quot()
            quot_lock.acquire()
            quot = copy.deepcopy(golbal_quot_book[contract_id])
            quot_lock.release()

            # 全部撤单
            self.__cancel_all_order(contract_id)

            # 初始档位
            level_param = self.levels_params[contract_id]
            for side in [1, -1]:
                order = Order()
                order.contract_id = contract_id
                order.side = side
                for level in range(level_param.max_level):
                    if order.side == 1:
                        if len(quot.bid_price) != 0 and quot.bid_price[0] != 0.0:
                            bid_price = quot.bid_price[0]
                        else:
                            bid_price = level_param.bid_price
                        price = bid_price - random.uniform(level_param.step_price[0], level_param.step_price[1])
                        order.price = to_decimal(price, price_precision_dic[contract_id])
                    else:
                        if len(quot.ask_price) != 0 and quot.ask_price[0] != 0.0:
                            ask_price = quot.ask_price[0]
                        else:
                            ask_price = level_param.ask_price
                        price = ask_price + random.uniform(level_param.step_price[0], level_param.step_price[1])
                        order.price = to_decimal(price, price_precision_dic[contract_id])

                    flag = random.randint(1, 4)
                    if flag % 2 == 0:
                        coeff = 1.0 + random.uniform(1 / (level + 1), 1)
                    else:
                        coeff = 1.0 - random.uniform(1 / (level + 1), 1)
                    min_qty = level_param.step_qty[0] * coeff + qty_size_dic[contract_id]
                    max_qty = level_param.step_qty[1] * coeff + qty_size_dic[contract_id]
                    qty = random.uniform(min_qty, max_qty)
                    order.quantity = to_decimal(qty, qty_precision_dic[contract_id])
                    self.__send_order(order)

    def __get_last_price(self, quot):
        last_price = 0.0
        if quot.contract_id not in self.lines_params:
            return last_price
        line_param = self.lines_params[quot.contract_id]
        if len(quot.bid_price) >= 1 and len(quot.ask_price) >= 1:
#            last_price = (float(quot.ask_price[0]) + float(quot.bid_price[0])) / 2
#            amplitude_rate = random.uniform(0.0, 0.0005)
#            flag = random.randint(0, 3)
#            if flag % 2 == 0:
#                last_price = float(last_price * (1.0 - amplitude_rate))
#            else:
#                last_price = float(last_price * (1.0 + amplitude_rate))
#            if last_price >= quot.ask_price[0] or last_price <= quot.bid_price[0]:
#                last_price = (float(quot.ask_price[0]) + float(quot.bid_price[0])) / 2
            last_price = (float(quot.ask_price[0]) + float(quot.bid_price[0])) / 2
            flag = random.randint(1, 4)
            if flag % 2 == 0:
                last_price = random.uniform(quot.bid_price[0], last_price)
            else:
                last_price = random.uniform(last_price, quot.ask_price[0])
        else:
            if 0 == len(quot.bid_price) and 0 != len(quot.ask_price) :
                if quot.last_price > 0.0:
                    last_price = (float(quot.last_price) + float(quot.ask_price[0])) / 2
                    last_price = random.uniform(quot.ask_price[0], last_price)
                else:
                    last_price = float(quot.ask_price[0]) * (1.0 - line_param.rate)
            elif 0 != len(quot.bid_price) and 0 == len(quot.ask_price):
                if quot.last_price > 0.0:
                    last_price = (float(quot.last_price) + float(quot.bid_price[0])) / 2
                    last_price = random.uniform(last_price, quot.bid_price[0])
                else:
                    last_price = float(quot.bid_price[0]) * (1.0 + line_param.rate)
            else:
                last_price = float(quot.last_price)
        return last_price

    def __get_order_price(self, side, level_param, quot):
        if side == 1:
            bid_price = 0.0
            if len(quot.bid_price) != 0:
                bid_price = quot.bid_price[0]
            if bid_price == 0.0:
                bid_price = quot.last_price
                if bid_price == 0.0:
                    bid_price = level_param.bid_price
            price = bid_price - random.uniform(level_param.step_price[0], level_param.step_price[1])
            return to_decimal(price, price_precision_dic[quot.contract_id])
        else:
            ask_price = 0.0
            if len(quot.ask_price) != 0:
                ask_price = quot.bid_price[0]
            if ask_price == 0.0:
                ask_price = quot.last_price
                if ask_price == 0.0:
                    ask_price = level_param.ask_price
            price = ask_price + random.uniform(level_param.step_price[0], level_param.step_price[1])
            return to_decimal(price, price_precision_dic[quot.contract_id])

    def __get_qty(self, contract_id):
        line_param = self.lines_params[contract_id]
        if line_param.next_time <= time.time():
            min_qty = round(random.uniform(line_param.min_qty[0], line_param.min_qty[1]), qty_precision_dic[contract_id])
            max_qty = round(random.uniform(line_param.max_qty[0], line_param.max_qty[1]), qty_precision_dic[contract_id])
            line_param.period = random.randint(line_param.step_perid[0], line_param.step_perid[1])
            flag = random.randint(1, 4)
            if flag % 2 == 0:
                step_period = (1.0 + 0.382) * random.randint(line_param.step_perid[0], line_param.step_perid[1])
            else:
                step_period = (1.0 - 0.382) * random.randint(line_param.step_perid[0], line_param.step_perid[1])
            line_param.next_time = time.time() + step_period
            line_param.scope_qty.append(min_qty + qty_size_dic[contract_id])
            line_param.scope_qty.append(max_qty + qty_size_dic[contract_id])
        return to_decimal(random.uniform(line_param.scope_qty[0], line_param.scope_qty[1]), qty_precision_dic[contract_id])

    def __build_kline(self, contract_id, quot):
        last_price = self.__get_last_price(quot)
        if last_price != 0.0:
            qty = self.__get_qty(contract_id)

            #买单
            buy_order = Order()
            buy_order.contract_id = contract_id
            buy_order.side = 1
            buy_order.price = to_decimal(float(last_price), price_precision_dic[contract_id])
            buy_order.quantity = qty

            #卖单
            sell_order = Order()
            sell_order.contract_id = contract_id
            sell_order.side = -1
            sell_order.price = to_decimal(float(last_price), price_precision_dic[contract_id])
            sell_order.quantity = qty

            flag = random.randint(1, 4)
            if flag % 2 == 0:
                if False == self.__send_order(buy_order):
                    return False
                if False == self.__send_order(sell_order):
                    return False
            else:
                if False == self.__send_order(sell_order):
                    return False
                if False == self.__send_order(buy_order):
                    return False
            return True

    def __rebuild_levels(self, contract_id, level_param, quot):

        # 全部撤单后补单
        self.__cancel_all_order(contract_id)
        for side in [1, -1]:
            order = Order()
            order.contract_id = contract_id
            order.side = side
            for level in range(level_param.max_level):
                order.price = self.__get_order_price(side, level_param, quot)
                flag = random.randint(1, 4)
                if flag % 2 == 0:
                    coeff = 1.0 + random.uniform(1 / (level + 1), 1)
                else:
                    coeff = 1.0 - random.uniform(1 / (level + 1), 1)
                min_qty = level_param.step_qty[0] * coeff
                max_qty = level_param.step_qty[1] * coeff
                qty = random.uniform(min_qty, max_qty)
                order.quantity = to_decimal(qty, qty_precision_dic[contract_id])
                self.__send_order(order)

    def run(self):
        # 读取参数
        csv_reader = csv.reader(open("conf_levels.csv"))
        for row in csv_reader:
            level_param = LevelParam()
            level_param.contract_id = int(row[0])
            level_param.max_level = int(row[1])
            level_param.bid_price = float(row[2])
            level_param.ask_price = float(row[3])
            level_param.step_price.append(float(row[4]))
            level_param.step_price.append(float(row[5]))
            level_param.step_qty.append(float(row[6]))
            level_param.step_qty.append(float(row[7]))
            self.levels_params[level_param.contract_id] = level_param

        csv_reader = csv.reader(open("conf_lines.csv"))
        for row in csv_reader:
            line_param = LineParam()
            line_param.contract_id = int(row[0])
            line_param.rate = float(row[1])
            line_param.step_perid.append(int(row[2]))
            line_param.step_perid.append(int(row[3]))
            line_param.min_qty.append(int(row[4]))
            line_param.min_qty.append(int(row[5]))
            line_param.max_qty.append(int(row[6]))
            line_param.max_qty.append(int(row[7]))
            self.lines_params[line_param.contract_id] = line_param

        # 初始档位
        self.__init_levels()

        fill_levels_time = {}
        build_next_time = {}
        cancel_next_time = {}
        while True:
            for contract_id in contract_id_dic:
                if contract_id not in golbal_quot_book:
                    continue
                if contract_id not in self.levels_params:
                    continue

                quot = Quot()
                quot_lock.acquire()
                quot = copy.deepcopy(golbal_quot_book[contract_id])
                quot_lock.release()

                # 构造K线
                if contract_id not in build_next_time:
                    build_next_time[contract_id] = 0
                if build_next_time[contract_id] < time.time():
                    if False == self.__build_kline(contract_id, quot):
                        self.__rebuild_levels(contract_id, level_param, quot)
                    build_next_time[contract_id] = time.time() + random.randint(45, 90)

                # 补单
                if contract_id not in fill_levels_time:
                    fill_levels_time[contract_id] = (0, 0)
                if quot.time != fill_levels_time[contract_id][0] and fill_levels_time[contract_id][1] < time.time():
                    fill_levels_time[contract_id] = (quot.time, time.time() + random.randint(15, 60))
                    level_param = self.levels_params[contract_id]

                    if len(quot.bid_price) < level_param.max_level:
                        level_num = level_param.max_level - len(quot.bid_price)
                        order = Order()
                        order.contract_id = contract_id
                        order.side = 1
                        for level in range(level_num):
                            order.price = self.__get_order_price(1, level_param, quot)
                            order.quantity = self.__get_qty(contract_id)
                            self.__send_order(order)

                    if len(quot.ask_price) < level_param.max_level:
                        level_num = level_param.max_level - len(quot.ask_price)
                        order = Order()
                        order.contract_id = contract_id
                        order.side = -1
                        for level in range(level_num):
                            order.price = self.__get_order_price(1, level_param, quot)
                            order.quantity = self.__get_qty(contract_id)
                            self.__send_order(order)

                # 随机撤单
                if contract_id not in cancel_next_time:
                    cancel_next_time[contract_id] = 0
                if cancel_next_time[contract_id] < time.time():
                    cancel_next_time[contract_id] = time.time() + random.randint(15, 60)

                    if contract_id in self.orders:
                        cancel_orders = []
                        for i in range(random.randint(3, 8)):
                            while True:
                                if len(self.orders[contract_id]) - 1 == 0:
                                    idx = 0
                                else:
                                    idx = random.randint(0, len(self.orders[contract_id]) - 1)
                                cancel_order = self.orders[contract_id][idx]
                                py2json = {}
                                py2json['message_type'] = 1003
                                py2json['appl_id'] = 1
                                py2json['account_id'] = ROBOT_USER_ID
                                py2json['contract_id'] = contract_id
                                cancel_orders.append(cancel_order)
                                del self.orders[contract_id][idx]
                                if True == self.__cancel_order(contract_id, cancel_order[2]):
                                    break

                        level = 0
                        for cancel_order in cancel_orders:
                            order = Order()
                            order.contract_id = contract_id
                            order.side = cancel_order[1]
                            order.price = self.__get_order_price(order.side, level_param, quot)

                            flag = random.randint(1, 4)
                            if flag % 2 == 0:
                                coeff = 1.0 + random.uniform(1 / (level + 1), 1)
                            else:
                                coeff = 1.0 - random.uniform(1 / (level + 1), 1)
                            level = level + 1
                            min_qty = level_param.step_qty[0] * coeff + qty_precision_dic[contract_id]
                            max_qty = level_param.step_qty[1] * coeff + qty_precision_dic[contract_id]
                            qty = random.uniform(min_qty, max_qty)
                            order.quantity = to_decimal(qty, qty_precision_dic[contract_id])
                            self.__send_order(order)

                time.sleep(1)

if __name__ == '__main__':
    ex_quot = ExchangeQuot()
    ex_quot.start()

    market_maker = MarketMaker()
    market_maker.start()

    while True:
        time.sleep(3600)
