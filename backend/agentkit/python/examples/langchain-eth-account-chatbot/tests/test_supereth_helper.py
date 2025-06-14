import os
import unittest
from unittest.mock import patch, MagicMock
from web3 import Web3
from eth_account import Account
import sys
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supereth_helper import get_supereth_contract, connect_to_optimism, crosschain_mint, crosschain_burn

class TestSuperEthHelper(unittest.TestCase):
    
    def setUp(self):
        # Create mock account
        self.private_key = "0x" + "0" * 64
        self.account = Account.from_key(self.private_key)
        
        # Mock web3 and contract
        self.mock_web3 = MagicMock()
        self.mock_contract = MagicMock()
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            "OPTIMISM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "OPTIMISM_RPC_URL": "https://sepolia.optimism.io"
        })
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('builtins.open')
    @patch('json.load')
    def test_get_supereth_contract(self, mock_json_load, mock_open):
        # Arrange
        mock_json_load.return_value = [{"inputs": [], "name": "crosschainMint", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]
        mock_web3 = MagicMock()
        mock_web3.eth.contract.return_value = "MockContract"
        
        # Act
        contract = get_supereth_contract(mock_web3, "0xContractAddress")
        
        # Assert
        self.assertEqual(contract, "MockContract")
        mock_web3.eth.contract.assert_called_once_with(address="0xContractAddress", abi=mock_json_load.return_value)
    
    @patch('web3.Web3.HTTPProvider')
    @patch('web3.Web3.is_connected', return_value=True)
    def test_connect_to_optimism(self, mock_is_connected, mock_http_provider):
        # Act
        web3 = connect_to_optimism()
        
        # Assert
        self.assertIsNotNone(web3)
        mock_is_connected.assert_called_once()
    
    @patch('supereth_helper.connect_to_optimism')
    @patch('supereth_helper.get_supereth_contract')
    def test_crosschain_mint_success(self, mock_get_contract, mock_connect):
        # Arrange
        mock_web3 = MagicMock()
        mock_connect.return_value = mock_web3
        
        mock_contract = MagicMock()
        mock_get_contract.return_value = mock_contract
        
        # Set up the function call
        mock_fn = MagicMock()
        mock_contract.functions.crosschainMint.return_value = mock_fn
        mock_fn.build_transaction.return_value = {"from": "0x", "gas": 21000, "gasPrice": 20000000000, "nonce": 0}
        
        # Set up transaction processing
        mock_web3.eth.account.sign_transaction.return_value = MagicMock(raw_transaction=b'0x')
        mock_web3.eth.send_raw_transaction.return_value = b'0xtxhash'
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock(status=1, blockNumber=123)
        
        # Act
        result = crosschain_mint(self.account, "0xReceiverAddress", 1000)
        
        # Assert
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['block_number'], 123)
        mock_contract.functions.crosschainMint.assert_called_once_with("0xReceiverAddress", 1000)
    
    @patch('supereth_helper.connect_to_optimism')
    @patch('supereth_helper.get_supereth_contract')
    def test_crosschain_burn_success(self, mock_get_contract, mock_connect):
        # Arrange
        mock_web3 = MagicMock()
        mock_connect.return_value = mock_web3
        
        mock_contract = MagicMock()
        mock_get_contract.return_value = mock_contract
        
        # Set up the function call
        mock_fn = MagicMock()
        mock_contract.functions.crosschainBurn.return_value = mock_fn
        mock_fn.build_transaction.return_value = {"from": "0x", "gas": 21000, "gasPrice": 20000000000, "nonce": 0}
        
        # Set up transaction processing
        mock_web3.eth.account.sign_transaction.return_value = MagicMock(raw_transaction=b'0x')
        mock_web3.eth.send_raw_transaction.return_value = b'0xtxhash'
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock(status=1, blockNumber=123)
        
        # Act
        result = crosschain_burn(self.account, "0xFromAddress", 1000)
        
        # Assert
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['block_number'], 123)
        mock_contract.functions.crosschainBurn.assert_called_once_with("0xFromAddress", 1000)
    
    @patch('supereth_helper.connect_to_optimism')
    def test_crosschain_mint_missing_contract_address(self, mock_connect):
        # Arrange
        with patch.dict(os.environ, {"OPTIMISM_CONTRACT_ADDRESS": ""}, clear=True):
            # Act & Assert
            with self.assertRaises(ValueError) as context:
                crosschain_mint(self.account, "0xReceiverAddress", 1000)
            
            self.assertIn("OPTIMISM_CONTRACT_ADDRESS not set", str(context.exception))

if __name__ == '__main__':
    unittest.main()
