import settings as stgs
import src.Modules.Bridges.networkBridge as nB
import src.logger as logger


def get_info(wallets):
    if stgs.exc_withdraw == 1:
        logger.cs_logger.info(f'Вывод с биржи в сеть включен!')
        if stgs.exc_mode == 1:
            logger.cs_logger.info(f'Выводим {stgs.exc_percent[0] * 100} - {stgs.exc_percent[1] * 100} % от баланса')
        if stgs.exc_mode == 2:
            logger.cs_logger.info(f'Выводим весь доступный баланс')
        if stgs.exc_mode == 3:
            logger.cs_logger.info(f'Выводим сумму от {stgs.exc_sum[0]} до {stgs.exc_sum[1]} ETH')

    else:
        logger.cs_logger.info(f'Вывод с биржи в сеть отключен!')

    if stgs.exc_deposit == 1:
        logger.cs_logger.info(f'Депозит на адрес биржи включен!')
    else:
        logger.cs_logger.info(f'Депозит на адрес биржи отключен!')

    bridge_info = ''
    if stgs.switch_bm1 == 1:
        logger.cs_logger.info(f'Прямой вывод с биржи!')
    if stgs.switch_bm1 == 2:
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
        logger.cs_logger.info(f'Вывод через бридж активирован: {bridge_info}')

        if stgs.work_mode_bridge == 1:
            logger.cs_logger.info(f'Бриджим часть баланса в пределах от {stgs.balance_percent_bridge_min} до {stgs.balance_percent_bridge_max}')
        if stgs.work_mode_bridge == 2:
            logger.cs_logger.info(f'Бриджим весь доступный баланс')

    if stgs.switch_bm1 == 0:
        logger.cs_logger.info(f'Модуль бриджа выключен')

    if stgs.switch_liq == 1:
        logger.cs_logger.info(f'Модуль ликвидности включен.')
        if stgs.liq_add == 1:
            logger.cs_logger.info(f'Добавление ликвидности включено.')
        else:
            logger.cs_logger.info(f'Добавление ликвидности отключено.')
        if stgs.liq_burn == 1:
            logger.cs_logger.info(f'Вывод ликвидности включен.')
        else:
            logger.cs_logger.info(f'Вывод ликвидности отключен.')
    else:
        logger.cs_logger.info(f'Модуль ликвидности отключен!')

    if stgs.switch_teva == 1:
        logger.cs_logger.info(f'TevaEra NFT Mint включен. Шанс: {stgs.teva_chance}')
    else:
        logger.cs_logger.info(f'TevaEra NFT Mint отключен!')

    if stgs.switch_domain == 1:
        logger.cs_logger.info(f'EraNameService NFT Mint включен. Шанс: {stgs.domain_chance}')
    else:
        logger.cs_logger.info(f'EraNameService NFT Mint отключен!')

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
