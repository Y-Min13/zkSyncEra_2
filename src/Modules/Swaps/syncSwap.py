import decimal
import datetime
from web3 import constants
import time
import math
import src.networkTokens as nt
import src.ABIs as ABIs
import eth_abi
import src.Helpers.txnHelper as swapHelper
import src.Helpers.helper as helper
import src.logger as logger
import settings as stgs


swap_contract_address = ''
poolFactory_address = ''
zero_address = constants.ADDRESS_ZERO
mode = stgs.network_mode
if mode == 1:
    poolFactory_address = '0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb'
    swap_contract_address = '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295'
if mode == 2:
    poolFactory_address = '0xf2FD2bc2fBC12842aAb6FbB8b1159a6a83E72006'  # Тестовый
    swap_contract_address = '0xB3b7fCbb8Db37bC6f572634299A58f51622A847e'  # Тестовый
contract_swap = nt.zkSyncEra.web3.eth.contract(nt.zkSyncEra.web3.to_checksum_address(swap_contract_address), abi=ABIs.SyncSwap_ABI)
contract_poolFactory = nt.zkSyncEra.web3.eth.contract(nt.zkSyncEra.web3.to_checksum_address(poolFactory_address), abi=ABIs.SyncSwap_PoolFactory_ABI)


def get_pool():
    pool_address = contract_poolFactory.functions.getPool(
        nt.wETH_token_sync.address, nt.USDC_token.address
    ).call()
    return pool_address


def build_txn_swap_in(address, value_eth):
    try:
        value = nt.zkSyncEra.web3.to_wei(value_eth, 'ether')
        pool_address = get_pool()
        remove_end = 1
        swap_data = eth_abi.encode(['address', 'address', 'uint8'], [nt.wETH_token_sync.address, address, remove_end])
        steps = [{'pool': pool_address, 'data': swap_data, 'callback': zero_address, 'callbackData': b'0x'}]
        paths = [{'steps': steps, 'tokenIn': zero_address, 'amountIn': value}]

        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(address)
        gas_price = nt.zkSyncEra.web3.eth.gas_price
        max_priority = nt.zkSyncEra.web3.to_wei(0.25, 'gWei')

        dict_transaction = {
            'chainId': nt.zkSyncEra.web3.eth.chain_id,
            'from': address,
            'value': value,
            'gas': 650000,
            'maxFeePerGas': gas_price,
            'maxPriorityFeePerGas': max_priority,
            'nonce': nonce,
        }
        txn_swap = contract_swap.functions.swap(
            paths,
            0,
            math.ceil(time.time()) + 1800
        ).build_transaction(dict_transaction)
        return txn_swap
    except Exception as ex:
        return f'Ошибка: {ex.args}'


def build_txn_swap_out(address, value):
    try:
        pool_address = get_pool()

        remove_end = 1
        swap_data = eth_abi.encode(['address', 'address', 'uint8'], [nt.USDC_token.address, address, remove_end])
        steps = [{'pool': pool_address, 'data': swap_data, 'callback': zero_address, 'callbackData': b'0x'}]
        paths = [{'steps': steps, 'tokenIn': nt.USDC_token.address, 'amountIn': value}]

        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(address)
        gas_price = nt.zkSyncEra.web3.eth.gas_price
        max_priority = nt.zkSyncEra.web3.to_wei(0.25, 'gWei')

        dict_transaction = {
            'chainId': nt.zkSyncEra.web3.eth.chain_id,
            'from': address,
            'gas': 650000,
            'maxFeePerGas': gas_price,
            'maxPriorityFeePerGas': max_priority,
            'nonce': nonce,
        }
        txn_swap = contract_swap.functions.swap(
            paths,
            0,
            math.ceil(time.time()) + 1800
        ).build_transaction(dict_transaction)
        return txn_swap
    except Exception as ex:
        return f'Ошибка: {ex.args}'


def swap_ETH_to_USDC(wallet, swap_value, operation, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
        logger.cs_logger.info(f'Свапаем {swap_value} ETH через SyncSwap')
        balance_start_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
        balance_start_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

        txn_swap = build_txn_swap_in(address, swap_value)
        estimate_gas = swapHelper.check_estimate_gas(txn_swap, nt.zkSyncEra)
        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
            return -1
        else:
            txn_swap['gas'] = estimate_gas
            txn_hash, txn_status = swapHelper.exec_txn(key, nt.zkSyncEra, txn_swap)
            logger.cs_logger.info(f'Hash: {txn_hash}')
            helper.delay_sleep(stgs.min_delay, stgs.max_delay)

            balance_end_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
            balance_end_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6
            log = logger.LogSwap(wallet.wallet_num, operation, txn_num + 1, address, 'SyncSwap', swap_value, txn_hash,
                                 balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
            log.write_log(stgs.log_file, 1, script_time)
            return 1
    except Exception as ex:
        return ex.args


def swap_USDC_to_ETH(wallet, token_value, operation, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
        if token_value != 0:
            logger.cs_logger.info(f'Свапаем {token_value / 10**6} USDC через SyncSwap')
            balance_start_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
            balance_start_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

            swapHelper.approve_amount(key, address, swap_contract_address)
            txn_swap = build_txn_swap_out(address, token_value)
            estimate_gas = swapHelper.check_estimate_gas(txn_swap, nt.zkSyncEra)
            if type(estimate_gas) is str:
                logger.cs_logger.info(f'{estimate_gas}')
                return -1
            else:
                txn_swap['gas'] = estimate_gas
                txn_hash, txn_status = swapHelper.exec_txn(key, nt.zkSyncEra, txn_swap)
                logger.cs_logger.info(f'Hash: {txn_hash}')
                helper.delay_sleep(stgs.min_delay, stgs.max_delay)

                balance_end_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
                balance_end_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6
                log = logger.LogSwap(wallet.wallet_num, operation, txn_num + 1, address, 'SyncSwap',
                                     token_value / 10 ** 6, txn_hash,
                                     balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
                log.write_log(stgs.log_file, 2, script_time)
                return 1
        else:
            logger.cs_logger.info(f'Баланс USDC равен 0')
    except Exception as ex:
        return ex.args


def swapping(wallet, swap_balance, txn_count, work_mode, operation, txn_num):
    txns = txn_num
    dd = txn_count // 10
    if work_mode == 1:
        swap_value_max = swap_balance / txn_count

        for i in range(txn_count):
            if i == txn_count - 1:
                swap_value = helper.trunc_value(swap_balance, stgs.digs_min_eth + 1 + dd, stgs.digs_max_eth + 1 + dd)
            else:
                swap_value = helper.trunc_value(
                    decimal.Decimal(swap_value_max) * decimal.Decimal(helper.get_random_value(0.80, 0.98, 3)),
                    stgs.digs_min_eth + 1 + dd, stgs.digs_max_eth + 1 + dd
                )
                swap_balance -= swap_value

            logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            st = swap_ETH_to_USDC(wallet, swap_value, operation, txns)
            if st != 1:
                break
            txns += 1

    if work_mode == 2:
        swap_value_max = swap_balance

        for i in range(txn_count):

            if i % 2 == 0:
                swap_value = helper.trunc_value(
                    decimal.Decimal(swap_value_max) * decimal.Decimal(helper.get_random_value(0.80, 0.98, 3)),
                    stgs.digs_min_eth + 1 + dd, stgs.digs_max_eth + 1 + dd
                )
                if i == 0:
                    swap_value = helper.trunc_value(swap_balance, stgs.digs_min_eth + 1 + dd, stgs.digs_max_eth + 1 + dd)

                logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
                st = swap_ETH_to_USDC(wallet, swap_value, operation, txns)
                if st != 1:
                    break
                txns += 1

            if i % 2 != 0:
                logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
                token_value = nt.contract_USDC.functions.balanceOf(wallet.address).call()
                st = swap_USDC_to_ETH(wallet, token_value, operation, txns)
                if st != 1:
                    break
                txns += 1
    return txns
