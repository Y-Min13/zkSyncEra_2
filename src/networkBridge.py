from web3 import Web3
import settings as stgs


# Класс для сетей используемых в бридже Orbiter
class Network(object):
    fees = list()

    def __init__(self, net_name, rpc, chain_okx, code, transfer):
        self.name = net_name,
        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.chain_okx = chain_okx
        self.code = code
        self.transfer = transfer


class BridgeFee(object):
    def __init__(self, net_from, fee_sum):  # Параметры при создании: сеть, из которой бриджим и сумма комиссии
        self.net_from_code = net_from.code  # Код сети из которой бриджим
        self.fee_sum = fee_sum  # Сумма комиссии


networks = list()

# Создание новой сети
ethereum_network = Network(
    'Ethereum',   # Имя сети
    stgs.ether_rpc,
    'ETH-ERC20',
    9001,  # код сети в орбитере
    0

)
# Добавление новой сети в список сетей
networks.append(ethereum_network)

zkSyncEra_network = Network(
    'zkSyncEra',
    stgs.zkSyncEra_rpc,
    'Not Supported',
    9014,
    0
)
networks.append(zkSyncEra_network)

arbitrum_network = Network(
    'Arbitrum',
    stgs.arbitrum_rpc,
    'ETH-Arbitrum One',
    9002,
    [2_000_000, 3_000_000]
)
networks.append(arbitrum_network)

optimism_network = Network(
    'Optimism',
    stgs.optimism_rpc,
    'ETH-Optimism',
    9007,
    [30_000, 40_000]
)
networks.append(optimism_network)
# Добавляем комиссии для каждой сети


# Создаем список комиссий для определенной сети
arbitrum_fees = list()  # список комиссий для Арбитрума
arbitrum_fees.extend([
    BridgeFee(ethereum_network, 0.0012),  # Комиссия при бридже из Эфира в Арбитрум
    BridgeFee(zkSyncEra_network, 0.0013),  # Комиссия при бридже из Эры в Арбитрум
])
arbitrum_network.fees = arbitrum_fees

zkSyncEra_fees = list()
zkSyncEra_fees.extend([
    BridgeFee(ethereum_network, 0.0021),
    BridgeFee(arbitrum_network, 0.0016),
    BridgeFee(optimism_network, 0.0016)
])
zkSyncEra_network.fees = zkSyncEra_fees

optimism_fees = list()
optimism_fees.extend([
    BridgeFee(zkSyncEra_network, 0.0017)
])
optimism_network.fees = optimism_fees
