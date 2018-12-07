# -*- coding: utf-8 -*-
"""
Created on Tues Oct 23 8:21:05 2018

@author: Muxin
"""

import time
import pymysql
import sys
import json
import decimal
from utils.logger import logger
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

DB_IP = 'xmu-centos7'
DB_USER_NAME = 'root'
DB_PASSWORD = 'Vv20180405$$'
DB_NAME = 'new_coin_v3'

ACCESS_KEY = 'xEVxDrX9fXQfn4lVxy1K5tUCPANoCf6tc7UyqPzDiduKLU1fAn4nrFyoFYCfa2FF'
SECRET_KEY = 'rjSCiysCmAbbPyQcnWkptJvEDzl1VawR1s7nJn90m6ypedjelQ94mlGERmjrWuR6'

###############################################################################

QUOT_FRONT_URL = 'tcp://quot01.citex.io:20051'

contract_symbol_id = {'ethbtc':1,'btcusdt':2,'ethusdt':3}
contract_id_symbol = {1:'ethbtc', 2:'btcusdt', 3:'ethusdt'}
contract_vs_user = {1:6, 2:6, 3:6}

###############################################################################

class DBDao:

    @staticmethod
    def fetch_data(sql):
        results = []
        db = pymysql.connect(DB_IP, DB_USER_NAME, DB_PASSWORD, DB_NAME)
        cursor = db.cursor()
        try:
           cursor.execute(sql)
           results = cursor.fetchall()
           db.close()
           return results
        except:
            logger.error(str(sys.exc_info()))
            db.close()
            return results

class Order:

    #定义基本属性
    def __init__(self):
        self.contract_id = 0
        self.side = ''
        self.order_type = 'LIMIT'
        self.time_in_force = 'GTC'
        self.quantity = 0.0
        self.price = 0.0
        self.is_complete = False
        self.client_order_id = ''
        self.order_id = ""
        self.err_code = 0
        self.err_msg = ''

    def to_json(self):
        py2json = {}
        py2json['contract_id'] = self.contract_id
        py2json['side'] = self.side
        py2json['price'] = self.price
        py2json['quantity'] = self.quantity
        py2json['order_id'] = self.order_id
        py2json['client_order_id'] = self.client_order_id
        return json.dumps(py2json).encode('utf-8')

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

class BinanceTrade:

    #定义基本属性
    def __init__(self):
        self.binance = Client(ACCESS_KEY, SECRET_KEY)

    def place_order(self, order):
        try:
            data = self.binance.create_order(
                    symbol = order.contract_id,
                    side = order.side,
                    type = order.order_type,
                    timeInForce = order.time_in_force,
                    quantity = order.quantity,
                    price = order.price)
            order.order_id = str(data['orderId'])
            order.client_order_id = data['clientOrderId']
        except (BinanceAPIException, BinanceRequestException) as e:
            order.err_code = 1
            order.err_msg = str(e)
        except:
            order.err_code = 2
            order.err_msg = str(sys.exc_info())
        if order.err_code != 0:
            logger.debug(order.err_msg)

    def cancel_order(self, order):
            pass

    def get_order(self, order):
        data = self.binance.get_order(
                symbol = order.security,
                orderId = order.order_id)
        if float(data['executedQty']) != order.executed_amount:
            pass
        if data['status'] == 'CANCELED':
            pass
        if data['status'] == 'FILLED' or data['status'] == 'CANCELED':
            self.is_complete = True

    def get_account(self):
        data_dic = self.binance.get_account()
        print(data_dic)

if __name__ == '__main__':

#    binance = BinanceTrade()

    while True:
        for key in contract_vs_user:
            contract_id = key
            user_id = contract_vs_user[key]

            buy_sql = 'select ifnull(contract_id, 0), ifnull(sum(match_qty), 0), ifnull(sum(match_price * match_qty), 0), from core_match ' \
                'where bid_user_id = {0} and ask_user_id <> {0} and contract_id = {1}'.format(user_id, contract_id)
            buy_match = DBDao.fetch_data(buy_sql)

            sell_sql = 'select ifnull(contract_id, 0), ifnull(sum(match_qty), 0), ifnull(sum(match_price * match_qty), 0) from core_match ' \
                'where bid_user_id <> {0} and ask_user_id = {0} and contract_id = {1}'.format(user_id, contract_id)
            sell_match = DBDao.fetch_data(sell_sql)
            
            if buy_match[0][0] == 0 and sell_match[0][0] == 0:
                continue
            delta_qty = decimal.Decimal(sell_match[0][1]) - decimal.Decimal(buy_match[0][1])
            if delta_qty > 0:
                order = Order()
                order.contract_id = contract_id_symbol[contract_id].upper()
                order.side = 'BUY'
                order.quantity = str(delta_qty)
                order.price = str(abs(decimal.Decimal(sell_match[0][2]) - decimal.Decimal(buy_match[0][2]))
                    / decimal.Decimal(delta_qty) * decimal.Decimal(1 + 0.0025))
            elif delta_qty < 0:
                order = Order()
                order.contract_id = contract_id_symbol[contract_id].upper()
                order.side = 'SELL'
                order.quantity = str(abs(delta_qty))
                order.price = str(abs(decimal.Decimal(sell_match[0][2]) - decimal.Decimal(buy_match[0][2]))
                    / decimal.Decimal(abs(delta_qty)) * decimal.Decimal(1 - 0.0025))
            logger.debug(order.to_json())
#            binance.place_order(order)
        time.sleep(10)

    while True:
        time.sleep(3600)

