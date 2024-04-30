import settings
from src.networkTokens import wETH_contract
from src.networkTokens import zkSyncEra as network
from src.logger import cs_logger, LogSwap
from src.Helpers.txnHelper import get_txn_dict, exec_txn, check_estimate_gas
from src.Helpers.helper import get_curr_time, delay_sleep, trunc_value, get_random_value
from decimal import Decimal
from random import randint


def get_txn_count(txns_count):
    txn_count = randint(txns_count[0], txns_count[1])  # Рандомим количество транзакций
    return txn_count


def get_open_balance(net, address, balance_percents):
    percent = get_random_value(balance_percents[0], balance_percents[1], 3)
    balance = net.web3.eth.get_balance(address)
    balance_perc = net.web3.from_wei(int(balance * percent), 'ether')
    open_balance = trunc_value(balance_perc, settings.digs_min_eth, settings.digs_max_eth)
    return open_balance


def build_txn_wrap(wallet, value_eth):
    try:
        value_wei = network.web3.to_wei(value_eth, 'ether')
        dict_transaction = get_txn_dict(wallet.address, network, value_wei)

        txn_wrap = wETH_contract.functions.deposit().build_transaction(dict_transaction)
        return txn_wrap
    except Exception as ex:
        cs_logger.info(f'Ошибка в (wrapper: build_txn_wrap) {ex.args}')


def build_txn_unwrap(wallet, value_token):
    try:
        dict_transaction = get_txn_dict(wallet.address, network)
        txn_wrap = wETH_contract.functions.withdraw(
            value_token
        ).build_transaction(dict_transaction)
        return txn_wrap
    except Exception as ex:
        cs_logger.info(f'Ошибка в (wrapper: build_txn_unwrap) {ex.args}')


def wrap_eth(wallet, wrap_value_eth, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = get_curr_time()

        cs_logger.info(f'Свапаем {wrap_value_eth} ETH на wETH')
        balance_start_eth = network.web3.from_wei(network.web3.eth.get_balance(address), 'ether')
        balance_start_token = wETH_contract.functions.balanceOf(address).call() / 10 ** 18

        txn_wrap = build_txn_wrap(wallet, wrap_value_eth)
        estimate_gas = check_estimate_gas(txn_wrap, network)
        if type(estimate_gas) is str:
            cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn_wrap['gas'] = estimate_gas
            txn_hash, txn_status = exec_txn(key, network, txn_wrap)
            cs_logger.info(f'Hash: {txn_hash}')
            delay_sleep(settings.min_delay, settings.max_delay)

            balance_end_eth = network.web3.from_wei(network.web3.eth.get_balance(address), 'ether')
            balance_end_token = wETH_contract.functions.balanceOf(address).call() / 10 ** 18

            wallet.swap_sum += wrap_value_eth
            log = LogSwap(wallet.wallet_num, wallet.operation, txn_num + 1, address, 'Wrap ETH',
                          wrap_value_eth, txn_hash,
                          balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
            log.write_log(settings.log_file, 1, script_time)
            return True
    except Exception as ex:
        cs_logger.info(f'Ошибка в (wrapper: wrap_eth), {ex.args}')
        return False


def unwrap_eth(wallet, token_value_wei, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = get_curr_time()
        balance_start_eth = network.web3.from_wei(network.web3.eth.get_balance(address), 'ether')
        balance_start_token = token_value_wei / 10 ** 18
        cs_logger.info(f'Свапаем {balance_start_token} wETH на ETH')

        txn_unwrap = build_txn_unwrap(wallet, token_value_wei)
        estimate_gas = check_estimate_gas(txn_unwrap, network)
        if type(estimate_gas) is str:
            cs_logger.info(f'{estimate_gas}')
            return False
        else:
            txn_unwrap['gas'] = estimate_gas
            txn_hash, txn_status = exec_txn(key, network, txn_unwrap)
            cs_logger.info(f'Hash: {txn_hash}')
            delay_sleep(settings.min_delay, settings.max_delay)

            balance_end_eth = network.web3.from_wei(network.web3.eth.get_balance(address), 'ether')
            balance_end_token = wETH_contract.functions.balanceOf(address).call() / 10 ** 18

            wallet.swap_sum += balance_start_token
            log = LogSwap(wallet.wallet_num, wallet.operation, txn_num + 1, address, 'Unwrap ETH',
                          balance_start_token, txn_hash,
                          balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
            log.write_log(settings.log_file, 2, script_time)
            return True
    except Exception as ex:
        cs_logger.info(f'Ошибка в (wrapper: unwrap_eth), {ex.args}')
        return False


def wrapping(wallet, module):
    txns = 0
    wrap_balance_eth = get_open_balance(network, wallet.address, settings.wrap_balance_percent)
    txn_count = get_txn_count(module.txns_count)
    for i in range(txn_count):
        if i % 2 == 0:

            wrap_value_eth = trunc_value(
                Decimal(wrap_balance_eth) * Decimal(get_random_value(0.80, 0.98, 3)),
                settings.digs_min_eth, settings.digs_max_eth
            )

            cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            status = wrap_eth(wallet, wrap_value_eth, txns)
            if status is not True:
                break
            txns += 1

        if i % 2 != 0:

            cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            weth_balance = wETH_contract.functions.balanceOf(wallet.address).call()
            if weth_balance == 0:
                cs_logger.info(f'Баланс wETH равен 0')
                break
            status = unwrap_eth(wallet, weth_balance, txns)
            if status is not True:
                break
            txns += 1

    weth_balance = wETH_contract.functions.balanceOf(wallet.address).call()
    if weth_balance != 0:
        cs_logger.info(f'Свапаем оставшийся wETH на эфир')
        unwrap_eth(wallet, weth_balance, txns)
        txns += 1

    wallet.txn_num += txns
    return txns
