import src.exchange as exc
import src.logger as logger
import settings
import src.helper as helper
import src.txnHelper as txnHelper
import src.ABIs as ABIs
import random


Optimism_gas_oracle_address = '0x420000000000000000000000000000000000000F'


def get_optimism_l1_fee(net, txn_data):
    oracle = net.web3.eth.contract(Optimism_gas_oracle_address, abi=ABIs.Optimism_gas_oracle_ABI)
    l1_fee = oracle.functions.getL1Fee(txn_data).call()
    return l1_fee


def build_transfer_txn(wallet, net, value, gas, gas_price):
    try:
        nonce = net.web3.eth.get_transaction_count(wallet.address)

        txn = {
            'chainId': net.web3.eth.chain_id,
            'from': wallet.address,
            'to': wallet.exchange_address,
            'value': value,
            'gas': gas,
            'nonce': nonce,
            'gasPrice': gas_price
        }

        return txn
    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (build_transfer_txn): {ex}')


def withdraw(wallet, net):
    wd_value = 0
    balance_st = net.web3.eth.get_balance(wallet.address)

    exc_balance, res = exc.get_balance_master()
    wallet.exc_bal_st = float(exc_balance)

    logger.cs_logger.info(f'Вывод средств с биржи')

    chain_info, res = exc.get_chain_info(net)
    if int(res) > 0:
        return f'Ошибка при выводе средств {res}', chain_info

    if settings.exc_mode == 1:
        wd_value = float(exc_balance) * helper.get_random_value(settings.exc_percent[0], settings.exc_percent[1], 2)
        wd_value = helper.trunc_value(wd_value, settings.exc_digs_min, settings.exc_digs_max)
    if settings.exc_mode == 2:
        wd_value = float(exc_balance)
    wd_result, res = exc.withdraw_on_chain(wallet, wd_value, chain_info)
    if int(res) > 0:
        return f'Ошибка при выводе средств {res}', wd_result

    logger.cs_logger.info(f'Ожидаем поступление средств на кошелек')
    balance_old = helper.check_balance_change(wallet.address, balance_st, net, 60*30)
    if balance_old == balance_st:
        return f'Период ожидания поступления средств истек', ''


def deposit(wallet, net):
    trying = True
    tr_mult = 1
    logger.cs_logger.info('Выполняем перевод средств на биржу')
    while trying is True:
        gas = random.randint(net.transfer[0], net.transfer[1])
        gp_mult = helper.get_random_value(settings.random_mult_min, settings.random_mult_max, 2)
        gas_price = int(net.web3.eth.gas_price * gp_mult)

        balance = net.web3.eth.get_balance(wallet.address)
        remains = helper.get_random_value(settings.exc_remains[0], settings.exc_remains[1], settings.rem_digs)
        remains_wei = int(net.web3.to_wei(remains, 'ether') * tr_mult)
        open_balance = (balance - (gas_price * gas)) - remains_wei

        if net.name == 'Optimism':
            optimism_l1_fee = int(get_optimism_l1_fee(net, b'') *
                                  helper.get_random_value(1.05, 1.10, 2))
            open_balance = open_balance - int(optimism_l1_fee * 2.1)

        transfer_value = open_balance
        txn_transfer = build_transfer_txn(wallet, net, transfer_value, gas, gas_price)
        test = txnHelper.check_estimate_gas(txn_transfer, net)
        if type(test) is str:
            logger.cs_logger.info(f'{test}')
            tr_mult += 0.2
            logger.cs_logger.info('Еще одна попытка перевода средств на биржу')
        else:
            txn_tr_hash, txn_status = txnHelper.exec_txn(wallet.key, net, txn_transfer)
            if txn_status is False:
                tr_mult += 0.2
                logger.cs_logger.info('Еще одна попытка перевода средств на биржу')
            else:
                trying = False
            logger.cs_logger.info(f'Hash перевода на адрес биржи: {txn_tr_hash}')
            logger.cs_logger.info('Ожидаем поступление средств на субаккаунт')

    exc_balance_new = exc.wait_deposit()
    wallet.exc_bal_end = float(exc_balance_new)
