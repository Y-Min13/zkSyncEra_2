import okx
import settings
import time
import src.logger as logger


funding_api = okx.funding.Funding(settings.api_key, settings.secret_key, settings.pass_phrase, '0')
sub_acc_api = okx.SubAccount(settings.api_key, settings.secret_key, settings.pass_phrase, '0')


def get_balance_master():
    response = funding_api.get_balances('ETH')
    if response['code'] == '0':
        balance = response['data'][0]['availBal']
        return balance, response['code']
    else:
        return f'Ошибка запроса (get_balance_master): {response} ', response['code']


def get_chain_info(net):
    info = ''
    ccy = funding_api.get_currencies('ETH')
    if ccy['code'] == '0':
        for c in ccy['data']:
            if c['chain'] == net.chain_okx:
                info = c
        return info, ccy['code']
    else:
        return f'Ошибка запроса (get_chain_info): {ccy} ', ccy['code']


def withdraw_on_chain(wallet, amount_inp, info):
    address = wallet.address
    chain = info['chain']
    fee = info['minFee']
    min_wd = info['minWd']

    amount = amount_inp - float(fee)
    logger.cs_logger.info(f'Выводим {amount} ETH в сеть {chain}')
    if float(min_wd) > amount:
        #logger.cs_logger.info(f'Выводимая сумма ({amount}) меньше минимально допустимой: {min_wd}')
        return f'Выводимая сумма ({amount}) меньше минимально допустимой: {min_wd}', '420'
    else:
        if settings.test_mode == 0:
            response = funding_api.set_withdrawal('ETH', str(amount), '4', address, fee, chain)

            if response['code'] == '0':
                return response, response['code']
            else:
                return f'Ошибка запроса (withdraw_on_chain): {response} ', response['code']

        if settings.test_mode == 1:
            response = 'Тестовый вывод'
            return response, '0'


def get_sub_accounts():
    subs = list()
    sub_acc_list = sub_acc_api.get_list()
    if sub_acc_list['code'] == '0':
        for sub in sub_acc_list['data']:
            subs.append(sub)
        return subs
    else:
        return f'Ошибка запроса (get_sub_accounts): {sub_acc_list} '


def get_balance_sub(sub):
    sub_name = sub['subAcct']
    response = sub_acc_api.get_asset_balances(sub_name, 'ETH')
    if response['code'] == '0':
        balance = response['data'][0]['availBal']
        return balance
    else:
        return f'Ошибка запроса (get_balance_sub): {response} '


def check_deposit(subs, balance_ms_old):
    balances = list()
    main_acc = False
    last_sub = ''
    #balance_ms_old, code = get_balance_master()
    for sub in subs:
        balance_old = '0'
        #balance_old = get_balance_sub(sub)
        balances.append([sub, balance_old])
        time.sleep(0.5)
    flag = True
    while flag is True:
        balance_ms_new, code = get_balance_master()
        if balance_ms_old != balance_ms_new:
            flag = False
            main_acc = True
            logger.cs_logger.info('Средства поступили на аккаунт')
            break
        for bal in balances:
            last_sub = bal[0]
            new_bal = get_balance_sub(bal[0])
            time.sleep(1)
            if new_bal != bal[1]:
                flag = False
                main_acc = False
                logger.cs_logger.info('Средства поступили на субаккаунт')
                break
        time.sleep(15)
    return last_sub, main_acc


def transfer_to_master(amount_inp, sub):
    sub_name = sub['subAcct']
    amount = str(amount_inp)

    response = funding_api.set_transfer('ETH', amount, '6', '6', sub_name, '2')
    if response['code'] == '0':
        return response
    else:
        return f'Ошибка запроса (transfer_to_master): {response} '


def check_transfer(old_bal):
    new_bal = old_bal
    flag = True
    while flag is True:
        new_bal, code = get_balance_master()
        time.sleep(0.25)
        if new_bal != old_bal:
            flag = False
        time.sleep(10)
    logger.cs_logger.info('Средства поступили на главный аккаунт')
    return new_bal


def wait_deposit(balance_ms_old):
    subs = get_sub_accounts()
    sub, main_acc = check_deposit(subs, balance_ms_old)
    if main_acc is False:
        balance_sub = get_balance_sub(sub)
        old_balance_master, code = get_balance_master()
        transfer_to_master(balance_sub, sub)
        new_bal = check_transfer(old_balance_master)
    else:
        new_bal, code = get_balance_master()
    return new_bal
