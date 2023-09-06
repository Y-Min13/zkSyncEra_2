import src.networkTokens as nt
import src.networkBridge as nb
import src.logger as logger
import settings as stgs
import src.swapper as swapper
import random
import src.gasPriceChecker as gpc
from threading import Thread
import src.helper as helper
import src.orbiterBridge as orbiterBridge
import datetime
import src.syncBridge as syncBridge
import src.userHelper as userHelper
import src.okxOperations as okxOp


# Параметры скрипта:
wallets = stgs.wallets
log_file = stgs.log_file

wallet_list = list()
networks = nb.networks
net_to = helper.choice_net(networks, stgs.net_to_code)
logger.create_xml(log_file)
stgs.last_row = logger.get_last_row_overall(log_file)

connection1 = nt.zkSyncEra.web3.is_connected()

swap_mode_step1 = stgs.swap_mode_step1
swap_mode_step2 = stgs.swap_mode_step2
swap_mode_step3 = stgs.swap_mode_step3
swap_mode_step4 = stgs.swap_mode_step4


def main():
    logger.cs_logger.info(f'Найдено кошельков: {len(wallet_list)}. Статус соединения с RPC: {connection1}')
    if connection1 is False or len(wallet_list) == 0:
        logger.cs_logger.info(f'RPC соединение не удалось или не найдены кошельки!')
    else:
        operation = logger.get_last_row_sm(stgs.log_file)
        op = 1

        if stgs.wallet_mode == 2:
            random.shuffle(wallet_list)

        for wallet in wallet_list:
            result = True
            net_from = helper.choice_net(networks, random.choice(stgs.net_from_code))
            connection2 = net_from.web3.is_connected()
            if stgs.switch_bm1 == 1:
                result = False

            wallet_num = wallet.wallet_num
            script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
            total_swap = 0
            bridge_value = 0
            bridge_vl = 0

            if stgs.bridge_module == 0:
                bridge_mod = random.randint(1, 2)
            else:
                bridge_mod = stgs.bridge_module

            logger.cs_logger.info(f'')
            logger.cs_logger.info(f'№ {op} ({wallet.wallet_num})  Адрес: {wallet.address}  Биржа: {wallet.exchange_address}')
            balance_st = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')

            # Модуль с бриджем (bm)
            if stgs.switch_bm1 == 1:
                fee = net_from.web3.to_wei(helper.get_fee(net_from, net_to), 'ether')

                logger.cs_logger.info(f'***   Модуль бриджа bm1   ***')
                if connection2 is True:

                    if bridge_mod == 1:

                        if stgs.exc_withdraw == 1:
                            res, rc = okxOp.withdraw(wallet, net_from)
                            logger.cs_logger.info(f'{res}')

                        bridge_vl, result = orbiterBridge.bridge(wallet, fee, net_from, net_to)
                        bridge_value += bridge_vl
                        balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                        logger.write_overall(wallet, wallet_num, bridge_value, total_swap, balance_st, balance_end,
                                             script_time, nonce)

                    if bridge_mod == 2:

                        if stgs.exc_withdraw == 1:
                            res, rc = okxOp.withdraw(wallet, nb.ethereum_network)
                            logger.cs_logger.info(f'{res}')

                        bridge_vl, result = syncBridge.bridge(wallet)
                        bridge_value += bridge_vl
                        balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                        logger.write_overall(wallet, wallet_num, bridge_value, total_swap, balance_st, balance_end,
                                             script_time, nonce)
                else:
                    logger.cs_logger.info(f'Соединение с rpc исходящей сети не удалось')

            if result is True:
                if stgs.switch_bm1 == 0:
                    balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                    nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                    logger.write_overall(wallet, wallet_num, bridge_value, total_swap, balance_st, balance_end,
                                         script_time, nonce)

                modules = stgs.modules
                if stgs.modules_shuffle == 1:
                    random.shuffle(modules)
                m_count = random.randint(stgs.modules_min, stgs.modules_max)
                logger.cs_logger.info(f'Количество модулей: {m_count}')
                for module in modules[:m_count]:
                    # Модуль с несколькими свапалками (sm1)
                    if module.mod == 'sm1':
                        if stgs.switch_sm1 == 1:
                            chance = random.randint(1, 100)
                            if chance <= stgs.sm1_chance:
                                gpc.check_limit()
                                logger.cs_logger.info(f'***   Модуль свапа {module.name}   ***')
                                total_swap += swapper.swap_module(wallet, module, swap_mode_step1, swap_mode_step2,
                                                                  swap_mode_step3, swap_mode_step4)
                                operation += 1

                    # Модуль с одной свапалкой (sm2)
                    if module.mod == 'sm2':
                        if stgs.switch_sm2 == 1:
                            chance = random.randint(1, 100)
                            if chance <= stgs.sm2_chance:
                                gpc.check_limit()
                                logger.cs_logger.info(f'***   Модуль свапа {module.name}   ***')
                                if module.swapper == 0:
                                    swap_mode_sm2 = random.randint(1, 5)
                                else:
                                    swap_mode_sm2 = module.swapper
                                total_swap += swapper.swap_module(wallet, module, swap_mode_sm2, swap_mode_sm2,
                                                                  swap_mode_sm2, swap_mode_sm2)
                                operation += 1
                    balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                    nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                    logger.rewrite_overall(wallet, bridge_value, total_swap, balance_end, nonce)
                    wallet.operation = operation

                if stgs.exc_deposit == 1:
                    bridge_vl = 0
                    net_from = helper.choice_net(networks, random.choice(stgs.net_from_code))
                    fee = net_from.web3.to_wei(helper.get_fee(net_to, net_from), 'ether')

                    # Делаем бридж в Arbitrum или Optimism
                    bridge_vl, result = orbiterBridge.bridge(wallet, fee, net_to, net_from)
                    if result is True:
                        bridge_value += bridge_vl
                        balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)

                        # Трансфер средств на адрес биржи
                        okxOp.deposit(wallet, net_from)
                        logger.rewrite_overall(wallet, bridge_value, total_swap, balance_end, nonce)
                    else:
                        logger.cs_logger.info(f'Бридж не удался')

            op += 1
            helper.delay_sleep(stgs.wallet_delay[0], stgs.wallet_delay[1])
    stgs.stop_flag = True
    logger.cs_logger.info(f'Нажмите Enter для выхода...')
    input()


#'''
if connection1 is False:
    logger.cs_logger.info(f'RPC соединение не удалось!')
else:
    wallet_list = helper.read_wallets()
    userHelper.get_info(wallet_list)
    if stgs.start_flag is True:
        gpc.check_gas_price_ether()
        check_thread = Thread(target=gpc.checking, args=(), daemon=True)
        main_thread = Thread(target=main, args=())
        check_thread.start()
        main_thread.start()
        main_thread.join()
    else:
        logger.cs_logger.info(f'Выход...')
# '''
