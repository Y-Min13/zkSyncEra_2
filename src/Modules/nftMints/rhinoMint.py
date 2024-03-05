import settings
from src.Helpers.helper import delay_sleep
from src.Helpers.txnHelper import get_txn_dict
from src.networkTokens import zkSyncEra
from src.logger import cs_logger
from src.ABIs import Rhino_zkSync_Era_Hunter_ABI
from src.Modules.nftMints.mint import mint_nft


class RhinoMint(object):
    nft_name = 'zkSync Era Hunter'
    contract_address = '0x812dE7B8cC9dC7ad5Bc929d3337BFB617Dcc7949'

    contract = zkSyncEra.web3.eth.contract(zkSyncEra.web3.to_checksum_address(contract_address),
                                           abi=Rhino_zkSync_Era_Hunter_ABI)
    nft_value = 0

    def get_mint_fee(self):
        mint_fee = self.contract.functions.mintFee().call()
        return mint_fee

    def build_txn(self, wallet, net):
        try:
            mint_fee = self.get_mint_fee()
            self.nft_value = net.web3.from_wei(mint_fee, 'ether')
            txn_mint = get_txn_dict(wallet.address, net, mint_fee)
            txn_mint['to'] = self.contract_address
            txn_mint['data'] = '0x1249c58b'
            return txn_mint, '-'
        except Exception as ex:
            cs_logger.info(f'Ошибка в (Rhino/mint: build_txn_mint) {ex.args}')


def minting(wallet, net):
    nft = RhinoMint()
    attempt = 1
    mint_status = False
    while mint_status is False and attempt < 4:
        cs_logger.info(f' _ Попытка №: {attempt}')
        mint_status = mint_nft(wallet, nft, net)
        attempt += 1
        if mint_status[1] is False:
            delay_sleep(settings.attempt_delay[0], settings.attempt_delay[1])
        else:
            return nft.nft_value
    return 0
