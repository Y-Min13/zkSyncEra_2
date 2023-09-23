import src.networkTokens as nt
import time
import settings as stgs


def exec_txn(private_key, net, txn):
    try:
        if stgs.test_mode == 0:
            signed_txn = net.web3.eth.account.sign_transaction(txn, private_key)
            txn_hash = net.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            check_tx_status(txn_hash, net, 3)
            return txn_hash.hex(), True
        if stgs.test_mode == 1:
            txn_hash = 'TESTIKS'  # Для тестов
            return txn_hash, True
    except Exception as ex:
        return f'Ошибка в (txnHelper: exec_txn): {ex.args}', False


def check_balance_of_token(address):
    contract = nt.contract_USDC
    balance_of_token = contract.functions.balanceOf(address).call()
    return balance_of_token


def approve_amount(private_key, address, swap_contract_address):
    try:
        contract = nt.contract_USDC
        allowance = contract.functions.allowance(address, swap_contract_address).call()
        if allowance == 0:
            approve_sum = 2 ** 256 - 1
            nonce = nt.zkSyncEra.web3.eth.get_transaction_count(address)
            gas_price = nt.zkSyncEra.web3.eth.gas_price

            dict_transaction_approve = {
                'from': address,
                'chainId': nt.zkSyncEra.web3.eth.chain_id,
                'gas': 650000,
                'gasPrice': gas_price,
                'nonce': nonce,
            }
            txn_approve = contract.functions.approve(
                swap_contract_address,
                approve_sum
            ).build_transaction(dict_transaction_approve)

            estimate_gas = check_estimate_gas(txn_approve, nt.zkSyncEra)
            txn_approve['gas'] = estimate_gas

            txn_hash, txn_status = exec_txn(private_key, nt.zkSyncEra, txn_approve)
            return txn_hash
    except Exception as ex:
        return f'Ошибка: {ex.args}'


def check_tx_status(txn_hash, net, sec=3):
    status = None
    while status is None:
        txn_done = net.web3.eth.wait_for_transaction_receipt(txn_hash, 60 * 5)
        status = txn_done.get('status')
        time.sleep(sec)
    return status


def check_estimate_gas(txn, net):
    try:
        estimate_gas = net.web3.eth.estimate_gas(txn)
        return estimate_gas
    except Exception as ex:
        return f'Ошибка в (txnHelper: check_estimate_gas): {ex.args}'
