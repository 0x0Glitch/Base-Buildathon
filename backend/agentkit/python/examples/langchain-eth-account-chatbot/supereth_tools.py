import os
from typing import Annotated, Dict, List, Optional

from langchain_core.tools import tool
from web3 import Web3

from supereth_helper import crosschain_mint, crosschain_burn

@tool
def mint_supereth_crosschain(
    account_address: Annotated[str, "The address that will receive the minted SuperETH tokens"],
    amount_wei: Annotated[str, "Amount to mint in wei (as a string)"]
) -> str:
    """
    Mint SuperETH tokens to a specified address on Optimism Sepolia network.
    
    Args:
        account_address: The address that will receive the minted SuperETH tokens
        amount_wei: Amount to mint in wei (as a string)
    
    Returns:
        Transaction details as a string
    """
    # Get private key
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        return "Error: PRIVATE_KEY not set in environment"
        
    if not private_key.startswith("0x"):
        private_key = f"0x{private_key}"
    
    from eth_account import Account
    account = Account.from_key(private_key)
    
    # Convert amount from string to int
    try:
        amount = int(amount_wei)
    except ValueError:
        return "Error: Invalid amount format. Please provide amount in wei as an integer string."
    
    # Validate address
    if not Web3.is_address(account_address):
        return "Error: Invalid Ethereum address format"
    
    try:
        # Call the crosschain_mint function from supereth_helper
        result = crosschain_mint(account, account_address, amount)
        return f"Successfully minted {amount_wei} wei of SuperETH to {account_address}\nTransaction hash: {result['tx_hash']}\nStatus: {result['status']}\nBlock number: {result['block_number']}"
    except Exception as e:
        return f"Error minting SuperETH: {str(e)}"

@tool
def burn_supereth_crosschain(
    from_address: Annotated[str, "The address to burn SuperETH tokens from"],
    amount_wei: Annotated[str, "Amount to burn in wei (as a string)"]
) -> str:
    """
    Burn SuperETH tokens from a specified address on Optimism Sepolia network.
    
    Args:
        from_address: The address to burn SuperETH tokens from
        amount_wei: Amount to burn in wei (as a string)
    
    Returns:
        Transaction details as a string
    """
    # Get private key
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        return "Error: PRIVATE_KEY not set in environment"
        
    if not private_key.startswith("0x"):
        private_key = f"0x{private_key}"
    
    from eth_account import Account
    account = Account.from_key(private_key)
    
    # Convert amount from string to int
    try:
        amount = int(amount_wei)
    except ValueError:
        return "Error: Invalid amount format. Please provide amount in wei as an integer string."
    
    # Validate address
    if not Web3.is_address(from_address):
        return "Error: Invalid Ethereum address format"
    
    try:
        # Call the crosschain_burn function from supereth_helper
        result = crosschain_burn(account, from_address, amount)
        return f"Successfully burned {amount_wei} wei of SuperETH from {from_address}\nTransaction hash: {result['tx_hash']}\nStatus: {result['status']}\nBlock number: {result['block_number']}"
    except Exception as e:
        return f"Error burning SuperETH: {str(e)}"
