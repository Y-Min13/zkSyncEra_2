
def check_balance(network, address):
    balance_wei = network.web3.eth.get_balance(address)
    return balance_wei
