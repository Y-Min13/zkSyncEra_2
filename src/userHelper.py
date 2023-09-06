import settings as stgs
import src.networkBridge as nB
import src.logger as logger


def get_info(wallets):
    if stgs.exc_withdraw == 1:
        logger.cs_logger.info(f'Вывод с биржи в сеть включен!')
    else:
        logger.cs_logger.info(f'Вывод с биржи в сеть отключен!')

    if stgs.exc_deposit == 1:
        logger.cs_logger.info(f'Депозит на адрес биржи включен!')
    else:
        logger.cs_logger.info(f'Депозит на адрес биржи отключен!')

    bridge_info = ''
    if stgs.switch_bm1 == 1:
        if stgs.bridge_module == 0:
            bridge_info = 'Случайный бридж'
        if stgs.bridge_module == 1:
            nets_names = ''
            for code in stgs.net_from_code:
                for net in nB.networks:
                    if net.code == code:
                        nets_names += f' {net.name[0]} '
            bridge_info = f'Orbiter бридж из {nets_names}'

        if stgs.bridge_module == 2:
            bridge_info = 'Sync бридж'
        logger.cs_logger.info(f'Модуль бриджа активирован: {bridge_info}')

        if stgs.work_mode_bridge == 1:
            logger.cs_logger.info(f'Бриджим часть баланса в пределах от {stgs.balance_percent_bridge_min} до {stgs.balance_percent_bridge_max}')
        if stgs.work_mode_bridge == 2:
            logger.cs_logger.info(f'Бриджим весь доступный баланс')
    else:
        logger.cs_logger.info(f'Модуль бриджа выключен')

    if stgs.switch_sm1 == 1:
        logger.cs_logger.info(f'Модуль sm1 активирован. Шанс: {stgs.sm1_chance}')
    else:
        logger.cs_logger.info(f'Модуль sm1 выключен')

    if stgs.switch_sm2 == 1:
        logger.cs_logger.info(f'Модуль sm2 активирован: Шанс: {stgs.sm2_chance}')
    else:
        logger.cs_logger.info(f'Модуль sm2 выключен')

    mods_str = 'Модули: '
    for mod in stgs.modules:
        mods_str += mod.name + ', '
    logger.cs_logger.info(f'{mods_str}')

    logger.cs_logger.info('Список обнаруженных адресов кошельков -- адресов бирж')
    #i = 1
    for wallet in wallets:
        logger.cs_logger.info(f'№ {wallet.wallet_num} | {wallet.address} -- {wallet.exchange_address}')
        #i += 1

    while True:
        logger.cs_logger.info(f'Подтвердить? Y/N: ')
        answer = input('')
        if answer.lower() == 'y':
            stgs.start_flag = True
            break
        if answer.lower() == 'n':
            break
