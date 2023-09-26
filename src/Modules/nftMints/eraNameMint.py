import src.Modules.nftMints.mint as mint
import src.logger as logger
import src.Helpers.helper as helper
import eth_abi
import settings


SYMBOLS = '0123456789-_abcdefghijklmnopqrstuvwxyz'


class DomainMint(object):
    nft_address = '0x935442AF47F3dc1c11F006D551E13769F12eab13'
    nft_name = 'RegisterName'

    def __init__(self):
        self.param = ''

    def build_txn(self, wallet, net):
        try:
            nonce = net.web3.eth.get_transaction_count(wallet.address)
            value = net.web3.to_wei(0.003, 'ether')

            param_length = helper.get_random_number(4, settings.domain_max_param_length)
            param = helper.create_param(param_length, SYMBOLS)
            self.param = param

            method = '0x40b2d3af'
            param_line = eth_abi.encode(['string'], [param])
            data = method + param_line.hex()

            txn = {
                'chainId': net.chain_id,
                'nonce': nonce,
                'from': wallet.address,
                'to': self.nft_address,
                'value': value,
                'gas': 3_000_000,
                'gasPrice': net.web3.eth.gas_price,
                'data': data,
            }

            return txn, param
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в (DomainMint: build_txn): {ex}')


class PrimaryAddressMint(object):
    nft_address = '0x935442AF47F3dc1c11F006D551E13769F12eab13'
    nft_name = 'setPrimaryAddress'

    def __init__(self, param):
        self.param = param

    def build_txn(self, wallet, net):
        try:
            nonce = net.web3.eth.get_transaction_count(wallet.address)

            param = self.param

            method = '0xc6fbf9a9'
            param_line = eth_abi.encode(['string'], [param])
            data = method + param_line.hex()

            txn = {
                'chainId': net.chain_id,
                'nonce': nonce,
                'from': wallet.address,
                'to': self.nft_address,
                'value': 0,
                'gas': 3_000_000,
                'gasPrice': net.web3.eth.gas_price,
                'data': data,
            }

            return txn, param
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в (PrimaryAddressMint: build_txn): {ex}')


def era_name_mint(wallet, net):
    txn_status1 = False
    txn_value1 = 0
    domain_mint = DomainMint()
    while txn_status1 is False:
        txn_value1, txn_status1 = mint.mint_nft(wallet, domain_mint, net)

    primary_address_mint = PrimaryAddressMint(domain_mint.param)
    txn_value2, txn_status2 = mint.mint_nft(wallet, primary_address_mint, net)

    value_sum = txn_value1 + txn_value2
    return value_sum


