import src.logger as logger
import src.Modules.nftMints.mint as mint


class CitizenNFT(object):
    nft_address = '0xd29Aa7bdD3cbb32557973daD995A3219D307721f'
    nft_name = 'CitizenId'

    def __init__(self):
        param = ''

    def build_txn(self, wallet, net):
        try:
            nonce = net.web3.eth.get_transaction_count(wallet.address)
            value = net.web3.to_wei(0.0003, 'ether')
            param = ''

            txn = {
                'chainId': net.chain_id,
                'nonce': nonce,
                'from': wallet.address,
                'to': self.nft_address,
                'value': value,
                'gas': 3_000_000,
                'gasPrice': net.web3.eth.gas_price,
                'data': '0xfefe409d',
            }

            return txn, param
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в (CitizenNFT: build_txn): {ex}')


class GuardianNFT(object):
    nft_address = '0x50B2b7092bCC15fbB8ac74fE9796Cf24602897Ad'
    nft_name = 'GuardianId'

    def __init__(self):
        param = ''

    def build_txn(self, wallet, net):
        try:
            nonce = net.web3.eth.get_transaction_count(wallet.address)
            param = ''

            txn = {
                'chainId': net.chain_id,
                'nonce': nonce,
                'from': wallet.address,
                'to': self.nft_address,
                'value': 0,
                'gas': 3_000_000,
                'gasPrice': net.web3.eth.gas_price,
                'data': '0x1249c58b',
            }

            return txn, param
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в (GuardianNFT: build_txn): {ex}')


def teva_era_mint(wallet, net):
    citizen_nft = CitizenNFT()
    guardian_nft = GuardianNFT()
    txn_value1, txn_status1 = mint.mint_nft(wallet, citizen_nft, net)
    txn_value2, txn_status2 = mint.mint_nft(wallet, guardian_nft, net)
    value_sum = txn_value1 + txn_value2
    return value_sum
