import src.helper as helper
import src.muteSwap as muteSwap
import src.syncSwap as syncSwap
import src.spacefiSwap as spacefiSwap
import src.pancakeSwap as pancakeSwap
import src.maverickSwap as maverickSwap
import src.networkTokens as nt
import src.logger as logger
import settings as stgs
import random
import datetime


class Swapper(object):
    def __init__(self, name, index):
        self.name = name
        self.id = index
        self.txns = 0
        self.value = 0

    def count_add(self, swapper_txns, swapper_value):
        self.txns += swapper_txns
        self.value += swapper_value

    def count_clear(self):
        self.txns = 0
        self.value = 0


swappers = list()
swappers.extend([
    Swapper('MuteSwap', 1),
    Swapper('SyncSwap', 2),
    Swapper('SpacefiSwap', 3),
    Swapper('PancakeSwap', 4),
    Swapper('MaverickSwap', 5)
])


def swap_ETH(swap_mode, work_mode, txn_count, wallet, swap_balance, price, step_num):
    txn_num = 0

    if swap_mode == 1:
        logger.cs_logger.info(f'{step_num}. Операции в MuteSwap ')
        logger.cs_logger.info(f'Свапаем {swap_balance} ETH | Транзакций: {txn_count}')
        txn_num = muteSwap.swapping(wallet, swap_balance, price, txn_count, work_mode,
                                    wallet.operation, wallet.txn_num)

    if swap_mode == 2:
        logger.cs_logger.info(f'{step_num}. Операции в SyncSwap ')
        logger.cs_logger.info(f'Свапаем {swap_balance} ETH | Транзакций: {txn_count}')
        txn_num = syncSwap.swapping(wallet, swap_balance, txn_count, work_mode, wallet.operation,
                                    wallet.txn_num)

    if swap_mode == 3:
        logger.cs_logger.info(f'{step_num}. Операции в SpacefiSwap ')
        logger.cs_logger.info(f'Свапаем {swap_balance} ETH | Транзакций: {txn_count}')
        txn_num = spacefiSwap.swapping(wallet, swap_balance, price, txn_count, work_mode,
                                       wallet.operation, wallet.txn_num)

    if swap_mode == 4:
        logger.cs_logger.info(f'{step_num}. Операции в PancakeSwap')
        logger.cs_logger.info(f'Свапаем {swap_balance} ETH | Транзакций: {txn_count}')
        txn_num = pancakeSwap.swapping(wallet, swap_balance, price, txn_count, work_mode,
                                       wallet.operation, wallet.txn_num)

    if swap_mode == 5:
        logger.cs_logger.info(f'{step_num}. Операции в MaverickSwap ')
        logger.cs_logger.info(f'Свапаем {swap_balance} ETH | Транзакций: {txn_count}')
        txn_num = maverickSwap.swapping(wallet, swap_balance, price, txn_count, work_mode,
                                        wallet.operation, wallet.txn_num)

    complete_txns = txn_num - wallet.txn_num
    sw = swappers[swap_mode - 1]
    sw.count_add(complete_txns, swap_balance)
    wallet.txn_num = txn_num


def swap_USDC(swap_mode, txn_count, wallet, balance_USDC, price, step_num):
    txn_num = wallet.txn_num
    swap_txns = 0
    value_USDC_max = int(balance_USDC / txn_count)
    dd = txn_count // 10
    if swap_mode == 1:
        logger.cs_logger.info(f'{step_num}. Операции в MuteSwap')
        logger.cs_logger.info(f'Продаем {balance_USDC / 10 ** 6} USDC | Транзакций: {txn_count}')
        for i in range(txn_count):
            value_USDC = int(value_USDC_max * helper.get_random_value(0.80, 0.98, 3))
            trunc_USDC = helper.trunc_value(value_USDC / 10 ** 6, stgs.digs_min_token + 1 + dd,
                                            stgs.digs_max_token + 1 + dd)
            value_USDC = int(trunc_USDC * 10 ** 6)
            if i == txn_count - 1:
                value_USDC = nt.contract_USDC.functions.balanceOf(wallet.address).call()
            logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            muteSwap.swap_USDC_to_ETH(wallet, value_USDC, price, wallet.operation, txn_num)
            txn_num += 1
            swap_txns += 1

    if swap_mode == 2:
        logger.cs_logger.info(f'{step_num}. Операции в SyncSwap')
        logger.cs_logger.info(f'Продаем {balance_USDC / 10 ** 6} USDC | Транзакций: {txn_count}')
        for i in range(txn_count):
            value_USDC = int(value_USDC_max * helper.get_random_value(0.80, 0.98, 3))
            trunc_USDC = helper.trunc_value(value_USDC / 10 ** 6, stgs.digs_min_token + 1 + dd,
                                            stgs.digs_max_token + 1 + dd)
            value_USDC = int(trunc_USDC * 10 ** 6)
            if i == txn_count - 1:
                value_USDC = nt.contract_USDC.functions.balanceOf(wallet.address).call()
            logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            syncSwap.swap_USDC_to_ETH(wallet, value_USDC, wallet.operation, txn_num)
            txn_num += 1
            swap_txns += 1

    if swap_mode == 3:
        logger.cs_logger.info(f'{step_num}. Операции в SpacefiSwap')
        logger.cs_logger.info(f'Продаем {balance_USDC / 10 ** 6} | Транзакций: {txn_count}')
        for i in range(txn_count):
            value_USDC = int(value_USDC_max * helper.get_random_value(0.80, 0.98, 3))
            trunc_USDC = helper.trunc_value(value_USDC / 10 ** 6, stgs.digs_min_token + 1 + dd,
                                            stgs.digs_max_token + 1 + dd)
            value_USDC = int(trunc_USDC * 10 ** 6)
            if i == txn_count - 1:
                value_USDC = nt.contract_USDC.functions.balanceOf(wallet.address).call()
            logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            spacefiSwap.swap_USDC_to_ETH(wallet, value_USDC, price, wallet.operation, txn_num)
            txn_num += 1
            swap_txns += 1

    if swap_mode == 4:
        logger.cs_logger.info(f'{step_num}. Операции в PancakeSwap')
        logger.cs_logger.info(f'Продаем {balance_USDC / 10 ** 6} | Транзакций: {txn_count}')
        for i in range(txn_count):
            value_USDC = int(value_USDC_max * helper.get_random_value(0.80, 0.98, 3))
            trunc_USDC = helper.trunc_value(value_USDC / 10 ** 6, stgs.digs_min_token + 1 + dd,
                                            stgs.digs_max_token + 1 + dd)
            value_USDC = int(trunc_USDC * 10 ** 6)
            if i == txn_count - 1:
                value_USDC = nt.contract_USDC.functions.balanceOf(wallet.address).call()
            logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            pancakeSwap.swap_USDC_to_ETH(wallet, value_USDC, price, wallet.operation, txn_num)
            txn_num += 1
            swap_txns += 1

    if swap_mode == 5:
        logger.cs_logger.info(f'{step_num}. Операции в MaverickSwap')
        logger.cs_logger.info(f'Продаем {balance_USDC / 10 ** 6} | Транзакций: {txn_count}')
        for i in range(txn_count):
            value_USDC = int(value_USDC_max * helper.get_random_value(0.80, 0.98, 3))
            trunc_USDC = helper.trunc_value(value_USDC / 10 ** 6, stgs.digs_min_token + 1 + dd,
                                            stgs.digs_max_token + 1 + dd)
            value_USDC = int(trunc_USDC * 10 ** 6)
            if i == txn_count - 1:
                value_USDC = nt.contract_USDC.functions.balanceOf(wallet.address).call()
            logger.cs_logger.info(f'Транзакция {i + 1} из {txn_count}')
            maverickSwap.swap_USDC_to_ETH(wallet, value_USDC, price, wallet.operation, txn_num)
            txn_num += 1
            swap_txns += 1

    complete_txns = txn_num - wallet.txn_num
    sw = swappers[swap_mode - 1]
    sw.count_add(complete_txns, 0)
    wallet.txn_num = txn_num


#'''
def swap_module(wallet, module, swap_mode_step1, swap_mode_step2, swap_mode_step3, swap_mode_step4):
    step_num = 1
    total = 0
    script_time = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
    price = helper.get_price('ETH')
    address = wallet.address

    # Первый свап \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    if stgs.work_mode == 0:
        work_mode = random.randint(1, 2)  # Рандомим режим
    else:
        work_mode = stgs.work_mode
    if swap_mode_step1 == 0:
        swap_mode = random.randint(1, 5)  # Рандомим свапалку
    else:
        swap_mode = swap_mode_step1

    txn_count = random.randint(module.txn_min1, module.txn_max1)  # Рандомим количество транзакций
    swap_balance = helper.get_open_balance(address, stgs.balance_percent_min1, stgs.balance_percent_max1, nt.zkSyncEra)

    balance_start_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
    balance_start_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6

    swap_ETH(swap_mode, work_mode, txn_count, wallet, swap_balance, price, step_num)
    step_num += 1

    txn_count = random.randint(module.txn_min2, module.txn_max2)  # Рандомим количество транзакций
    # Промежуточный свап USDC \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    if swap_mode_step2 == 0:
        swap_mode = random.randint(1, 5)  # Рандомим свапалку
    else:
        swap_mode = swap_mode_step2

    balance_USDC = nt.contract_USDC.functions.balanceOf(address).call()
    # Если баланс USDC не равен 0
    if balance_USDC != 0:

        swap_USDC(swap_mode, txn_count, wallet, balance_USDC, price, step_num)
        step_num += 1

    if balance_USDC == 0:
        # Второй свап \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        swap_balance = helper.get_open_balance(address, stgs.balance_percent_min2, stgs.balance_percent_max2, nt.zkSyncEra)

        if stgs.work_mode == 0:
            work_mode = random.randint(1, 2)  # Рандомим режим
        else:
            work_mode = stgs.work_mode

        swap_ETH(swap_mode, work_mode, txn_count, wallet, swap_balance, price, step_num)
        step_num += 1

        if swap_mode_step3 == 0:
            swap_mode = random.randint(1, 5)  # Рандомим свапалку
        else:
            swap_mode = swap_mode_step3

        balance_USDC = nt.contract_USDC.functions.balanceOf(address).call()
        if balance_USDC == 0:

            # третий свап \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
            swap_balance = helper.get_open_balance(address, stgs.balance_percent_min3, stgs.balance_percent_max3, nt.zkSyncEra)

            if stgs.work_mode == 0:
                work_mode = random.randint(1, 2)  # Рандомим режим
            else:
                work_mode = stgs.work_mode
            txn_count = random.randint(module.txn_min3, module.txn_max3)  # Рандомим количество транзакций

            swap_ETH(swap_mode, work_mode, txn_count, wallet, swap_balance, price, step_num)
            step_num += 1


        # Четвертый свап \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        # Если баланс USDC не равен 0
        balance_USDC = nt.contract_USDC.functions.balanceOf(address).call()
        if swap_mode_step4 == 0:
            swap_mode = random.randint(1, 5)  # Рандомим свапалку
        else:
            swap_mode = swap_mode_step4

        if balance_USDC != 0:
            txn_count = 1
            swap_USDC(swap_mode, txn_count, wallet, balance_USDC, price, step_num)

    mute_txns = swappers[0].txns
    sync_txns = swappers[1].txns
    spacefi_txns = swappers[2].txns
    pancake_txns = swappers[3].txns
    maverick_txns = swappers[4].txns

    mute_value = swappers[0].value
    sync_value = swappers[1].value
    spacefi_value = swappers[2].value
    pancake_value = swappers[3].value
    maverick_value = swappers[4].value

    balance_end_eth = nt.zkSyncEra.web3.from_wei(nt.zkSyncEra.web3.eth.get_balance(address), 'ether')
    balance_end_token = nt.contract_USDC.functions.balanceOf(address).call() / 10 ** 6
    logger.write_balance_sm(stgs.log_file, wallet.wallet_num, wallet.operation, module.mod, address,
                            mute_txns, mute_value, sync_txns, sync_value, spacefi_txns, spacefi_value,
                            pancake_txns, pancake_value, maverick_txns, maverick_value,
                            balance_start_eth, balance_end_eth, balance_start_token, balance_end_token, script_time)

    for sw in swappers:
        total += sw.value
        sw.count_clear()
    return total
# '''
