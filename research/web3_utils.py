from web3 import Web3
from dotenv import load_dotenv
import os
import json

load_dotenv()



def call_contract(method, arg, value=0):
    load_dotenv()
    
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    assert w3.is_connected() == True
    
    pk = os.environ.get('PRIVATE_KEY')
    acct = w3.eth.account.from_key(pk)
    
    contract_addr = os.environ.get('CONTRACT_ADDRESS')
    print("contract_address", contract_addr)
    with open("../abi.json", "r") as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=contract_addr, abi=abi)

    args = {
        "from": acct.address,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "value": value
    }
    
    unsent_tx = contract.functions[method](arg).build_transaction(args)
    signed_tx = w3.eth.account.sign_transaction(unsent_tx, private_key=acct.key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("Call", method, arg, w3.eth.wait_for_transaction_receipt(tx_hash))