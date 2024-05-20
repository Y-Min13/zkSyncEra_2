import src.networkTokens as nt
import src.Modules.Bridges.networkBridge as nb
import src.logger as logger
import settings as stgs
import src.Modules.Swaps.swapper as swapper
import random
import src.gasPriceChecker as gpc
from threading import Thread
import src.Helpers.helper as helper
import src.Modules.Bridges.orbiterBridge as orbiterBridge
import src.Modules.Bridges.syncBridge as syncBridge
import src.Helpers.userHelper as userHelper
import src.Exchanges.okxOperations as okxOp
import src.Modules.Modules as Mods
import src.Modules.nftMints.tevaEraMint as tevaEraMint
import src.Modules.nftMints.eraNameMint as eraNameMint
import src.Modules.Liquidity.addLiquidity as liquidity
from src.Modules.nftMints.rhinoMint import minting as rhino_mint
from src.Modules.Swaps.wrapper import wrapping
from src.Modules.Supply.eralend import supply_ops


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

            wallet_num = wallet.wallet_num
            script_time = helper.get_curr_time()
            total_swap = 0
            bridge_value = 0
            nft_value = 0
            liq_value = 0

            if stgs.bridge_module == 0:
                bridge_mod = random.randint(1, 2)
            else:
                bridge_mod = stgs.bridge_module

            logger.cs_logger.info(f'\n')
            logger.cs_logger.info(f'№ {op} ({wallet.wallet_num})  Адрес: {wallet.address}  Биржа: {wallet.exchange_address}')
            balance_st = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')

            # Прямой вывод средств с биржи
            if stgs.switch_bm1 == 1:
                result = True
                if stgs.exc_withdraw == 1:
                    rc = 1
                    while int(rc) > 0:
                        res, rc = okxOp.withdraw(wallet, nb.zkSyncEra_network)
                        if int(rc) > 0:
                            logger.cs_logger.info(f'{res}')
                            logger.cs_logger.info(f'Доп попытка вывода')

                balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                logger.write_overall(wallet, wallet_num, bridge_value, total_swap, nft_value, liq_value,
                                     balance_st, balance_end, script_time, nonce)

            # Вывод средств через бридж
            if stgs.switch_bm1 == 2:
                result = False
                fee = net_from.web3.to_wei(helper.get_fee(net_from, net_to), 'ether')
                logger.cs_logger.info(f'')
                logger.cs_logger.info(f'***   Модуль бриджа bm1   ***')
                if connection2 is True:

                    if bridge_mod == 1:

                        if stgs.exc_withdraw == 1:
                            rc = 1
                            while int(rc) > 0:
                                res, rc = okxOp.withdraw(wallet, net_from)
                                if int(rc) > 0:
                                    logger.cs_logger.info(f'{res}')
                                    logger.cs_logger.info(f'Доп попытка вывода')
                                    #break

                        bridge_vl, result = orbiterBridge.bridge(wallet, fee, net_from, net_to)
                        bridge_value += bridge_vl
                        balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                        logger.write_overall(wallet, wallet_num, bridge_value, total_swap, nft_value, liq_value,
                                             balance_st, balance_end, script_time, nonce)

                    if bridge_mod == 2:

                        if stgs.exc_withdraw == 1:
                            rc = 1
                            while int(rc) > 0:
                                res, rc = okxOp.withdraw(wallet, nb.ethereum_network)
                                if int(rc) > 0:
                                    logger.cs_logger.info(f'{res}')
                                    logger.cs_logger.info(f'Доп попытка вывода')
                                    #break

                        bridge_vl, result = syncBridge.bridge(wallet)
                        bridge_value += bridge_vl
                        balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                        logger.write_overall(wallet, wallet_num, bridge_value, total_swap, nft_value, liq_value,
                                             balance_st, balance_end, script_time, nonce)
                else:
                    logger.cs_logger.info(f'Соединение с rpc исходящей сети не удалось')

            if result is True:
                if stgs.switch_bm1 == 0:
                    balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                    nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                    logger.write_overall(wallet, wallet_num, bridge_value, total_swap, nft_value, liq_value, balance_st,
                                         balance_end, script_time, nonce)

                modules = stgs.modules
                if stgs.modules_shuffle == 1:
                    random.shuffle(modules)

                m_count = random.randint(stgs.modules_min, stgs.modules_max)
                modules = modules[:m_count]

                if stgs.switch_teva == 1:
                    modules.append(Mods.TevaEraMint)
                    random.shuffle(modules)
                    m_count += 1

                if stgs.switch_domain == 1:
                    modules.append(Mods.DomainMint)
                    random.shuffle(modules)
                    m_count += 1

                if stgs.switch_liq == 1:
                    modules.append(Mods.Liquidity)
                    modules.append(Mods.Liquidity)
                    random.shuffle(modules)
                    m_count += 1

                if stgs.switch_rhino == 1:
                    modules.append(Mods.RhinoMint)
                    random.shuffle(modules)
                    m_count += 1

                if stgs.switch_eralend == 1:
                    modules.append(Mods.Eralend)
                    random.shuffle(modules)

                logger.cs_logger.info(f'Количество модулей: {m_count}')
                for module in modules:

                    # Модуль Ликвидности
                    if module.mod == 'liq':
                        gpc.check_limit()
                        #logger.cs_logger.info(f'***   Модуль Ликвидности   ***')
                        liq = liquidity.Liquidity()
                        liq_value += liq.liquidity_op(wallet, nt.zkSyncEra)

                    # Модуль Mint Домена
                    if module.mod == 'domain':
                        chance = random.randint(1, 100)
                        if chance <= stgs.domain_chance:
                            gpc.check_limit()
                            logger.cs_logger.info(f'')
                            logger.cs_logger.info(f'***   Модуль Mint Домена   ***')
                            nft_value += eraNameMint.era_name_mint(wallet, nt.zkSyncEra)
                            #operation += 1

                    # Модуль TevaEra NFT (citizenId, guardianId)
                    if module.mod == 'teva':
                        chance = random.randint(1, 100)
                        if chance <= stgs.teva_chance:
                            gpc.check_limit()
                            logger.cs_logger.info(f'')
                            logger.cs_logger.info(f'***   Модуль TevaEra NFT Mint   ***')
                            nft_value += tevaEraMint.teva_era_mint(wallet, nt.zkSyncEra)
                            #operation += 1

                    # Модуль zkSync Era Hunter Rhino NFT
                    if module.mod == 'rhino':
                        chance = random.randint(1, 100)
                        if chance <= stgs.rhino_chance:
                            gpc.check_limit()
                            logger.cs_logger.info(f'')
                            logger.cs_logger.info(f'***   Модуль Mint Rhino   ***')
                            nft_value += rhino_mint(wallet, nt.zkSyncEra)

                    # Модуль с несколькими свапалками (sm1)
                    if module.mod == 'sm1':
                        if stgs.switch_sm1 == 1:
                            chance = random.randint(1, 100)
                            if chance <= stgs.sm1_chance:
                                gpc.check_limit()
                                logger.cs_logger.info(f'')
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
                                logger.cs_logger.info(f'')
                                logger.cs_logger.info(f'***   Модуль свапа {module.name}   ***')
                                if module.swapper == 0:
                                    swap_mode_sm2 = random.randint(1, 5)
                                else:
                                    swap_mode_sm2 = module.swapper
                                total_swap += swapper.swap_module(wallet, module, swap_mode_sm2, swap_mode_sm2,
                                                                  swap_mode_sm2, swap_mode_sm2)
                                operation += 1

                    if module.name == 'wrapper':
                        if stgs.switch_wrapper == 1:
                            chance = random.randint(1, 100)
                            if chance <= stgs.wrapper_chance:
                                logger.cs_logger.info(f'')
                                logger.cs_logger.info(f'***   Модуль свапа {module.name}   ***')
                                wrapping(wallet, module)
                                operation += 1
                            else:
                                logger.cs_logger.info(
                                    f'В этот раз модуль не выполняется: {chance} > {stgs.wrapper_chance}')

                    if module.name == 'eralend':
                        chance = random.randint(1, 100)
                        if chance <= stgs.eralend_chance:
                            logger.cs_logger.info(f'')
                            logger.cs_logger.info(f'***   Модуль {module.name}   ***')
                            supply_ops(wallet)
                            operation += 1
                        else:
                            logger.cs_logger.info(f'В этот раз модуль не выполняется: {chance} > {stgs.eralend_chance}')

                    balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                    nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                    logger.rewrite_overall(wallet, bridge_value, total_swap, nft_value, liq_value, balance_end, nonce)
                    wallet.operation = operation

                # Депозит на биржу в сети zkSyncEra
                if stgs.switch_bridge_exc == 1:
                    if stgs.exc_deposit == 1:
                        okxOp.deposit(wallet, nb.zkSyncEra_network)
                        balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                        logger.rewrite_overall(wallet, bridge_value, total_swap, nft_value, liq_value, balance_end, nonce)

                # Депозит через бридж в другую сеть
                if stgs.switch_bridge_exc == 2:
                    net_from = helper.choice_net(networks, random.choice(stgs.net_from_code))
                    fee = net_from.web3.to_wei(helper.get_fee(net_to, net_from), 'ether')

                    # Делаем бридж в Arbitrum или Optimism
                    bridge_vl, result = orbiterBridge.bridge(wallet, fee, net_to, net_from)
                    if result is True:
                        bridge_value += bridge_vl
                        balance_end = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(wallet.address), 'ether')
                        nonce = nt.zkSyncEra.web3.eth.get_transaction_count(wallet.address)
                        # Трансфер средств на адрес биржи
                        if stgs.exc_deposit == 1:
                            okxOp.deposit(wallet, net_from)
                            logger.rewrite_overall(wallet, bridge_value, total_swap, nft_value, liq_value, balance_end, nonce)
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
