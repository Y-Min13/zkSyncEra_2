import settings
import src.logger as logger
import src.Helpers.helper as helper
import src.Helpers.txnHelper as txnHelper


def mint_nft(wallet, nft, net):
    try:
        txn_status = False
        balance_st = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')
        txn_value = 0
        script_time = helper.get_curr_time()

        txn, param = nft.build_txn(wallet, net)
        est_gas = txnHelper.check_estimate_gas(txn, net)
        if type(est_gas) is str:
            logger.cs_logger.info(est_gas)
        else:
            logger.cs_logger.info(f'Минтим NFT: {nft.nft_name}')
            txn['gas'] = int(est_gas)
            txn_hash, txn_status = txnHelper.exec_txn(wallet.key, txn, net)
            logger.cs_logger.info(f'Hash mint: {txn_hash}')

            if txn_status is True:
                wallet.txn_num += 1
                txn_value = net.web3.from_wei(txn['value'], 'ether')
                balance_end = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')

                log = logger.LogNFT(wallet, txn_hash, nft, txn_value, param, balance_st, balance_end, script_time)
                log.write_log()

            helper.delay_sleep(settings.min_delay, settings.max_delay)
        return txn_value, txn_status

    except Exception as ex:
        logger.cs_logger.info(f'Ошибка в (mint: mint_nft): {ex}')
        return 0, False
