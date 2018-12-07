# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 8:21:05 2018

@author: Muxin
"""

import json
import time
from utils.logger import logger
from binance.client import Client
from binance.websockets import BinanceSocketManager
from websocket import create_connection
from utils.tool_util import get_day, to_decimal, get_price, to_float
import zmq
import threading
import copy
import random
import gzip

# 全局变量
global golbal_quot_book
golbal_quot_book = {}
global golbal_exquot_book
golbal_exquot_book = {}

quot_lock = threading.Lock()
exquot_lock = threading.Lock()

MAX_LEVEL_NUM = 20

###############################################################################

#TRADE_FRONT_URL = 'tcp://218.17.107.70:20050'
#QUOT_FRONT_URL = 'tcp://218.17.107.70:20051'
#
#contract_id_dic = {'ethbtc':1,
#                   'btcusdt':21, 'ethusdt': 16,
#                   'wtcbtc': 34, 'wtceth': 41, 
#                   'omgbtc': 35, 'omgeth': 42,
#                   'zilbtc': 38, 'zileth': 45,
#                   'icxbtc': 39, 'icxeth': 46}
#price_precision_dic = {1:6,
#                       21:6, 16:6,
#                       34:7, 41:6,
#                       35:6, 42:6,
#                       38:8, 45:8,
#                       39:7, 46:6}
#qty_precision_dic = {1:5,
#                     21:5, 16:5,
#                     34:3, 41:3,
#                     35:3, 42:3,
#                     38:3, 45:3,
#                     39:3, 46:3}
#qty_size_dic = {1:0.00001,
#                21:0.00001, 16:0.00001,
#                34:0.001, 41:0.001,
#                35:0.001, 42:0.001,
#                38:0.001, 45:0.001,
#                39:0.001, 46:0.001}
#
#contract_vs_user = {1:1654,
#                    21:1656, 16:1655,
#                    34:1652, 41:1652,
#                    35:1653, 42:1653,
#                    38:1650, 45:1650,
#                    39:1651, 46:1651}

###############################################################################

TRADE_FRONT_URL = 'tcp://match01.citex.io:20050'
QUOT_FRONT_URL = 'tcp://quot01.citex.io:20051'

contract_id_dic = {'ethbtc':1,'btcusdt':2,'ethusdt':3,
                   'wtcbtc': 20, 'wtceth': 19, 
                   'omgbtc': 22, 'omgeth': 21,
                   'zilbtc': 24, 'zileth': 23,
                   'icxbtc': 26, 'icxeth': 25}

price_precision_dic = {1:6, 2:2, 3:2,
                       20:7, 19:6,
                       22:6, 21:6,
                       24:8, 23:8,
                       26:7, 25:6}

qty_precision_dic = {1:3, 2:6, 3:5,
                     20:3, 19:3,
                     22:3, 21:3,
                     24:3, 23:3,
                     26:3, 25:3}

qty_size_dic = {1:0.001, 2:0.000001, 3:0.00001,
                20:0.001, 19:0.001,
                22:0.001, 21:0.001,
                24:0.001, 23:0.001,
                26:0.001, 25:0.001}

contract_vs_user = {1:10646, 
                    2:10648, 3:10647,
                    20:10641, 19:10641,
                    22:10634, 21:10634,
                    24:10632, 23:10632,
                    26:10635, 25:10635}

###############################################################################

class Quot:
    #定义基本属性
    def __init__(self):
        self.contract_id = 0
        self.market_id = ''
        self.symbol = ''
        self.last_price = 0.0
        self.last_qty = 0.0
        self.bid_price = []
        self.bid_qty = []
        self.ask_price = []
        self.ask_qty = []
        self.volume = 0.0
        self.turnover = 0.0

    def to_string(self):
        quot_time = str(time.strftime('%Y%m%d %H:%M:%S'))
        quot_str = quot_time + ',' + self.market_id + ',' + self.symbol + ',' + str(self.last_price)
        arr_len = min(len(self.bid_price), len(self.ask_price), MAX_LEVEL_NUM)
        if arr_len < MAX_LEVEL_NUM:
            return ''
        for i in range(0, arr_len):
            quot_str = quot_str + ',' + str(self.bid_price[i]) + ',' + str(self.bid_qty[i]) + ',' + \
                str(self.ask_price[i]) + ',' + str(self.ask_qty[i])
        quot_str = quot_str + ',' + str(self.volume) + ',' + str(self.turnover)
        return quot_str

    def get_change(self, quot):
        change = {}
        if self.last_price != quot.last_price:
            change[1] = 0
        bid_levels = []
        ask_levels = []
#        arr_len = min(len(self.bid_price), len(self.ask_price), len(quot.bid_price), len(quot.ask_price), MAX_LEVEL_NUM)
#        for i in range(0, arr_len):
#            if self.bid_price[i] != quot.bid_price[i] or self.bid_qty[i] != quot.bid_qty[i]:
#                bid_levels.append(i)
#            if self.ask_price[i] != quot.ask_price[i] or self.ask_qty[i] != quot.ask_qty[i]:
#                ask_levels.append(i)
        arr_len = 0
        if arr_len == 0:
            arr_len = min(len(self.bid_price), len(self.ask_price), MAX_LEVEL_NUM)
            for i in range(0, arr_len):
                bid_levels.append(i)
                ask_levels.append(i)
        if len(bid_levels) > 0:
            change[2] = bid_levels
        if len(ask_levels) > 0:
            change[3] = ask_levels
        return change

    def to_json(self):
        py2json = {}
        py2json['type'] = 'quot'
        py2json['security'] = self.symbol
        py2json['date'] = get_day()
        py2json['time'] = str(time.strftime('%H:%M:%S.000'))
        py2json['price'] = float(self.last_price)
        py2json['match_qty'] = float(self.volume)
        py2json['turnover'] = float(self.turnover)
        py2json['buy_price'] = [float(x) for x in self.bid_price[0:min(MAX_LEVEL_NUM, len(self.bid_price))]]
        py2json['buy_qty'] = [float(x) for x in self.bid_qty[0:min(MAX_LEVEL_NUM, len(self.bid_qty))]]
        py2json['sell_price'] =[float(x) for x in self.ask_price[0:min(MAX_LEVEL_NUM, len(self.ask_price))]]
        py2json['sell_qty'] = [float(x) for x in self.ask_qty[0:min(MAX_LEVEL_NUM, len(self.ask_qty))]]
        py2json['market'] = self.market_id
        py2json['interest'] = 0
        py2json['limit_up'] = 0
        py2json['limit_down'] = 0
#        logger.debug(json.dumps(py2json).encode('utf-8'))
        return json.dumps(py2json).encode('utf-8')

class Order:
    #定义基本属性
    def __init__(self, contract_id):
        self.message_type = 1001
        self.contract_id = contract_id
        self.appl_id = 1
        self.account_id = contract_vs_user[contract_id]
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

class BinanceQuot:

    #定义基本属性
    def __init__(self):
        self.trade_date = get_day()
        self.quot_book = {}
        self.symbol_curr_time = {}

    def __get_quot(self, symbol):
        if symbol not in self.quot_book:
            quot = Quot()
            quot.market_id = 'binance'
            quot.symbol = symbol
            if symbol in contract_id_dic:
                quot.contract_id = contract_id_dic[symbol]
            self.quot_book[symbol] = quot
        return self.quot_book[symbol]

    def __parse(self, symbol, data):
        quot = self.__get_quot(symbol)
        quot.bid_price.clear()
        quot.bid_qty.clear()
        quot.ask_price.clear()
        quot.ask_qty.clear()
        arr_len = min(len(data['bids']), len(data['asks']), MAX_LEVEL_NUM)
        for i in range(0, arr_len):
            quot.bid_price.append(data['bids'][i][0])
            quot.bid_qty.append(data['bids'][i][1])
            quot.ask_price.append(data['asks'][i][0])
            quot.ask_qty.append(data['asks'][i][1])

        # 发送并保存行情
        if quot.symbol not in self.symbol_curr_time:
            self.symbol_curr_time[quot.symbol] = 0;
        curr_time = self.symbol_curr_time[quot.symbol]
        if (curr_time + 1000) <= int(round(time.time() * 1000)):
            quot_lock.acquire()
            golbal_quot_book[quot.symbol] = quot
#            logger.debug(golbal_quot_book[quot.symbol].to_string())
            quot_lock.release()
            self.symbol_curr_time[quot.symbol] = int(round(time.time() * 1000))

    def __recv_btcusdt(self, data):
        self.__parse('btcusdt', data)

    def __recv_ethusdt(self, data):
        self.__parse('ethusdt', data)

    def __recv_ethbtc(self, data):
        self.__parse('ethbtc', data)

    def __recv_omgbtc(self, data):
        self.__parse('omgbtc', data)
        
    def __recv_omgeth(self, data):
        self.__parse('omgeth', data)

    def __recv_wtcbtc(self, data):
        self.__parse('wtcbtc', data)
        
    def __recv_wtceth(self, data):
        self.__parse('wtceth', data)
        
    def __recv_icxbtc(self, data):
        self.__parse('icxbtc', data)
        
    def __recv_icxeth(self, data):
        self.__parse('icxeth', data)

    def __recv_zilbtc(self, data):
        self.__parse('zilbtc', data)
        
    def __recv_zileth(self, data):
        self.__parse('zileth', data)

    def __recv_tick(self, data):
        for tick in data:
            symbol = str(tick['s']).lower()
            quot = self.__get_quot(symbol)
            if quot.last_price == tick['c']:
                print(symbol, quot.last_price, tick['c'])
            quot.last_price = tick['c']
            if float(tick['v']) - float(quot.volume) > 0.0 and float(quot.volume) > 0.0:
                quot.last_qty = float(tick['v']) - float(quot.volume)
            quot.volume = tick['v']
            quot.turnover = tick['q']

    def run(self):
        client = Client('', '')
        ws = BinanceSocketManager(client)

        ws.start_depth_socket('BTCUSDT', self.__recv_btcusdt, MAX_LEVEL_NUM)
        ws.start_depth_socket('ETHUSDT', self.__recv_ethusdt, MAX_LEVEL_NUM)
        
        ws.start_depth_socket('ETHBTC', self.__recv_ethbtc, MAX_LEVEL_NUM)
        
        ws.start_depth_socket('OMGBTC', self.__recv_omgbtc, MAX_LEVEL_NUM)
        ws.start_depth_socket('OMGETH', self.__recv_omgeth, MAX_LEVEL_NUM)
        
        ws.start_depth_socket('WTCBTC', self.__recv_wtcbtc, MAX_LEVEL_NUM)
        ws.start_depth_socket('WTCETH', self.__recv_wtceth, MAX_LEVEL_NUM)
        
        ws.start_depth_socket('ICXBTC', self.__recv_icxbtc, MAX_LEVEL_NUM)
        ws.start_depth_socket('ICXETH', self.__recv_icxeth, MAX_LEVEL_NUM)
        
        ws.start_depth_socket('ZILBTC', self.__recv_zilbtc, MAX_LEVEL_NUM)
        ws.start_depth_socket('ZILETH', self.__recv_zileth, MAX_LEVEL_NUM)

        ws.start_ticker_socket(self.__recv_tick)
        ws.start()

class HuobiQuot(threading.Thread):

    #定义基本属性
    def __init__(self):
        threading.Thread.__init__(self)
        self.quot_book = {}
        self.symbol_curr_time = {}

    def __get_quot(self, symbol):
        if symbol not in self.quot_book:
            quot = Quot()
            quot.market_id = 'huobi'
            quot.symbol = symbol
            if symbol in contract_id_dic:
                quot.contract_id = contract_id_dic[symbol]
            self.quot_book[symbol] = quot
        return self.quot_book[symbol]

    def run(self):
        while(True):
            try:
                self.quot_book.clear()
                self.symbol_curr_time.clear()
                ws = create_connection("wss://api.huobipro.com/ws")
                ws.send("""{"sub":"market.ethbtc.depth.step0", "id":"ethbtc"}""")
                ws.send("""{"sub":"market.ethbtc.detail", "id":"ethbtcdtl"}""")

                ws.send("""{"sub":"market.ethusdt.depth.step0", "id":"ethusdt"}""")
                ws.send("""{"sub":"market.ethusdt.detail", "id":"ethusdtdtl"}""")

                ws.send("""{"sub":"market.btcusdt.depth.step0", "id":"btcusdt"}""")
                ws.send("""{"sub":"market.btcusdt.detail", "id":"btcusdtdtl"}""")

                ws.send("""{"sub":"market.wtcbtc.depth.step0", "id":"wtcbtc"}""")
                ws.send("""{"sub":"market.wtcbtc.detail", "id":"wtcbtcdtl"}""")

                ws.send("""{"sub":"market.wtceth.depth.step0", "id":"wtceth"}""")
                ws.send("""{"sub":"market.wtceth.detail", "id":"wtcethdtl"}""")

                ws.send("""{"sub":"market.omgbtc.depth.step0", "id":"omgbtc"}""")
                ws.send("""{"sub":"market.omgbtc.detail", "id":"omgbtcdtl"}""")

                ws.send("""{"sub":"market.omgeth.depth.step0", "id":"omgeth"}""")
                ws.send("""{"sub":"market.omgeth.detail", "id":"omgethdtl"}""")
                
                ws.send("""{"sub":"market.zileth.depth.step0", "id":"zileth"}""")
                ws.send("""{"sub":"market.zileth.detail", "id":"zilethdtl"}""")
                
                ws.send("""{"sub":"market.zilbtc.depth.step0", "id":"zilbtc"}""")
                ws.send("""{"sub":"market.zilbtc.detail", "id":"zilbtcdtl"}""")
                
                ws.send("""{"sub":"market.icxeth.depth.step0", "id":"icxeth"}""")
                ws.send("""{"sub":"market.icxeth.detail", "id":"icxethdtl"}""")
                
                ws.send("""{"sub":"market.icxbtc.depth.step0", "id":"icxbtc"}""")
                ws.send("""{"sub":"market.icxbtc.detail", "id":"icxbtcdtl"}""")
                while True:
                    compress_data = ws.recv()
                    json_data = gzip.decompress(compress_data).decode('utf-8')
                    if json_data[:7] == '{"ping"':
                        ts = json_data[8:21]
                        pong = '{"pong":' + ts + '}'
                        ws.send(pong)
                    else:
                        data = json.loads(json_data)
                        if 'ch' in data and 'depth' in data['ch']:
                            print(data)
                            symbol = data['ch'].split('.')[1]
                            quot = self.__get_quot(symbol)
                            arr_len = min(len(data['tick']['bids']), len(data['tick']['asks']), MAX_LEVEL_NUM)
                            quot.bid_price.clear()
                            quot.bid_qty.clear()
                            quot.ask_price.clear()
                            quot.ask_qty.clear()
                            for i in range(0, arr_len):
                                quot.bid_price.append(float(data['tick']['bids'][i][0]))
                                quot.bid_qty.append(float(data['tick']['bids'][i][1]))
                                quot.ask_price.append(float(data['tick']['asks'][i][0]))
                                quot.ask_qty.append(float(data['tick']['asks'][i][1]))

                            # 保存并发送行情
                            if quot.symbol not in self.symbol_curr_time:
                                self.symbol_curr_time[quot.symbol] = 0;
                            curr_time = self.symbol_curr_time[quot.symbol]
                            if (curr_time + 1000) <= int(round(time.time() * 1000)):
                                quot_lock.acquire()
                                golbal_quot_book[quot.symbol] = quot
                                #logger.debug(golbal_quot_book[quot.symbol].to_string())
                                quot_lock.release()
                                self.symbol_curr_time[quot.symbol] = int(round(time.time() * 1000))
                        elif 'ch' in data and 'detail' in data['ch']:
                            symbol = data['ch'].split('.')[1]
                            quot = self.__get_quot(symbol)
                            quot.last_price = float(data['tick']['close'])
                            quot.volume = float(data['tick']['amount'])
                            quot.turnover = float(data['tick']['vol'])
                        else:
                            print(json_data)
            except Exception as e:
                logger.error('huobi ' + str(e))
                time.sleep(5)

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
            if data['message_type'] == 4:
                contract_id = data['contract_id']
                quot = Quot()
                quot.market_id = 'ex'
                quot.contract_id = contract_id
                arr_len = min(len(data['bids']), len(data['asks']), MAX_LEVEL_NUM)
                for i in range(0, arr_len):
                    quot.bid_price.append(to_float(data['bids'][i]['price']))
                    quot.bid_qty.append(to_float(data['bids'][i]['quantity']))
                    quot.ask_price.append(to_float(data['asks'][i]['price']))
                    quot.ask_qty.append(to_float(data['asks'][i]['quantity']))
                exquot_lock.acquire()
                golbal_exquot_book[contract_id] = quot
                exquot_lock.release()

class MarketMaker(threading.Thread):

    #定义基本属性
    def __init__(self):
        threading.Thread.__init__(self)
        self.match_adj_rate = 0.001
        self.level_adj_rate = (0.025, 0.035)

    def __send_order(self, socket, order):
        socket.send(order.to_json())
        ret = socket.recv()
        data = json.loads(ret.decode('utf-8'))
        if 0 != data['code']:
            logger.debug(order.to_json())
            logger.debug(data['msg'])
        else:
            pass

    def __get_last_price(self, exquot, quot):
        last_price = 0.0
        if len(exquot.bid_price) >= 1 and len(exquot.ask_price) >= 1:
            if float(exquot.ask_price[0]) > float(quot.last_price) > float(exquot.bid_price[0]):
                last_price = float(quot.last_price)
            elif float(quot.last_price) >= float(exquot.ask_price[0]):
                last_price = random.uniform(float(exquot.bid_price[0]), float(exquot.ask_price[0] * (1.0 - self.match_adj_rate)))
            elif float(quot.last_price) <= float(exquot.bid_price[0]):
                last_price = random.uniform(float(exquot.bid_price[0] * (1.0 + self.match_adj_rate)), float(exquot.ask_price[0])) 
        else:
            if 0 == len(quot.bid_price) and 0 != len(quot.ask_price):
                if float(quot.last_price) >= float(exquot.ask_price[0]):
                    last_price = random.uniform(float(exquot.bid_price[0]), float(exquot.ask_price[0] * (1.0 - self.match_adj_rate)))
                else:
                    last_price = float(quot.last_price)
            elif 0 != len(quot.bid_price) and 0 == len(quot.ask_price):
                if float(quot.last_price) <= float(exquot.bid_price[0]):
                    last_price = random.uniform(float(exquot.bid_price[0] * (1.0 + self.match_adj_rate)), float(exquot.ask_price[0])) 
                else:
                    last_price = float(quot.last_price)
            else:
                last_price = float(quot.last_price)
        return last_price

    def __get_order_qty(self, i):
        min_qty = 0.01 * (1.0 + 0.0005 * i)
        max_qty = 0.03 * (1.0 + 0.002 * i)
        return round(random.uniform(min_qty, max_qty), 4)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(TRADE_FRONT_URL)

        # 全部撤单
        for user_id in contract_vs_user:
            py2json = {}
            py2json['message_type'] = 1003
            py2json['appl_id'] = 1
            py2json['account_id'] = contract_vs_user[user_id]
            py2json['contract_id'] = 0
            cancel_order = json.dumps(py2json).encode('utf-8')
            socket.send(cancel_order)
            socket.recv()

        pre_quot = {}
        cancel_orders = {}
        while True:
            for symbol in contract_id_dic:
                contract_id = 0
                quot_lock.acquire()
                quot = Quot()
                if symbol in golbal_quot_book:
                    quot = copy.deepcopy(golbal_quot_book[symbol])
                    contract_id = quot.contract_id;
#                    logger.debug(quot.to_string())
                quot_lock.release()

                if symbol not in pre_quot:
                    empty = Quot()
                    pre_quot[symbol] = empty

                # 构造K线
                if contract_id != 0:
                    exquot = Quot()
                    exquot_lock.acquire()
                    if contract_id in golbal_exquot_book:
                        exquot = copy.deepcopy(golbal_exquot_book[contract_id])
                    exquot_lock.release()

                    last_price = self.__get_last_price(exquot, quot)
                    if last_price != 0.0:
                        qty = float(quot.last_qty) * random.uniform(0.001, 0.01)
                        if qty < qty_size_dic[contract_id]:
                            qty = qty_size_dic[contract_id] * random.randint(5, 10)
                        qty = to_decimal(float(qty), qty_precision_dic[contract_id])

                        #买单
                        buy_order = Order(contract_id)
                        buy_order.side = 1
                        buy_order.price = to_decimal(float(last_price), price_precision_dic[contract_id])
                        buy_order.quantity = qty
#                        print(buy_order.to_json())

                        #卖单
                        sell_order = Order(contract_id)
                        sell_order.side = -1
                        sell_order.price = to_decimal(float(last_price), price_precision_dic[contract_id])
                        sell_order.quantity = qty
#                        print(sell_order.to_json())

                        flag = random.randint(1, 4)
                        if flag % 2 == 0:
                            self.__send_order(socket, buy_order)
                            self.__send_order(socket, sell_order)
                        else:
                            self.__send_order(socket, sell_order)
                            self.__send_order(socket, buy_order)

                # 构造价格档位
                change = quot.get_change(pre_quot[symbol])
                pre_quot[symbol] = copy.deepcopy(quot)
                order_list = []
                for key in change:
                    if key == 2:
                        #买单
                        levels = change[2]
                        for i in range(0, len(levels)):
                            order = Order(contract_id)
                            order.side = 1
                            order_price = get_price(quot.bid_price[levels[i]], -1, self.level_adj_rate)
                            order.price = to_decimal(order_price, price_precision_dic[contract_id])
                            order_qty = self.__get_order_qty(i)
                            order.quantity = to_decimal(order_qty, qty_precision_dic[contract_id])
                            order_list.append((order.contract_id, order.to_json()))
                    elif key == 3:
                        #卖单
                        levels = change[3]
                        for i in range(0, len(levels)):
                            order = Order(contract_id)
                            order.side = -1
                            order_price = get_price(quot.ask_price[levels[i]], 1, self.level_adj_rate)
                            order.price = to_decimal(order_price, price_precision_dic[contract_id])
                            order_qty = self.__get_order_qty(i)
                            order.quantity = to_decimal(order_qty, qty_precision_dic[contract_id])
                            order_list.append((order.contract_id, order.to_json()))
                    
                # 报单
                pre_cancel_list = []
                if quot.symbol in cancel_orders:
                    pre_cancel_list = copy.deepcopy(cancel_orders[quot.symbol])
                    cancel_orders[quot.symbol].clear()

                for i in range(0, len(order_list)):
#                    logger.debug(order_list[i][1])
                    socket.send(order_list[i][1])
                    ret = socket.recv()
                    data = json.loads(ret.decode('utf-8'))
#                    logger.debug(data)
                    if 0 == data['code']:
                        if quot.symbol not in cancel_orders:
                            orders = []
                            cancel_orders[quot.symbol] = orders
                        cancel_orders[quot.symbol].append((data['msg'], order_list[i][0]))
                    else:
                        logger.debug('LevelMaker')
                        logger.debug(order_list[i][1])
                        logger.debug(data)

                # 撤掉上一轮报单
                for i in range(0, len(pre_cancel_list)):
                    contract_id = pre_cancel_list[i][1]
                    py2json = {}
                    py2json['message_type'] = 1003
                    py2json['appl_id'] = 1
                    py2json['account_id'] = contract_vs_user[contract_id]
                    py2json['contract_id'] = contract_id
                    py2json['original_order_id'] = pre_cancel_list[i][0]
                    cancel_order = json.dumps(py2json).encode('utf-8')
#                    logger.debug(cancel_order)
                    socket.send(cancel_order)
                    ret = socket.recv()
                    data = json.loads(ret.decode('utf-8'))
#                    if 0 != data['code']:
#                        logger.debug(data)

            wait_sec = random.randint(3, 6)
            time.sleep(wait_sec)

if __name__ == '__main__':
    binance_quot = BinanceQuot()
    binance_quot.run()

#    huobi = HuobiQuot()
#    huobi.start()

    ex_quot = ExchangeQuot()
    ex_quot.start()

    market_maker = MarketMaker()
    market_maker.start()

    while True:
        time.sleep(3600)
