import json
import os
from web3 import Web3
from eth_account.account import Account

def get_supereth_contract(web3, contract_address):
    """
    Create a contract instance for the SuperETH contract
    
    Args:
        web3: Web3 instance connected to the Optimism Sepolia network
        contract_address: Address of the SuperETH contract
        
    Returns:
        Contract instance
    """
    # Load ABI from the JSON file
    with open(os.path.join(os.path.dirname(__file__), 'supereth_abi.json'), 'r') as f:
        abi = json.load(f)
    
    # Create contract instance
    return web3.eth.contract(address=contract_address, abi=abi)

def connect_to_optimism():
    """Connect to the Optimism Sepolia network
    
    Returns:
        Web3 instance connected to Optimism Sepolia
    """
    # Get the RPC URL from environment variable or use public endpoint
    optimism_rpc_url = os.getenv('OPTIMISM_RPC_URL', 'https://sepolia-rollup.arbitrum.io/rpc')
    web3 = Web3(Web3.HTTPProvider(optimism_rpc_url))
    if not web3.is_connected():
        raise ConnectionError(f"Failed to connect to Optimism Sepolia network at {optimism_rpc_url}")
    return web3

def crosschain_mint(account, to_address, amount):
    """
    Mint SuperETH tokens to an address on Optimism Sepolia
    
    Args:
        account: Eth account with the aiAgent private key
        to_address: Address to receive the minted tokens
        amount: Amount of tokens to mint (in wei)
        
    Returns:
        Transaction hash
    """
    # Connect to Optimism Sepolia and get contract
    web3 = connect_to_optimism()
    contract_address = os.getenv('OPTIMISM_CONTRACT_ADDRESS')
    if not contract_address:
        raise ValueError("OPTIMISM_CONTRACT_ADDRESS not set in .env file")
        
    contract = get_supereth_contract(web3, contract_address)
    
    # Build transaction
    tx = contract.functions.crosschainMint(to_address, amount).build_transaction({
        'from': account.address,
        'gas': 300000,  # Gas limit
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(account.address),
    })
    
    # Sign and send transaction
    signed_tx = web3.eth.account.sign_transaction(tx, account.key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Wait for transaction receipt
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return {
        'tx_hash': tx_hash.hex(),
        'status': 'success' if receipt.status == 1 else 'failed',
        'block_number': receipt.blockNumber
    }

def crosschain_burn(account, from_address, amount):
    """
    Burn SuperETH tokens from an address on Optimism Sepolia
    
    Args:
        account: Eth account with the aiAgent private key
        from_address: Address to burn tokens from
        amount: Amount of tokens to burn (in wei)
        
    Returns:
        Transaction hash
    """
    # Connect to Optimism Sepolia and get contract
    web3 = connect_to_optimism()
    contract_address = os.getenv('OPTIMISM_CONTRACT_ADDRESS')
    if not contract_address:
        raise ValueError("OPTIMISM_CONTRACT_ADDRESS not set in .env file")
        
    contract = get_supereth_contract(web3, contract_address)
    
    # Build transaction
    tx = contract.functions.crosschainBurn(from_address, amount).build_transaction({
        'from': account.address,
        'gas': 300000,  # Gas limit
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(account.address),
    })
    
    # Sign and send transaction
    signed_tx = web3.eth.account.sign_transaction(tx, account.key)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Wait for transaction receipt
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return {
        'tx_hash': tx_hash.hex(),
        'status': 'success' if receipt.status == 1 else 'failed',
        'block_number': receipt.blockNumber
    }
