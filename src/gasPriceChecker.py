from web3 import Web3
import settings as stgs
import time

web3 = Web3(Web3.HTTPProvider(stgs.ether_rpc))


def check_gas_price_ether():
    gas_price_now = web3.eth.gas_price
    stgs.gas_price_ether = web3.from_wei(gas_price_now, 'gWei')


def checking():
    while stgs.stop_flag is False:
        check_gas_price_ether()
        time.sleep(60 * 1)


def check_limit():
    if stgs.gas_price_ether > stgs.gas_price_limit:
        while stgs.gas_price_ether > stgs.gas_price_limit:
            wait_anim('|', stgs.gas_price_ether)
            time.sleep(0.4)
            wait_anim('/', stgs.gas_price_ether)
            time.sleep(0.4)
            wait_anim('--', stgs.gas_price_ether)
            time.sleep(0.4)
            wait_anim('\ ', stgs.gas_price_ether)
            time.sleep(0.4)


def wait_anim(symbol, gas_price):
    print(f'\rЖдем, цена газа большая: {gas_price}  {symbol} ', end='')
