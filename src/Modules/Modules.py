
class ModuleSM2(object):
    mod = 'sm2'

    def __init__(self, name, swapper, txn_min1, txn_max1, txn_min2, txn_max2, txn_min3, txn_max3):
        self.name = name
        self.swapper = swapper
        self.txn_min1 = txn_min1
        self.txn_max1 = txn_max1
        self.txn_min2 = txn_min2
        self.txn_max2 = txn_max2
        self.txn_min3 = txn_min3
        self.txn_max3 = txn_max3


class ModuleSM1(object):
    mod = 'sm1'

    def __init__(self, name, txn_min1, txn_max1, txn_min2, txn_max2, txn_min3, txn_max3):
        self.name = name
        self.txn_min1 = txn_min1
        self.txn_max1 = txn_max1
        self.txn_min2 = txn_min2
        self.txn_max2 = txn_max2
        self.txn_min3 = txn_min3
        self.txn_max3 = txn_max3


class TevaEraMint(object):
    mod = 'teva'
    name = 'teva'


class DomainMint(object):
    mod = 'domain'
    name = 'domain'


class RhinoMint(object):
    mod = 'rhino'
    name = 'rhino'


class Liquidity(object):
    mod = 'liq'
    name = 'liquidity'
