import decimal
import settings as stgs
import src.ABIs as ABIs
from web3 import Web3
import random
import src.networkBridge as nB
import src.helper as helper
import src.bridger as bridger
import src.logger as logger
import src.txnHelper as txnHelper
import datetime


net_eth = ''
bridge_contract_address = ''
mode = stgs.network_mode
if mode == 1:
    bridge_contract_address = '0x32400084C286CF3E17e7B677ea9583e60a000324'
    web3 = nB.ethereum_network.web3
    net_eth = nB.ethereum_network
    net_zks = nB.zkSyncEra_network

contract = net_eth.web3.eth.contract(Web3.to_checksum_address(bridge_contract_address), abi=ABIs.SyncBridge_ABI)

logs = list()
log_file = stgs.log_file


def get_tax():
    l2_value = contract.functions.l2TransactionBaseCost(
        net_eth.web3.eth.gas_price,
        762908, 800
    ).call()

    tax_mult = random.uniform(stgs.taxMin, stgs.taxMax)
    tax = int(l2_value * tax_mult)
    return tax


def build_txn(wallet, value, tax, gas_price, gas=210000):  # Value в WEI
    address = wallet.address

    # value_wei = net_eth.web3.to_wei(value, 'ether')
    nonce = net_eth.web3.eth.get_transaction_count(wallet.address)
    dict_transaction = {
      'value': value + tax,
      'chainId': net_eth.web3.eth.chain_id,
      'from': address,
      'gas': gas,
      'maxFeePerGas': gas_price,
      'maxPriorityFeePerGas': net_eth.web3.eth.max_priority_fee,
      'nonce': nonce,
    }

    # Транзакция для проверки
    txn = contract.functions.requestL2Transaction(
      address, value, b'', 1000000, 800, [], address,
    ).build_transaction(dict_transaction)
    return txn


def bridge(wallet):
    try:
        helper.wait_bridge_gp(nB.ethereum_network)
        result = False
        txn_status = False
        flag = True
        txn_hash = ''
        address = wallet.address
        script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
        logger.cs_logger.info(f'Sync Бридж из Ethereum в zkSyncEra')
        balance_start_eth = bridger.check_balance(net_eth, address)
        balance_start_zks = bridger.check_balance(net_zks, address)
        bridge_value = net_eth.web3.to_wei(0.0000001, 'ether')

        gp_mult = helper.get_random_value(stgs.random_mult_min, stgs.random_mult_max, 2)
        tax = get_tax()
        gas_price = int(net_eth.web3.eth.gas_price * gp_mult)
        txn = build_txn(wallet, bridge_value, tax, gas_price)
        estimate_gas = txnHelper.check_estimate_gas(txn, net_eth)
        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')

        else:
            if stgs.work_mode_bridge == 1:
                bridge_value = helper.get_open_balance_bridge(address, stgs.balance_percent_bridge_min,
                                                              stgs.balance_percent_bridge_max, net_eth)
                bridge_value_wei = net_eth.web3.to_wei(bridge_value, 'ether')
                txn = build_txn(wallet, bridge_value_wei, tax, gas_price)
                logger.cs_logger.info(f'Делаем бридж {bridge_value} ETH')
            if stgs.work_mode_bridge == 2:
                remains = helper.get_random_value(stgs.exc_remains[0], stgs.exc_remains[1],
                                                  stgs.rem_digs)
                estimate_gas = 210000
                bridge_value = (net_eth.web3.from_wei(balance_start_eth - (estimate_gas * gas_price) - tax, 'ether') -
                                decimal.Decimal(remains))
                bridge_value_wei = net_eth.web3.to_wei(bridge_value, 'ether')
                txn = build_txn(wallet, bridge_value_wei, tax, gas_price)
                logger.cs_logger.info(f'Делаем бридж {bridge_value} ETH')
            est_gas = txnHelper.check_estimate_gas(txn, net_eth)
            if type(est_gas) is str:
                logger.cs_logger.info(f'{est_gas}')
                flag = False
            if flag is True:
                txn_hash, txn_status = txnHelper.exec_txn(wallet.key, net_eth, txn)
                logger.cs_logger.info(f'Hash бриджа: {txn_hash}')
                balance_end_eth = net_zks.web3.from_wei(bridger.check_balance(net_eth, address), 'ether')
                balance_end_zks = net_zks.web3.from_wei(bridger.check_balance(net_zks, address), 'ether')
                log = logger.LogBridge(wallet.wallet_num, net_eth.name, net_zks.name, address, bridge_value, txn_hash,
                                       net_zks.web3.from_wei(balance_start_eth, 'ether'),
                                       net_zks.web3.from_wei(balance_start_zks, 'ether'),
                                       balance_end_eth, balance_end_zks)
                log.write_log(log_file, script_time)
                logs.append(log)
                helper.delay_sleep(stgs.min_delay, stgs.max_delay)

                balance_end_zks_new = bridger.check_balance(net_zks, address)
                if balance_end_zks_new != balance_start_zks:
                    balance_end_eth_new = bridger.check_balance(net_eth, address)
                    log.balance_from_end = net_eth.web3.from_wei(balance_end_eth_new, 'ether')
                    log.balance_to_end = net_zks.web3.from_wei(balance_end_zks_new, 'ether')
                    log.rewrite_log(log_file)

        if txn_status is True and flag is True:
            result = True
            wallet.txn_num += 1
            logger.cs_logger.info(f'Ждем окончания бриджа в сети назначения...')
        for log in logs:
            log.balance_from_end = net_eth.web3.from_wei(bridger.check_balance(net_eth, log.address), 'ether')
            balance_old = net_zks.web3.to_wei(log.balance_to_st, 'ether')
            log.balance_to_end = net_zks.web3.from_wei(helper.check_balance_change(log.address, balance_old, net_zks, 25 * 60),
                                                       'ether')
            log.rewrite_log(log_file)
        return bridge_value, result
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка: {ex.args}')
        return 0, False
