
class Wallet(object):
    def __init__(self, wallet_num, key, address, exc_address, index):
        self.wallet_num = wallet_num
        self.key = key
        self.address = address
        self.exchange_address = exc_address
        self.operation = 1
        self.index = index
        self.txn_num = 0
        self.exc_bal_st = 0
        self.exc_bal_end = 0
