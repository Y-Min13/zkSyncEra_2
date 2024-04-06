from src.Modules.Modules import ModuleSM1 as SM1
from src.Modules.Modules import ModuleSM2 as SM2


# Параметры скрипта:
modules = list()
wallet_mode = 2  # Режим кошельков: 1 - порядок как в файле, 2 - случайный порядок
work_mode = 0  # Вариант работы свапов 1 или 2, 0 - рандом
gas_price_limit = 40  # Лимит цены газа в Эфире

wallets = open('wallet.txt')   # Файл с приватниками
log_file = 'ZkSyncEra logs.xlsx'  # Файл с результатами свапа
slippage = 0.020  # Проскальзывание для Mute, Spacefi, Pancake и Maverick (2%)
gas_mult = [1.05, 1.10]  # Множитель для количества газа транзакций
max_priority = 0.01  # приоритет газа в Era


#       / Параметры биржи /
api_key = ''  # Ключ API основного аккаунта биржи
secret_key = ''  # Секретный ключ
pass_phrase = ''  # Пасс-фраза

exc_withdraw = 0  # Вывод с биржи на кошельки: 0 - выкл / 1 - вкл
exc_deposit = 1  # Депозит с кошельков на биржу: 0 - выкл / 1 - вкл
sub_acc_transfer = 1  # Включен ли перевод средств с суб акков на главный. Если выкл, то скрипт не ждет поступления депозита
deposit_digs = [4, 5]  # Количество знаков после запятой для округления суммы депозита на биржу

exc_mode = 1  # Режим вывода средств с биржи: 1 - часть от баланса | 2 - весь доступный баланс | 3 - число в ед. эфира
exc_percent = [0.3, 0.4]  # Процент баланса, который будем выводить с биржи

exc_sum = [0.04, 0.06]  # Количество эфира, которое выводим с биржи
exc_sum_digs = [3, 5]  # количество знаков для округления суммы вывода с биржи

exc_limit_max = 0.001  # Верхняя граница суммы вывода с биржи (в единицах эфира)
exc_percent_step = 0.05  # Шаг, с которым уменьшаются границы процента баланса

deposit_remains = [0.0003, 0.0004]  # Остаток на кошельке при переводе на адрес биржи (ETH)
deposit_remains_digs = 5  # Количество знаков после запятой для остатка на кошельке

sync_remains = [0.0001, 0.0005]  # Остаток на кошельке при Sync бридже из Эфира в zkSync (ETH)
sync_digs = 5  # Количество знаков после запятой для остатка при Sync бридже из Эфира в zkSync

ob_remains1 = [0, 0]  # Остаток на кошельке при Orbiter бридже в zkSync (ETH)
ob_digs1 = 1  # Количество знаков после запятой для остатка при Orbiter бридже в zkSync

ob_remains2 = [0.0001, 0.0005]  # Остаток на кошельке при Orbiter бридже из zkSync в Arbitrum/Optimism (ETH)
ob_digs2 = 5  # Количество знаков после запятой для остатка при Orbiter бридже из zkSync в Arbitrum/Optimism

exc_digs_min = 4  # Минимальное количество знаков после запятой для суммы вывода с биржи (при % от баланса)
exc_digs_max = 5  # Максимальное количество знаков после запятой для суммы вывода с биржи (при % от баланса)

#       / Параметры rpc для сетей /
# rpc Эфира, для чека цены газа и SyncBridge
ether_rpc = 'https://eth-mainnet.g.alchemy.com/v2/gmJx-uFyEfIjJZ9Z52OwEM67uZyYIDdn'
zkSyncEra_rpc = 'https://mainnet.era.zksync.io'
arbitrum_rpc = 'https://arb-mainnet.g.alchemy.com/v2/MpkakD255V5Ls7G9QTdkaIvq8eYKsmNe'
optimism_rpc = 'https://1rpc.io/op'


#       / Включение (1) | (0) Выключение модулей /
switch_bm1 = 0  # Как выводим средства в zkSyncEra (0 - выкл, 1 - прямой вывод с биржи, 2 - вывод через бридж)
switch_bridge_exc = 2  # Как производим депозит средств на биржу (0 - выкл, 1 - депозит из сети zkSyncEra, 2 - через бридж)
switch_sm1 = 1  # Включить модуль свапа с несколькими свапалками (sm1)?
switch_sm2 = 1  # Включить модуль свапа с одной свапалкой (sm2)?
switch_teva = 0  # Включючить модуль минта NFT tevaEra (teva)?
switch_domain = 0  # Включить модуль минта домена eraName (domain)?
switch_liq = 1  # Включить модуль ликвидности (liq)?
switch_rhino = 1  # Включить модуль минтинга Rhino

#       / Параметры NFT /
domain_max_param_length = 20  # Максимальная длина параметря для eraNameService (domain)
attempt_delay = [2, 4]  # Промежуток между попытками минта некоторых NFT

#       / Параметры ликвидности /
liq_balance_perc = [0.25, 0.30]  # процент от баланса для ликвидности
liq_balance_digs = [3, 5]  # количество знаков для округления процента от баланса для ликвидности
liq_add = 1  # Включение добавления ликвидности
liq_burn = 1  # Включение сжигания ликвидности

#       / Порядок модулей после бриджа /
# Модули: (Имя модуля, Свапалка(для sm2), Минимум транз1, Максимум транз1,
#          Минимум транз2, Максимум транз2,Минимум транз3, Максимум транз3)
modules.extend([
    SM2('sm2_1', 0, 2, 2, 1, 2, 1, 2),
    SM1('sm1_1', 1, 2, 1, 2, 1, 2),
])
modules_shuffle = 1  # Перемешать порядок модулей? 1 - да, 0 - нет

modules_min = 2  # Минимальное количество модулей для кошелька
modules_max = 3  # Максимальное количество модулей для кошелька


#       / Шанс выполнения модуля /
sm1_chance = 100
sm2_chance = 100
teva_chance = 100
domain_chance = 100
rhino_chance = 100

#       / Параметры для выбора свапалок /
# Выбор свапалки для модуля с разными свапалками (sm1):
#  0 - рандом, 1 - Mute, 2 - Sync, 3 - Spacefi, 4 - Pancake, 5 - Maverick
swap_mode_step1 = 0  # Шаг 1 (свап 1)
swap_mode_step2 = 0  # Шаг 2 (свап 2)
swap_mode_step3 = 0  # Шаг 3 (свап 3)
swap_mode_step4 = 0  # Шаг 4 (свап 4)


#       / Параметры округления для суммы свапа /
digs_min_eth = 3  # Минимальное количество знаков после запятой для округления Эфира при свапах
digs_max_eth = 5  # Максимальное количество знаков после запятой для округления Эфира при свапах

digs_min_token = 2  # Минимальное количество знаков после запятой для округления USDC при свапах
digs_max_token = 3  # Максимальное количество знаков после запятой для округления USDC при свапах

percent_digs = 3  # Количество знаков после запятой для доли (0.305 = 30.5 %)


#       / Параметры доступного баланся для свапа /
balance_percent_min1 = 0.30  # Минимальная доля баланса для первой свапалки
balance_percent_max1 = 0.52  # Максимальная доля баланса для первой свапалки

balance_percent_min2 = 0.30  # Минимальная доля баланса для второй свапалки
balance_percent_max2 = 0.40  # Максимальная доля баланса для второй свапалки

balance_percent_min3 = 0.45  # Минимальная доля баланса для третьей свапалки
balance_percent_max3 = 0.63  # Максимальная доля баланса для третьей свапалки

#      / Параметры задержек между свапами /
min_delay = 1   # Минимальная
max_delay = 5  # и максимальная величина задержки между свапами

wallet_delay = [10, 15]  # Задержки между кошельками


#       / Параметры для бриджа /
bridge_module = 0  # Выбор бриджа: 0 - случайный, 1 - Orbiter, 2 - Sync

digs_bridge_min = 3  # Минимальное количество знаков после запятой для округления (НЕ МЕНЕЕ 3)
digs_bridge_max = 5  # Максимальное количество знаков после запятой для округления (НЕ МЕНЕЕ 3)

taxMin = 1.80   # Минимальная граница для множителя комиссии в SyncBridge
taxMax = 1.90   # Максимальная граница для множителя комиссии в SyncBridge

net_from_code = [9002, 9007]  # Коды сетей, из которых будем бриджить  (Arbitrum: 9002), (Optimism: 9007)
net_to_code = 9014  # Код сети, в которую будем бриджить (zkSyncEra: 9014)

work_mode_bridge = 2  # Режим работы скрипта (1 - бридж % от баланса, 2 - всего доступного эфира)

balance_percent_bridge_min = 0.35  # Минимальная доля баланса для бриджа
balance_percent_bridge_max = 0.40  # Максимальная доля баланса для бриджа

gas_price_limit_bridge = 30  # Лимит цены газа (gWei) для бриджа (в исходящей сети)

random_mult_max = 1.20  # Максимальный множитель цены газа для транзакции бриджа
random_mult_min = 1.15  # Минимальный множитель цены газа для транзакции бриджа


#       / Переменные для работы скрипта /
exc_remains = [0.00003, 0.00005]  # Запас эфира при переводе на адрес биржи и бридже (ETH), чтобы точно прошло
rem_digs = 5  # Количество знаков после запятой для остатка на кошельке
network_mode = 1
test_mode = 0
gas_price_ether = 99
stop_flag = False
start_flag = False
last_row = 1


#       / Тестовые параметры /
min_swap_value = 0.000012    # Минимальная
max_swap_value = 0.000024    # и максимальная сумма свапа в Eth
digs = 6       # Количество знаков после запятой для округления
