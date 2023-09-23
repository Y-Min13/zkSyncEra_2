import random
import math
import time
import datetime
import src.networkTokens as nt
import requests
import settings as stgs
import src.gasPriceChecker as gPC
import src.logger as logger
from web3 import Web3
from src.wallet import Wallet


def get_random_number(number_min, number_max):
    number = random.randint(number_min, number_max)
    return number


def create_param(param_length, symbols):
    param = ''
    for i in range(param_length):
        letter = random.choice(symbols)
        param += letter
    return param


def get_curr_time():
    script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
    return script_time


def get_random_value(min_value, max_value, digs=5):
    random_value = random.uniform(min_value, max_value)
    trunc = math.trunc(random_value * (10 ** digs))  # Округляем до {digs} знаков после запятой
    random_value_tr = trunc / (10 ** digs)
    return random_value_tr


def trunc_value(value, digs_min, digs_max):
    digs = random.randint(digs_min, digs_max)
    trunc = math.trunc(value * (10 ** digs))  # Округляем до {digs} знаков после запятой
    value_tr = trunc / (10 ** digs)
    return value_tr


def delay_sleep(min_delay, max_delay):
    delay = random.randint(min_delay, max_delay)
    logger.cs_logger.info(f'Делаем перерыв в {delay} сек')
    time.sleep(delay)
    return delay


def get_open_balance(address, percent_min, percent_max, net):
    percent = get_random_value(percent_min, percent_max, stgs.percent_digs)
    balance = net.web3.eth.get_balance(address)
    balance_perc = nt.zkSyncEra.web3.from_wei(int(balance * percent), 'ether')
    open_balance = trunc_value(balance_perc, stgs.digs_min_eth, stgs.digs_max_eth)
    return open_balance


def get_open_balance_bridge(address, percent_min, percent_max, net):
    percent = get_random_value(percent_min, percent_max, stgs.percent_digs)
    balance = net.web3.eth.get_balance(address)
    balance_perc = net.web3.from_wei(int(balance * percent), 'ether')
    open_balance = trunc_value(balance_perc, stgs.digs_bridge_min, stgs.digs_bridge_max)
    return open_balance


def get_price(token_name):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={token_name}&tsyms=USD&api_key=c8a5e2ad37b494efbbd89af2f4edb232353d228e93406615a36b273c0fccd4f2'
    response = requests.get(url)
    try:
        result = [response.json()]
        price = result[0]['USD']
    except Exception as error:
        logger.cs_logger.info(f'{error.args}')
        price = 1800
    return price


def choice_net(networks, code):
    for net in networks:
        if net.code == code:
            network = net
            return network


def check_balance_change(address, balance, net_to, timeout, period=30):
    end_time = time.time() + timeout
    while time.time() < end_time:
        new_balance = net_to.web3.eth.get_balance(address)
        if balance == new_balance:
            time.sleep(period)
        else:
            return new_balance
    return balance


def get_random_gas(min_value, max_value, digs=2):
    random_value = random.uniform(min_value, max_value)
    trunc = math.trunc(random_value * (10 ** digs))
    gas_mult = trunc / (10 ** digs)
    return gas_mult


def get_fee(net_from, net_to):
    for bridge_fee in net_to.fees:
        if net_from.code == bridge_fee.net_from_code:
            fee = bridge_fee.fee_sum
            return fee


def check_bridge_gp(net_from):
    gp_wei = net_from.web3.eth.gas_price
    gp_gwei = net_from.web3.from_wei(gp_wei, 'gWei')
    return gp_gwei


def wait_bridge_gp(net_from):
    gas_price = check_bridge_gp(net_from)
    i = 0
    while gas_price > stgs.gas_price_limit_bridge:
        gPC.wait_anim('|', gas_price)
        time.sleep(0.4)
        gPC.wait_anim('/', gas_price)
        time.sleep(0.4)
        gPC.wait_anim('--', gas_price)
        time.sleep(0.4)
        gPC.wait_anim('\ ', gas_price)
        time.sleep(0.4)
        i += 1.6
        if i >= 60:
            i = 0
            gas_price = check_bridge_gp(net_from)


def read_wallets():
    wallet_list = list()
    wallet_info = stgs.wallets.read().splitlines()
    index = 1
    w3 = Web3()
    for wl in wallet_info:
        num = wl.split(', ')[0]
        wallet_num = int(num)
        key = wl.split(', ')[1]
        address = w3.eth.account.from_key(key).address
        exchange = wl.split(', ')[2]
        exc_address = Web3.to_checksum_address(exchange)
        wlt = Wallet(wallet_num, key, address, exc_address, index)
        index += 1
        wallet_list.append(wlt)
    return wallet_list
