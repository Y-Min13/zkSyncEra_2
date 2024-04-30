import decimal
import datetime
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
mode = stgs.network_mode
if mode == 1:
    swap_contract_address = '0xf8b59f3c3Ab33200ec80a8A58b2aA5F5D2a8944C'
if mode == 2:
    swap_contract_address = '0x4DC9186c6C5F7dd430c7b6D8D513076637902241'  # Тестовый


def build_txn_swap_in(address, value, price):
    try:
        contract = nt.zkSyncEra.web3.eth.contract(nt.zkSyncEra.web3.to_checksum_address(swap_contract_address),
                                                  abi=ABIs.PancakeSwap_ABI)
        slippage = stgs.slippage
        gas_price = nt.zkSyncEra.web3.eth.gas_price
        max_priority = nt.zkSyncEra.web3.to_wei(stgs.max_priority, 'gWei')
        value_wei = nt.zkSyncEra.web3.to_wei(value, 'ether')
        token_out_wei = int(float(value) * price * (10 ** 6))
        min_output = int(token_out_wei * (1 - slippage))
        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(address)
        dict_transaction = {
            'chainId': nt.zkSyncEra.web3.eth.chain_id,
            'from': address,
            'value': value_wei,
            'gas': 650000,
            'maxFeePerGas': gas_price,
            'maxPriorityFeePerGas': max_priority,
            'nonce': nonce,
        }

        deadline = math.ceil(time.time()) + 20 * 60
        usdc_address = nt.USDC_token.address
        weth_address = nt.wETH_token_pancake.address
        fee = 500
        zr = 0

        contract_code = eth_abi.encode(
            ['address', 'address', 'uint24', 'address', 'uint256', 'uint256', 'uint160'],
            [weth_address, usdc_address, fee, address, value_wei, min_output, zr]
        )
        txn_code_hex = '04e45aaf' + contract_code.hex()
        txn_code = bytes.fromhex(txn_code_hex)

        txn_swap = contract.functions.multicall(
            deadline,
            [txn_code]
        ).build_transaction(dict_transaction)

        return txn_swap
    except Exception as ex:
        logger.cs_logger.info(f'{ex.args}')
        return f'Ошибка: {ex.args}'


def build_txn_swap_out(address, value, price):
    try:
        slippage = stgs.slippage
        contract = nt.zkSyncEra.web3.eth.contract(nt.zkSyncEra.web3.to_checksum_address(swap_contract_address),
                                                  abi=ABIs.PancakeSwap_ABI)
        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(address)
        gas_price = nt.zkSyncEra.web3.eth.gas_price
        max_priority = nt.zkSyncEra.web3.to_wei(stgs.max_priority, 'gWei')
        ether_out = value / price / 10 ** 6
        min_output = int(nt.zkSyncEra.web3.to_wei(ether_out * (1 - slippage), 'ether'))
        #min_output = nt.zkSyncEra.web3.to_wei(0.000001, 'ether')  # для  тестика

        dict_transaction = {
            'chainId': nt.zkSyncEra.web3.eth.chain_id,
            'from': address,
            'gas': 650000,
            'maxFeePerGas': gas_price,
            'maxPriorityFeePerGas': max_priority,
            'nonce': nonce,
        }

        deadline = math.ceil(time.time()) + 20 * 60
        usdc_address = nt.USDC_token.address
        weth_address = nt.wETH_token_pancake.address
        fee = 500
        zr = 0

        contract_code = eth_abi.encode(
            ['address', 'address', 'uint24', 'uint24', 'uint256', 'uint256', 'uint160'],
            [usdc_address, weth_address, fee, 2, value, min_output, zr]
        )
        unwrap_code = eth_abi.encode(
            ['uint256', 'address'],
            [min_output, address]
        )
        txn_code_hex = '04e45aaf' + contract_code.hex()
        txn_unwrap_hex = '49404b7c' + unwrap_code.hex()
        txn_code = bytes.fromhex(txn_code_hex)
        txn_unwrap_code = bytes.fromhex(txn_unwrap_hex)

        txn_swap = contract.functions.multicall(
            deadline,
            [txn_code, txn_unwrap_code]
        ).build_transaction(dict_transaction)
        return txn_swap
    except Exception as ex:
        return f'Ошибка: {ex.args}'


def swap_ETH_to_USDC(wallet, swap_value, price, operation, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
        logger.cs_logger.info(f'Свапаем {swap_value} ETH через PancakeSwap')
        balance_start_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
        balance_start_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

        txn_swap = build_txn_swap_in(address, swap_value, price)
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
            log = logger.LogSwap(wallet.wallet_num, operation, txn_num + 1, address, 'PancakeSwap', swap_value, txn_hash,
                                 balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
            log.write_log(stgs.log_file, 1, script_time)
            return 1
    except Exception as ex:
        return ex.args


def swap_USDC_to_ETH(wallet, token_value, price, operation, txn_num):
    try:
        key = wallet.key
        address = wallet.address
        script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
        if token_value != 0:
            logger.cs_logger.info(f'Свапаем {token_value / 10**6} USDC через PancakeSwap')
            balance_start_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
            balance_start_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

            swapHelper.approve_amount(key, address, swap_contract_address)
            txn_swap = build_txn_swap_out(address, token_value, price)
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
                log = logger.LogSwap(wallet.wallet_num, operation, txn_num + 1, address, 'PancakeSwap', token_value / 10 ** 6, txn_hash,
                                     balance_start_eth, balance_end_eth, balance_start_token, balance_end_token)
                log.write_log(stgs.log_file, 2, script_time)
                return 1
        else:
            logger.cs_logger.info(f'Баланс USDC равен 0')
    except Exception as ex:
        return ex.args


def swapping(wallet, swap_balance, price, txn_count, work_mode, operation, txn_num):
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
            st = swap_ETH_to_USDC(wallet, swap_value, price, operation, txns)
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
                st = swap_ETH_to_USDC(wallet, swap_value, price, operation, txns)
                if st != 1:
                    break
                txns += 1

            if i % 2 != 0:
                logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
                token_value = nt.contract_USDC.functions.balanceOf(wallet.address).call()
                st = swap_USDC_to_ETH(wallet, token_value, price, operation, txns)
                if st != 1:
                    break
                txns += 1
    return txns

