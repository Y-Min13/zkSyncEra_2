import settings
import decimal
import src.ABIs as ABIs
import eth_abi
import src.logger as logger
from web3 import constants
import src.Helpers.txnHelper as txnHelper
import src.Helpers.helper as helper


class Liquidity(object):
    LP_address = '0x80115c708E12eDd42E504c1cD52Aea96C547c05c'
    sync_swap_address = '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295'
    vault_address = '0x621425a1Ef6abE91058E9712575dcc4258F8d091'
    domain_name = 'SyncSwap USDC/WETH Classic LP'
    usdc_address = '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'
    weth_address = '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91'
    zero_address = constants.ADDRESS_ZERO

    def __init__(self):
        self.param = ''

    def get_allowance(self, wallet, net):
        contract = net.web3.eth.contract(self.LP_address, abi=ABIs.ERC20_ABI)
        allowance = contract.functions.allowance(wallet.address, self.sync_swap_address).call()
        return allowance

    def get_balance_lp(self, address, net):
        contract = net.web3.eth.contract(self.LP_address, abi=ABIs.ERC20_ABI)
        balance = contract.functions.balanceOf(address).call()
        return balance

    def get_balance_of(self, address, net):
        contract = net.web3.eth.contract(self.vault_address, abi=ABIs.SyncSwap_Vault_ABI)
        balance = contract.functions.balanceOf(address, self.LP_address).call()
        return balance

    def get_supply(self, net):
        contract = net.web3.eth.contract(self.LP_address, abi=ABIs.ERC20_ABI)
        supply = contract.functions.totalSupply().call()
        return supply

    def approve_lp(self, wallet, net):
        try:
            contract = net.web3.eth.contract(self.LP_address, abi=ABIs.ERC20_ABI)
            allowance = self.get_allowance(wallet, net)
            if allowance == 0:
                approve_sum = 2 ** 256 - 1
                nonce = net.web3.eth.get_transaction_count(wallet.address)

                dict_transaction_approve = {
                    'from': wallet.address,
                    'chainId': net.chain_id,
                    'gas': 650000,
                    'gasPrice': net.web3.eth.gas_price,
                    'nonce': nonce,
                }
                txn_approve = contract.functions.approve(
                    self.sync_swap_address,
                    approve_sum
                ).build_transaction(dict_transaction_approve)

                estimate_gas = txnHelper.check_estimate_gas(txn_approve, net)
                txn_approve['gas'] = estimate_gas

                txn_hash, txn_status = txnHelper.exec_txn(wallet.key, net, txn_approve)
                return txn_hash
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в approve_lp: {ex}')

    def get_lp_price(self, net):
        try:
            balance_eth = self.get_balance_of(self.zero_address, net)
            balance_usdc = self.get_balance_of(self.usdc_address, net)

            usdc = decimal.Decimal(balance_usdc / 10 ** 6)
            ether = net.web3.from_wei(balance_eth, 'ether')
            price = decimal.Decimal(helper.get_price('ETH'))

            tvl = (usdc + (ether * price))
            supply = net.web3.from_wei(self.get_supply(net), 'ether')
            lp_mult = price / (tvl / supply)
            lp_price = net.web3.to_wei(1, 'ether') / net.web3.to_wei(lp_mult, 'ether')

            return lp_price
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в get_lp_price: {ex}')

    def build_txn_liq_add(self, wallet, net, value_wei):
        try:
            nonce = net.web3.eth.get_transaction_count(wallet.address)
            contract = net.web3.eth.contract(self.sync_swap_address, abi=ABIs.SyncSwap_ABI)

            lp_mult = self.get_lp_price(net)
            LP_amount = int((value_wei / lp_mult) * 0.99)
            wl_line = eth_abi.encode(['address'], [wallet.address])

            txn_dict = {
                'chainId': net.web3.eth.chain_id,
                'from': wallet.address,
                'value': value_wei,
                'gas': 1_500_000,
                'nonce': nonce,
                'gasPrice': net.web3.eth.gas_price,
            }

            txn = contract.functions.addLiquidity2(
                self.LP_address, [(self.usdc_address, 0), (self.zero_address, value_wei)],
                wl_line, LP_amount, self.zero_address, b''
            ).build_transaction(txn_dict)

            return txn
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в build_txn_liq_add: {ex}')

    def build_txn_liq_burn(self, wallet, net, lp_wei):
        try:
            nonce = net.web3.eth.get_transaction_count(wallet.address)
            contract = net.web3.eth.contract(self.sync_swap_address, abi=ABIs.SyncSwap_ABI)

            lp_mult = self.get_lp_price(net)
            data = (eth_abi.encode(['address'], [self.weth_address]).hex().removeprefix('0x') +
                    eth_abi.encode(['address'], [wallet.address]).hex().removeprefix('0x') +
                    eth_abi.encode(['address'], ['0x0000000000000000000000000000000000000001']).hex().removeprefix('0x')
                    )
            data_line = '0x'+data
            min_amount = int((lp_wei * lp_mult) * 0.99)

            txn_dict = {
                'chainId': net.web3.eth.chain_id,
                'from': wallet.address,
                'value': 0,
                'gas': 1_500_000,
                'nonce': nonce,
                'gasPrice': net.web3.eth.gas_price,
            }

            txn = contract.functions.burnLiquiditySingle(
                self.LP_address, lp_wei, data_line, min_amount,
                self.zero_address, b''
            ).build_transaction(txn_dict)

            return txn
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в build_txn_liq_burn: {ex}')

    def liquidity_add(self, wallet, net, value_wei):
        try:
            balance_st = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')
            script_time = helper.get_curr_time()

            value_eth = net.web3.from_wei(value_wei, "ether")
            logger.cs_logger.info(f'Добавляем ликвидность {value_eth} ETH через SyncSwap')
            txn = self.build_txn_liq_add(wallet, net, value_wei)
            est_gas = txnHelper.check_estimate_gas(txn, net)
            if type(est_gas) is str:
                logger.cs_logger.info(f'{est_gas}')
                return False, 0
            else:
                txn['gas'] = est_gas
                txn_hash, txn_status = txnHelper.exec_txn(wallet.key, net, txn)
                logger.cs_logger.info(f'Hash: {txn_hash}')
                helper.delay_sleep(settings.min_delay, settings.max_delay)

                wallet.txn_num += 1
                balance_end = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')
                log = logger.LogLiquidity(wallet, txn_hash, value_eth, '', balance_st, balance_end, script_time)
                log.write_log()

                return True, value_eth
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в liquidity_add: {ex}')
            return False, 0

    def liquidity_burn(self, wallet, net, lp_value_wei):
        try:
            balance_st = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')
            script_time = helper.get_curr_time()
            self.approve_lp(wallet, net)

            value_lp = net.web3.from_wei(lp_value_wei, "ether")
            logger.cs_logger.info(f'Выводим ликвидность {value_lp} LP token через SyncSwap')
            txn = self.build_txn_liq_burn(wallet, net, lp_value_wei)
            est_gas = txnHelper.check_estimate_gas(txn, net)
            if type(est_gas) is str:
                logger.cs_logger.info(f'{est_gas}')
                return False, 0
            else:
                txn['gas'] = est_gas
                txn_hash, txn_status = txnHelper.exec_txn(wallet.key, net, txn)
                logger.cs_logger.info(f'Hash: {txn_hash}')
                helper.delay_sleep(settings.min_delay, settings.max_delay)

                wallet.txn_num += 1
                balance_end = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')
                log = logger.LogLiquidity(wallet, txn_hash, '', value_lp, balance_st, balance_end, script_time)
                log.write_log()
                return True, 0
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в liquidity_burn: {ex}')
            return False, 0

    def liquidity_op(self, wallet, net):
        try:
            liq_value = 0
            balance_lp = self.get_balance_lp(wallet.address, net)

            if settings.liq_add == 1 and settings.liq_burn == 1:
                logger.cs_logger.info(f'***   Модуль Ликвидности   ***')
                if wallet.liq == 1:
                    if balance_lp > 0:
                        self.liquidity_burn(wallet, net, balance_lp)
                    else:
                        logger.cs_logger.info(f'Баланс LP токена равен 0.')

                if wallet.liq == 0:
                    percent = decimal.Decimal(
                        helper.get_random_value(settings.liq_balance_perc[0], settings.liq_balance_perc[1]))
                    balance = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')
                    value = helper.trunc_value(balance * percent, settings.liq_balance_digs[0],
                                               settings.liq_balance_digs[1])
                    value_wei = net.web3.to_wei(value, 'ether')
                    status, liq_value = self.liquidity_add(wallet, net, value_wei)
                    wallet.liq += 1

            if settings.liq_add == 1 and settings.liq_burn == 0:
                if wallet.liq == 0:
                    logger.cs_logger.info(f'***   Модуль Ликвидности   ***')
                    percent = decimal.Decimal(
                        helper.get_random_value(settings.liq_balance_perc[0], settings.liq_balance_perc[1]))
                    balance = net.web3.from_wei(net.web3.eth.get_balance(wallet.address), 'ether')
                    value = helper.trunc_value(balance * percent, settings.liq_balance_digs[0],
                                               settings.liq_balance_digs[1])
                    value_wei = net.web3.to_wei(value, 'ether')
                    status, liq_value = self.liquidity_add(wallet, net, value_wei)
                    wallet.liq += 1

            if settings.liq_add == 0 and settings.liq_burn == 1:
                if wallet.liq == 0:
                    logger.cs_logger.info(f'***   Модуль Ликвидности   ***')
                    if balance_lp > 0:
                        self.liquidity_burn(wallet, net, balance_lp)
                        wallet.liq += 1
                    else:
                        logger.cs_logger.info(f'Баланс LP токена равен 0.')
                        wallet.liq += 2

            return liq_value
        except Exception as ex:
            logger.cs_logger.info(f'Ошибка в liquidity_op: {ex}')
            return 0
