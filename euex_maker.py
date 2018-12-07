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
from utils.tool_util import get_day, to_decimal
import zmq
import threading
import copy
import random

# 全局变量
global golbal_quot_book
golbal_quot_book = {}
quot_lock = threading.Lock()

global max_level_num
max_level_num = 10

#contract_id_dic = {'ethbtc':1, 'eosbtc':2, 'neobtc':3, 'etcbtc':4, 'bchbtc':5, 'ltcbtc':6,
#                   'eoseth':7, 'neoeth':8, 'etceth':9, 'bcheth':10, 'ltceth':11, 'btcusdt':12,
#                   'ethusdt':13, 'eosusdt':14, 'neousdt':15, 'etcusdt':16, 'bccusdt':17, 'ltcusdt':18}
#price_precision_dic = {1:6, 2:6, 3:6, 4:6, 5:6, 6:6, 7:6, 8:6, 9:6,
#                       10:6, 11:6, 12:6, 13:6, 14:6, 15:6, 16:6, 17:6, 18:6}
#qty_precision_dic = {1:3, 2:3, 3:3, 4:3, 5:3, 6:3, 7:3, 8:3, 9:3,
#                     10:3, 11:3, 12:3, 13:3, 14:3, 15:3, 16:3, 17:3, 18:3}

contract_id_dic = {'ethbtc':1,'btcusdt':2,'ethusdt':3}
price_precision_dic = {1:6, 2:2, 3:2}
qty_precision_dic = {1:3, 2:6, 3:5}

class Quot:
    #定义基本属性
    def __init__(self):
        self.market_id = ''
        self.symbol = ''
        self.last_price = 0.0
        self.bid_price = []
        self.bid_qty = []
        self.ask_price = []
        self.ask_qty = []
        self.volume = 0.0
        self.turnover = 0.0

    def to_string(self):
        quot_time = str(time.strftime('%Y%m%d %H:%M:%S'))
        quot_str = quot_time + ',' + self.market_id + ',' + self.symbol + ',' + str(self.last_price)
        arr_len = min(len(self.bid_price), len(self.ask_price), max_level_num)
        if arr_len < max_level_num:
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
#        arr_len = min(len(self.bid_price), len(self.ask_price), len(quot.bid_price), len(quot.ask_price), max_level_num)
#        for i in range(0, arr_len):
#            if self.bid_price[i] != quot.bid_price[i] or self.bid_qty[i] != quot.bid_qty[i]:
#                bid_levels.append(i)
#            if self.ask_price[i] != quot.ask_price[i] or self.ask_qty[i] != quot.ask_qty[i]:
#                ask_levels.append(i)
        arr_len = 0
        if arr_len == 0:
            arr_len = min(len(self.bid_price), len(self.ask_price), max_level_num)
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
        self.account_id = 6
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
            self.quot_book[symbol] = quot
        return self.quot_book[symbol]
    
    def __parse(self, symbol, data):
        quot = self.__get_quot(symbol)
        quot.bid_price.clear()
        quot.bid_qty.clear()
        quot.ask_price.clear()
        quot.ask_qty.clear()
        arr_len = min(len(data['bids']), len(data['asks']), max_level_num)
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
            #logger.debug(golbal_quot_book[quot.symbol].to_string())
            quot_lock.release()
            self.symbol_curr_time[quot.symbol] = int(round(time.time() * 1000))

    def __recv_btcusdt(self, data):
        self.__parse('btcusdt', data)
        
    def __recv_ethusdt(self, data):
        self.__parse('ethusdt', data)
        
    def __recv_eosusdt(self, data):
        self.__parse('eosusdt', data)
        
    def __recv_neousdt(self, data):
        self.__parse('neousdt', data)
        
    def __recv_etcusdt(self, data):
        self.__parse('etcusdt', data)
        
    def __recv_bccusdt(self, data):
        self.__parse('bccusdt', data)

    def __recv_ltcusdt(self, data):
        self.__parse('ltcusdt', data)

    def __recv_ethbtc(self, data):
        self.__parse('ethbtc', data)
    
    def __recv_eosbtc(self, data):
        self.__parse('eosbtc', data)
        
    def __recv_neobtc(self, data):
        self.__parse('neobtc', data)
    
    def __recv_etcbtc(self, data):
        self.__parse('etcbtc', data)
    
    def __recv_bccbtc(self, data):
        self.__parse('bccbtc', data)
        
    def __recv_ltcbtc(self,data):
        self.__parse('ltcbtc', data)
        
    def __recv_eoseth(self, data):
        self.__parse('eoseth', data)
    
    def __recv_neoeth(self, data):
        self.__parse('neoeth', data)
    
    def __recv_etceth(self, data):
        self.__parse('etceth', data)
    
    def __recv_bcceth(self, data):
        self.__parse('bcceth', data)
    
    def __recv_ltceth(self, data):
        self.__parse('ltceth', data)
    
    def __recv_tick(self, data): 
        for tick in data:
            symbol = str(tick['s']).lower()
            quot = self.__get_quot(symbol)
            quot.last_price = tick['c']
            quot.volume = tick['v']
            quot.turnover = tick['q']
    
    def run(self):
        client = Client('', '')
        ws = BinanceSocketManager(client)
        ws.start_depth_socket('BTCUSDT', self.__recv_btcusdt, max_level_num)
        ws.start_depth_socket('ETHUSDT', self.__recv_ethusdt, max_level_num)
        ws.start_depth_socket('EOSUSDT', self.__recv_eosusdt, max_level_num)
        ws.start_depth_socket('NEOUSDT', self.__recv_neousdt, max_level_num)
        ws.start_depth_socket('ETCUSDT', self.__recv_etcusdt, max_level_num)
        ws.start_depth_socket('BCCUSDT', self.__recv_bccusdt, max_level_num)
        ws.start_depth_socket('LTCUSDT', self.__recv_ltcusdt, max_level_num)

        ws.start_depth_socket('ETHBTC', self.__recv_ethbtc, max_level_num)
        ws.start_depth_socket('EOSBTC', self.__recv_eosbtc, max_level_num)
        ws.start_depth_socket('NEOBTC', self.__recv_neobtc, max_level_num)
        ws.start_depth_socket('ETCBTC', self.__recv_etcbtc, max_level_num)
        ws.start_depth_socket('BCCBTC', self.__recv_bccbtc, max_level_num)
        ws.start_depth_socket('LTCBTC', self.__recv_ltcbtc, max_level_num)

        ws.start_depth_socket('EOSETH', self.__recv_eoseth, max_level_num)
        ws.start_depth_socket('NEOETH', self.__recv_neoeth, max_level_num)
        ws.start_depth_socket('ETCETH', self.__recv_etceth, max_level_num)
        ws.start_depth_socket('BCCETH', self.__recv_bcceth, max_level_num)
        ws.start_depth_socket('LTCETH', self.__recv_ltceth, max_level_num)

        ws.start_ticker_socket(self.__recv_tick)
        ws.start()

class MarketMaker(threading.Thread):

    #定义基本属性
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:20050")
        logger.debug('Market Maker is Ready')
        
        pre_quot = {}
        cancel_orders = {}
        while True:
            for symbol in contract_id_dic:                
                quot_lock.acquire() 
                quot = Quot()
                if symbol in golbal_quot_book:
                    quot = copy.deepcopy(golbal_quot_book[symbol])
#                    logger.debug(quot.to_string())
                quot_lock.release()
                
                if symbol not in pre_quot:
                    empty = Quot()
                    pre_quot[symbol] = empty                 
                change = quot.get_change(pre_quot[symbol])
                pre_quot[symbol] = copy.deepcopy(quot)
                order_list = []
                for key in change:
                    #print(key, change[key])
                    contract_id = contract_id_dic[quot.symbol]
                    if key == 1:
                        qty = round(random.uniform(0.01, 0.02), 4)
#                        print(quot.to_string())
    
                        #买单                        
                        buy_order = Order()
                        buy_order.contract_id = contract_id
                        buy_order.side = 1
                        buy_order.price = to_decimal(float(quot.last_price), price_precision_dic[contract_id])
                        buy_order.quantity = to_decimal(qty, qty_precision_dic[contract_id])
                        
                        #卖单
                        sell_order = Order()               
                        sell_order.contract_id = contract_id
                        sell_order.side = -1
                        sell_order.price = to_decimal(float(quot.last_price), price_precision_dic[contract_id])
                        sell_order.quantity = to_decimal(qty, qty_precision_dic[contract_id])
                        
                        flag = random.randint(0, 3)
                        if flag % 2 == 0:
                            order_list.append((contract_id, buy_order.to_json()))
                            order_list.append((contract_id, sell_order.to_json()))
                        else:
                            order_list.append((contract_id, sell_order.to_json()))
                            order_list.append((contract_id, buy_order.to_json()))
                    elif key == 2:
                        #买单
                        levels = change[2]
                        for i in range(0, len(levels)):
                            order = Order()
                            order.contract_id = contract_id
                            order.side = 1
                            order.price = to_decimal(float(quot.bid_price[levels[i]]), price_precision_dic[contract_id])
                            order.quantity = to_decimal(float(quot.bid_qty[levels[i]]), qty_precision_dic[contract_id])
                            #order_list.append((order.contract_id, order.to_json()))
                    elif key == 3:
                        #卖单
                        levels = change[3]
                        for i in range(0, len(levels)):
                            order = Order()
                            order.contract_id = contract_id
                            order.side = -1
                            order.price = to_decimal(float(quot.ask_price[levels[i]]), price_precision_dic[contract_id])
                            order.quantity = to_decimal(float(quot.ask_qty[levels[i]]), qty_precision_dic[contract_id])
                            #order_list.append((order.contract_id, order.to_json()))
                
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
                    if quot.symbol not in cancel_orders:
                        orders = []
                        cancel_orders[quot.symbol] = orders
                    cancel_orders[quot.symbol].append((data['msg'], order_list[i][0]))
                
                # 撤掉上一轮报单
                for i in range(0, len(pre_cancel_list)):
                    py2json = {}
                    py2json['message_type'] = 1003
                    py2json['appl_id'] = 1
                    py2json['account_id'] = 6
                    py2json['contract_id'] = pre_cancel_list[i][1]
                    py2json['original_order_id'] = pre_cancel_list[i][0]
                    cancel_order = json.dumps(py2json).encode('utf-8')
#                    logger.debug(cancel_order)
                    socket.send(cancel_order)
                    socket.recv()
            wait_sec = random.randint(1, 3)
            time.sleep(wait_sec)

if __name__ == '__main__':
    binance = BinanceQuot()
    binance.run()

    maker = MarketMaker()
    maker.start()
    maker.join()
    
    while True:
        time.sleep(3600)