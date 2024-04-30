from web3 import Web3
import src.ABIs as ABIs
import settings as stgs


class Network(object):
    def __init__(self, net_name, rpc,):
        self.name = net_name
        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.chain_id = self.web3.eth.chain_id


class Token(object):
    def __init__(self, token_name, token_address):
        self.name = token_name
        self.address = token_address


mode = stgs.network_mode

if mode == 1:
    zkSyncEra = Network(
        'zkSyncEra',
        stgs.zkSyncEra_rpc
    )

    USDC_token = Token(
        'USDC',
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'
    )
    contract_USDC = zkSyncEra.web3.eth.contract(Web3.to_checksum_address(USDC_token.address), abi=ABIs.ERC20_ABI)

    wETH_token_sync = Token(
        'wETH',
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'
    )
    wETH_contract = zkSyncEra.web3.eth.contract(Web3.to_checksum_address(wETH_token_sync.address), abi=ABIs.wETH_ABI)
    wETH_token_mute = Token(
        'wETH',
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'
    )

    wETH_token_spacefi = Token(
        'wETH',
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'
    )

    wETH_token_pancake = Token(
        'wETH',
        '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'
    )

if mode == 2:  # Параметры для тестовой сети
    zkSyncEra = Network(
        'zkSyncEra',
        'https://testnet.era.zksync.dev'
    )

    USDC_token = Token(
        'USDC',
        '0x0faF6df7054946141266420b43783387A78d82A9'
    )
    contract_USDC = zkSyncEra.web3.eth.contract(Web3.to_checksum_address(USDC_token.address), abi=ABIs.ERC20_ABI)

    wETH_token_sync = Token(
        'wETH',
        '0x20b28B1e4665FFf290650586ad76E977EAb90c5D'
    )

    wETH_token_mute = Token(
        'wETH',
        '0x294cB514815CAEd9557e6bAA2947d6Cf0733f014'
    )

    wETH_token_spacefi = Token(
        'wETH',
        '0x8a144308792a23AadB118286aC0dec646f638908'
    )

    wETH_token_pancake = Token(
        'wETH',
        '0x02968DB286f24cB18bB5b24903eC8eBFAcf591C0'
    )
