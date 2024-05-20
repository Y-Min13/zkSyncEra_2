import random
import eth_abi
from src.gasPriceChecker import check_limit
import settings
from src.Helpers.txnHelper import exec_txn, check_estimate_gas, get_txn_dict
from src.Helpers.helper import get_curr_time, delay_sleep, get_price
from src.networkTokens import zkSyncEra as network
from src.logger import cs_logger, SupplyLog
from src.Modules.Swaps.wrapper import get_open_balance
from src.ABIs import Eralend_ABI, Eralend_Market_ABI


class Eralend:
    contract_address = '0x22D8b71599e14F20a49a397b88c1C878c86F5579'
    market_address = '0xC955d5fa053d88E7338317cc6589635cD5B2cf09'

    def __init__(self):
        self.volume = 0
        self.volume_min = random.randint(settings.eralend_volume[0], settings.eralend_volume[1])

    def build_txn_supply(self, wallet, value_wei):
        try:
            txn_supply = get_txn_dict(wallet.address, network, value_wei)
            txn_supply['to'] = self.contract_address
            txn_supply['data'] = '0x1249c58b'

            return txn_supply
        except Exception as ex:
            cs_logger.info(f'Ошибка в (Supply/eralend: build_txn_supply) {ex.args}')

    def build_txn_enter_markets(self, wallet):
        try:
            txn_enter = get_txn_dict(wallet.address, network)
            txn_enter['to'] = self.market_address
            txn_enter['data'] = '0xc2998238' + eth_abi.encode(['address[]'], [[self.contract_address]]).hex().removeprefix('0x')

            return txn_enter
        except Exception as ex:
            cs_logger.info(f'Ошибка в (Supply/eralend: build_txn_enter_markets) {ex.args}')

    def build_txn_redeem_token(self, wallet, token_value):
        try:
            txn_redeem = get_txn_dict(wallet.address, network)
            txn_redeem['to'] = self.contract_address
            txn_redeem['data'] = '0x852a12e3' + eth_abi.encode(['uint256'], [token_value]).hex().removeprefix('0x')

            return txn_redeem
        except Exception as ex:
            cs_logger.info(f'Ошибка в (Supply/eralend: build_txn_redeem_token) {ex.args}')

    def supply_eth(self, wallet):
        try:
            script_time = get_curr_time()
            supply_value_eth = get_open_balance(network, wallet.address, settings.eralend_balance_percent)
            cs_logger.info(f'Выполняем supply {supply_value_eth} ETH в Eralend')

            contract = network.web3.eth.contract(self.contract_address, abi=Eralend_ABI)
            balance_start_eth = network.web3.from_wei(network.web3.eth.get_balance(wallet.address), 'ether')
            balance_start_token = contract.functions.balanceOf(wallet.address).call() / 10 ** contract.functions.decimals().call()

            supply_value = network.web3.to_wei(supply_value_eth, 'ether')
            txn = self.build_txn_supply(wallet, supply_value)
            estimate_gas = check_estimate_gas(txn, network)
            if type(estimate_gas) is str:
                cs_logger.info(f'{estimate_gas}')
                return False
            else:
                txn['gas'] = estimate_gas
                txn_hash, txn_status = exec_txn(wallet.key, network, txn)
                cs_logger.info(f'Hash: {txn_hash}')
                if txn_status is False:
                    return False
                self.volume += supply_value_eth * get_price('ETH')
                delay_sleep(settings.min_delay, settings.max_delay)

                balance_end_eth = network.web3.from_wei(network.web3.eth.get_balance(wallet.address), 'ether')
                balance_end_token = contract.functions.balanceOf(wallet.address).call() / 10 ** contract.functions.decimals().call()
                wallet.txn_num += 1
                log = SupplyLog(wallet.wallet_num, wallet.txn_num, wallet.address, 'Eralend supply ETH',
                                supply_value_eth, txn_hash,
                                balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
                log.write_log(1, script_time)
                return True
        except Exception as ex:
            cs_logger.info(f'Ошибка в (Supply/eralend: supply_eth), {ex.args}')
            return False

    def enter_markets(self, wallet):
        try:
            cs_logger.info(f'Выполняем enterMarkets в Eralend')
            market_contract = network.web3.eth.contract(self.market_address, abi=Eralend_Market_ABI)
            if market_contract.functions.checkMembership(wallet.address, self.contract_address).call() is True:
                cs_logger.info(f'Для этого кошелька уже выполнялась данная транзакция')
                return True

            txn = self.build_txn_enter_markets(wallet)
            estimate_gas = check_estimate_gas(txn, network)
            if type(estimate_gas) is str:
                cs_logger.info(f'{estimate_gas}')
                return False
            else:
                txn['gas'] = estimate_gas
                txn_hash, txn_status = exec_txn(wallet.key, network, txn)
                cs_logger.info(f'Hash: {txn_hash}')
                if txn_status is False:
                    return False
                delay_sleep(settings.min_delay, settings.max_delay)

                return True
        except Exception as ex:
            cs_logger.info(f'Ошибка в (Supply/eralend: enter_markets), {ex.args}')
            return False

    def redeem_token(self, wallet):
        try:
            script_time = get_curr_time()
            contract = network.web3.eth.contract(self.contract_address, abi=Eralend_ABI)
            redeem_value = contract.functions.balanceOfUnderlying(wallet.address).call()
            redeem_value_eth = network.web3.from_wei(redeem_value, 'ether')
            cs_logger.info(f'Выполняем redeemToken {redeem_value_eth} ETH из Eralend')
            if redeem_value == 0:
                cs_logger.info(f'Средств для вывода: 0')
                return True
            balance_start_eth = network.web3.from_wei(network.web3.eth.get_balance(wallet.address), 'ether')
            balance_start_token = redeem_value_eth

            txn = self.build_txn_redeem_token(wallet, redeem_value)
            estimate_gas = check_estimate_gas(txn, network)
            if type(estimate_gas) is str:
                cs_logger.info(f'{estimate_gas}')
                return False
            else:
                txn['gas'] = estimate_gas
                txn_hash, txn_status = exec_txn(wallet.key, network, txn)
                cs_logger.info(f'Hash: {txn_hash}')
                if txn_status is False:
                    return False
                delay_sleep(settings.min_delay, settings.max_delay)

                balance_end_eth = network.web3.from_wei(network.web3.eth.get_balance(wallet.address), 'ether')
                balance_end_token = contract.functions.balanceOf(wallet.address).call() / 10 ** contract.functions.decimals().call()
                wallet.txn_num += 1
                log = SupplyLog(wallet.wallet_num, wallet.txn_num, wallet.address, 'Eralend redeemToken',
                                redeem_value_eth, txn_hash,
                                balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
                log.write_log(2, script_time)
                return True
        except Exception as ex:
            cs_logger.info(f'Ошибка в (Supply/eralend: redeem_token), {ex.args}')
            return False


def exec_operation(wallet, operation):
    attempt = 1
    txn_status = False
    while txn_status is False:
        if attempt == settings.attempts_num + 1:
            break
        cs_logger.info(f'Попытка № {attempt}')
        check_limit()
        txn_status = operation(wallet)
        attempt += 1
        if txn_status is False:
            delay_sleep(settings.attempt_delay[0], settings.attempt_delay[1])


def supply_ops(wallet):
    eralend = Eralend()
    if settings.eralend_volume_enable == 1:
        cs_logger.info(f'Минимальный объем для модуля Eralend: {eralend.volume_min} USD')
        while eralend.volume < eralend.volume_min:
            first_step = random.randint(1, 2)
            if first_step == 1:
                exec_operation(wallet, eralend.supply_eth)
                exec_operation(wallet, eralend.enter_markets)
            elif first_step == 2:
                exec_operation(wallet, eralend.enter_markets)
                exec_operation(wallet, eralend.supply_eth)
            cs_logger.info(f'Выполненный объем Eralend: {round(eralend.volume, 2)} USD')
            cs_logger.info(f'Задержка перед выводом средств из Eralend')
            delay_sleep(settings.redeem_sleep_time[0], settings.redeem_sleep_time[1])
            exec_operation(wallet, eralend.redeem_token)
    else:
        first_step = random.randint(1, 2)
        if first_step == 1:
            exec_operation(wallet, eralend.supply_eth)
            exec_operation(wallet, eralend.enter_markets)
        elif first_step == 2:
            exec_operation(wallet, eralend.enter_markets)
            exec_operation(wallet, eralend.supply_eth)
        cs_logger.info(f'Задержка перед выводом средств из Eralend')
        delay_sleep(settings.redeem_sleep_time[0], settings.redeem_sleep_time[1])
        exec_operation(wallet, eralend.redeem_token)
