import settings as stgs
import datetime
import decimal
import src.logger as logger
import src.Modules.Bridges.bridger as bridger
import src.Helpers.helper as helper
import src.Helpers.txnHelper as txnHelper
import src.Exchanges.okxOperations as okxOp


bridge_contract_address = ''
mode = stgs.network_mode
if mode == 1:
    bridge_contract_address = '0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8'
if mode == 2:
    bridge_contract_address = '0xa08606A85bf58AFB7c3d464Fc6cF78A159933DD1'  # Тестовый

# Параметры скрипта

logs = list()
log_file = stgs.log_file


def build_txn(network_from, network_to, address, contract, value, fee):
    nonce = network_from.web3.eth.get_transaction_count(address)
    value_wei = network_from.web3.to_wei(value, 'ether')
    br_value = value_wei + fee + network_to.code
    txn = {
        'chainId': network_from.web3.eth.chain_id,
        'from': address,
        'to': contract,
        'value': br_value,
        'nonce': nonce,
        'gasPrice': network_from.web3.eth.gas_price,
    }
    return txn


#'''
def bridge(wallet, fee, net_from, net_to):
    try:
        txn_status = False
        wl_rem = 0
        optimism_l1_fee = 0
        helper.wait_bridge_gp(net_from)
        txn_hash = ''
        script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
        logger.cs_logger.info(f'Orbiter Бридж из {net_from.name[0]} в {net_to.name[0]}')
        mult = helper.get_random_gas(stgs.random_mult_min, stgs.random_mult_max)
        flag = True
        result = False
        bridge_value = 0.005
        address = wallet.address
        balance_from_st = bridger.check_balance(net_from, address)
        balance_to_st = bridger.check_balance(net_to, address)
        txn = build_txn(net_from, net_to, address, bridge_contract_address, bridge_value, fee)
        txn_gp = net_from.web3.from_wei(txn['gasPrice'], 'ether')
        txn['gasPrice'] = net_from.web3.to_wei(txn_gp * decimal.Decimal(mult), 'ether')
        estimate_gas = txnHelper.check_estimate_gas(txn, net_from)
        if type(estimate_gas) is str:
            logger.cs_logger.info(f'{estimate_gas}')
        else:
            txn['gas'] = estimate_gas
            gas_price = txn['gasPrice']
            txn_cost = (gas_price * estimate_gas) + fee
            if txn_cost > balance_from_st:
                logger.cs_logger.info(f'Не хватает средств: {net_from.web3.from_wei(txn_cost - net_from.web3.to_wei(bridge_value, "ether") - balance_from_st, "ether")}')
            else:
                if stgs.work_mode_bridge == 1:

                    if net_from.name == 'Optimism':
                        optimism_l1_fee = int(okxOp.get_optimism_l1_fee(net_from, b'') *
                                              helper.get_random_value(1.05, 1.10, 2))

                    bridge_value = helper.get_open_balance_bridge(address, stgs.balance_percent_bridge_min,
                                                                  stgs.balance_percent_bridge_max, net_from)
                    bridge_value_wei = ((fee + net_from.web3.to_wei(bridge_value, 'ether')) - int(optimism_l1_fee * 2.1)) // 10 ** 4
                    txn['value'] = (bridge_value_wei * 10 ** 4) + net_to.code
                    logger.cs_logger.info(f'Делаем бридж {bridge_value} ETH')
                if stgs.work_mode_bridge == 2:

                    if net_from.name == 'Optimism':
                        optimism_l1_fee = int(okxOp.get_optimism_l1_fee(net_from, b'') *
                                              helper.get_random_value(1.05, 1.10, 2))

                    remains = helper.get_random_value(stgs.exc_remains[0], stgs.exc_remains[1],
                                                      stgs.rem_digs)

                    if net_to.code != 9014: #Код эры
                        wl_rem = helper.get_random_value(stgs.ob_remains2[0], stgs.ob_remains2[1], stgs.ob_digs2)
                    else:
                        wl_rem = helper.get_random_value(stgs.ob_remains1[0], stgs.ob_remains1[1], stgs.ob_digs1)

                    bridge_value = ((net_from.web3.from_wei(balance_from_st - (estimate_gas * gas_price) - 10000, 'ether')
                                    - net_from.web3.from_wei(int(optimism_l1_fee * 2.1), 'ether'))
                                    - decimal.Decimal(remains) - decimal.Decimal(wl_rem))
                    bridge_value_wei = (net_from.web3.to_wei(bridge_value, 'ether')) // 10 ** 4
                    txn['value'] = bridge_value_wei * 10 ** 4 + net_to.code
                    logger.cs_logger.info(f'Делаем бридж {bridge_value} ETH')
                    est_gas = txnHelper.check_estimate_gas(txn, net_from)
                    if type(est_gas) is str:
                        logger.cs_logger.info(f'{est_gas}')
                        flag = False
                if bridge_value < (net_from.web3.from_wei(fee + 9000 + net_from.web3.to_wei(0.005, "ether"), 'ether')):
                    logger.cs_logger.info(f'Сумма бриджа ниже минимальной величины! {net_from.web3.from_wei(txn["value"], "ether")}')
                    flag = False
                if flag is True:
                    txn_hash, txn_status = txnHelper.exec_txn(wallet.key, net_from, txn)
                    logger.cs_logger.info(f'Hash бриджа: {txn_hash}')
                    balance_from_end = bridger.check_balance(net_from, address)
                    log = logger.LogBridge(
                        wallet.wallet_num,
                        net_from.name,
                        net_to.name,
                        address,
                        bridge_value,
                        txn_hash,
                        net_from.web3.from_wei(balance_from_st, 'ether'),
                        net_from.web3.from_wei(balance_to_st, 'ether'),
                        net_from.web3.from_wei(balance_from_end, 'ether'),
                        net_from.web3.from_wei(balance_to_st, 'ether')
                    )

                    log.write_log(log_file, script_time)
                    if txn_status is True:
                        logger.cs_logger.info(f'Ждем окончания бриджа в сети назначения...')
                        result = True
                        wallet.txn_num += 1
                        balance_to_end = helper.check_balance_change(log.address, balance_to_st, net_to, 300 * 60)
                        log.balance_to_end = net_to.web3.from_wei(balance_to_end, 'ether')
                        log.rewrite_log(log_file)
                    helper.delay_sleep(stgs.min_delay, stgs.max_delay)

        return bridge_value, result

    except Exception as ex:
        logger.cs_logger.info(f'Ошибка: {ex.args}')
        return 0, False
#'''
