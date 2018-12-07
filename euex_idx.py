# -*- coding: utf-8 -*-

#import json
#import time
#from utils.logger import logger
#from binance.client import Client
#from binance.websockets import BinanceSocketManager
#from utils.tool_util import get_day, to_decimal
#import zmq
#import threading
#import copy
#
#MAX_LEVEL_NUM = 10 # 10档
#SEND_QUOT_FREQ = 5000 # 5秒
#TRADE_SERVER_URL = 'tcp://xmu-centos7:20050'
#
#variety_vs_symbol = {1:'btcusdt'}
#price_precision = {1:2}
#
#class Quot:
#
#    #定义基本属性
#    def __init__(self):
#        self.market_id = ''
#        self.symbol = ''
#        self.last_price = 0.0
#        self.bid_price = []
#        self.bid_qty = []
#        self.ask_price = []
#        self.ask_qty = []
#        self.volume = 0.0
#        self.turnover = 0.0
#
#    def to_json(self):
#        py2json = {}
#        py2json['type'] = 'quot'
#        py2json['security'] = self.symbol
#        py2json['date'] = get_day()
#        py2json['time'] = str(time.strftime('%H:%M:%S.000'))
#        py2json['price'] = float(self.last_price)
#        py2json['match_qty'] = float(self.volume)
#        py2json['turnover'] = float(self.turnover)
#        py2json['buy_price'] = [float(x) for x in self.bid_price[0:min(MAX_LEVEL_NUM, len(self.bid_price))]]
#        py2json['buy_qty'] = [float(x) for x in self.bid_qty[0:min(MAX_LEVEL_NUM, len(self.bid_qty))]]
#        py2json['sell_price'] =[float(x) for x in self.ask_price[0:min(MAX_LEVEL_NUM, len(self.ask_price))]]
#        py2json['sell_qty'] = [float(x) for x in self.ask_qty[0:min(MAX_LEVEL_NUM, len(self.ask_qty))]]
#        py2json['market'] = self.market_id
#        py2json['interest'] = 0
#        py2json['limit_up'] = 0
#        py2json['limit_down'] = 0
##        logger.debug(json.dumps(py2json).encode('utf-8'))
#        return json.dumps(py2json).encode('utf-8')
#
#class BinanceQuot:
#
#    #定义基本属性
#    def __init__(self):
#        self.trade_date = get_day()
#        self.quot_book = {}
#        self.next_send_time = {}
#        self.lock = threading.Lock()
#        self.quot_book = {}
#
#    def get_quot(self, symbol):
#        quot = Quot()
#        self.lock.acquire()
#        if symbol in self.quot_book:
#            quot = copy.deepcopy(self.quot_book[symbol])
#            self.lock.release()
#            return (True, quot)
#        self.lock.release()
#        return (False, quot)
#
#    def __get_quot(self, symbol):
#        if symbol not in self.quot_book:
#            quot = Quot()
#            quot.market_id = 'binance'
#            quot.symbol = symbol
#            self.quot_book[symbol] = quot
#        return self.quot_book[symbol]
#
#    def __parse(self, symbol, data):
#        quot = self.__get_quot(symbol)
#        quot.bid_price.clear()
#        quot.bid_qty.clear()
#        quot.ask_price.clear()
#        quot.ask_qty.clear()
#        arr_len = min(len(data['bids']), len(data['asks']), MAX_LEVEL_NUM)
#        for i in range(0, arr_len):
#            quot.bid_price.append(data['bids'][i][0])
#            quot.bid_qty.append(data['bids'][i][1])
#            quot.ask_price.append(data['asks'][i][0])
#            quot.ask_qty.append(data['asks'][i][1])
#
#        # 发送并保存行情
#        if quot.symbol not in self.next_send_time:
#            self.next_send_time[quot.symbol] = 0;
#        if self.next_send_time[quot.symbol] <= time.time():
#             self.symbol_curr_time[quot.symbol] = time.time() + SEND_QUOT_FREQ
#             self.lock.acquire()
#             self.quot_book[quot.symbol] = quot
#             self.lock.release()
#
#    def __recv_btcusdt(self, data):
#        self.__parse('btcusdt', data)
#
#    def __recv_ethusdt(self, data):
#        self.__parse('ethusdt', data)
#
#    def __recv_eosusdt(self, data):
#        self.__parse('eosusdt', data)
#
#    def __recv_neousdt(self, data):
#        self.__parse('neousdt', data)
#
#    def __recv_etcusdt(self, data):
#        self.__parse('etcusdt', data)
#
#    def __recv_bccusdt(self, data):
#        self.__parse('bccusdt', data)
#
#    def __recv_ltcusdt(self, data):
#        self.__parse('ltcusdt', data)
#
#    def __recv_ethbtc(self, data):
#        self.__parse('ethbtc', data)
#
#    def __recv_eosbtc(self, data):
#        self.__parse('eosbtc', data)
#
#    def __recv_neobtc(self, data):
#        self.__parse('neobtc', data)
#
#    def __recv_etcbtc(self, data):
#        self.__parse('etcbtc', data)
#
#    def __recv_bccbtc(self, data):
#        self.__parse('bccbtc', data)
#
#    def __recv_ltcbtc(self,data):
#        self.__parse('ltcbtc', data)
#
#    def __recv_eoseth(self, data):
#        self.__parse('eoseth', data)
#
#    def __recv_neoeth(self, data):
#        self.__parse('neoeth', data)
#
#    def __recv_etceth(self, data):
#        self.__parse('etceth', data)
#
#    def __recv_bcceth(self, data):
#        self.__parse('bcceth', data)
#
#    def __recv_ltceth(self, data):
#        self.__parse('ltceth', data)
#
#    def __recv_tick(self, data):
#        for tick in data:
#            symbol = str(tick['s']).lower()
#            quot = self.__get_quot(symbol)
#            quot.last_price = tick['c']
#            quot.volume = tick['v']
#            quot.turnover = tick['q']
#
#    def run(self):
#        client = Client('', '')
#        ws = BinanceSocketManager(client)
#        ws.start_depth_socket('BTCUSDT', self.__recv_btcusdt, MAX_LEVEL_NUM)
##        ws.start_depth_socket('ETHUSDT', self.__recv_ethusdt, MAX_LEVEL_NUM)
##        ws.start_depth_socket('EOSUSDT', self.__recv_eosusdt, MAX_LEVEL_NUM)
##        ws.start_depth_socket('NEOUSDT', self.__recv_neousdt, MAX_LEVEL_NUM)
##        ws.start_depth_socket('ETCUSDT', self.__recv_etcusdt, MAX_LEVEL_NUM)
##        ws.start_depth_socket('BCCUSDT', self.__recv_bccusdt, MAX_LEVEL_NUM)
##        ws.start_depth_socket('LTCUSDT', self.__recv_ltcusdt, MAX_LEVEL_NUM)
##
##        ws.start_depth_socket('ETHBTC', self.__recv_ethbtc, MAX_LEVEL_NUM)
##        ws.start_depth_socket('EOSBTC', self.__recv_eosbtc, MAX_LEVEL_NUM)
##        ws.start_depth_socket('NEOBTC', self.__recv_neobtc, MAX_LEVEL_NUM)
##        ws.start_depth_socket('ETCBTC', self.__recv_etcbtc, MAX_LEVEL_NUM)
##        ws.start_depth_socket('BCCBTC', self.__recv_bccbtc, MAX_LEVEL_NUM)
##        ws.start_depth_socket('LTCBTC', self.__recv_ltcbtc, MAX_LEVEL_NUM)
##
##        ws.start_depth_socket('EOSETH', self.__recv_eoseth, MAX_LEVEL_NUM)
##        ws.start_depth_socket('NEOETH', self.__recv_neoeth, MAX_LEVEL_NUM)
##        ws.start_depth_socket('ETCETH', self.__recv_etceth, MAX_LEVEL_NUM)
##        ws.start_depth_socket('BCCETH', self.__recv_bcceth, MAX_LEVEL_NUM)
##        ws.start_depth_socket('LTCETH', self.__recv_ltceth, MAX_LEVEL_NUM)
#
#        ws.start_ticker_socket(self.__recv_tick)
#        ws.start()
#
#if __name__ == '__main__':
#    binance = BinanceQuot()
#    binance.run()
#
#    context = zmq.Context()
#    socket = context.socket(zmq.DEALER)
#    socket.connect(TRADE_SERVER_URL)
#
#    while True:
#        for variety_id in variety_vs_symbol:
#            quot = binance.get_quot(variety_id)
#            if quot[0] == True:
#                py2json = {}
#                py2json['message_type'] = 5008
#                py2json['appl_id'] = 2
#                py2json['variety_id'] = variety_id
#                py2json['index_price'] = to_decimal(quot[1].last_price, price_precision[variety_id])
#                py2json['funding_basis'] = '0'
#                str_json = json.dumps(py2json).encode('utf-8')
#                print(str_json)
#                socket.send(str_json)
#                ret = socket.recv()
#                print(ret)
#    while True:
#        time.sleep(3600)

import json
import zmq
from utils.tool_util import to_decimal

TRADE_SERVER_URL = 'tcp://xmu-centos7:20050'
#TRADE_SERVER_URL = 'tcp://118.24.201.203:20060'

variety_vs_symbol = {1:'btcusdt'}
price_precision = {1:2}

if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect(TRADE_SERVER_URL)
    py2json = {}
    py2json['message_type'] = 5008
    py2json['appl_id'] = 2
    py2json['commodity_id'] = 2
    py2json['currency_id'] = 7
    py2json['index_price'] = to_decimal(6400)
#    py2json['index_price'] = to_decimal(5252.4)
#    py2json['index_price'] = to_decimal(5169.1)
#    py2json['index_price'] = to_decimal(5169.1)
#    py2json['index_price'] = to_decimal(6099.2)
#    py2json['index_price'] = to_decimal(5946.2)
#    py2json['index_price'] = to_decimal(7381)
    py2json['funding_basis'] = '0'
    py2json['market_id'] = ''
    str_json = json.dumps(py2json).encode('utf-8')
    print(str_json)
    socket.send(str_json)
    ret = socket.recv()
    print(ret)




