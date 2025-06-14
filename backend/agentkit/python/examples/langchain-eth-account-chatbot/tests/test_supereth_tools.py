import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supereth_tools import mint_supereth_crosschain, burn_supereth_crosschain

class TestSuperEthTools(unittest.TestCase):
    
    def setUp(self):
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            "PRIVATE_KEY": "1" * 64,
            "OPTIMISM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2"
        })
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('supereth_tools.Web3.is_address', return_value=True)
    @patch('supereth_tools.crosschain_mint')
    @patch('supereth_tools.Account.from_key')
    def test_mint_supereth_crosschain_success(self, mock_account_from_key, mock_crosschain_mint, mock_is_address):
        # Arrange
        mock_account = MagicMock()
        mock_account_from_key.return_value = mock_account
        
        mock_crosschain_mint.return_value = {
            'tx_hash': '0xabc123',
            'status': 'success',
            'block_number': 123
        }
        
        # Act
        result = mint_supereth_crosschain("0xReceiverAddress", "1000")
        
        # Assert
        self.assertIn("Successfully minted", result)
        self.assertIn("0xabc123", result)
        mock_crosschain_mint.assert_called_once_with(mock_account, "0xReceiverAddress", 1000)
        mock_is_address.assert_called_once_with("0xReceiverAddress")
    
    @patch('supereth_tools.Web3.is_address', return_value=False)
    def test_mint_supereth_crosschain_invalid_address(self, mock_is_address):
        # Act
        result = mint_supereth_crosschain("InvalidAddress", "1000")
        
        # Assert
        self.assertEqual(result, "Error: Invalid Ethereum address format")
        mock_is_address.assert_called_once_with("InvalidAddress")
    
    @patch('supereth_tools.Web3.is_address', return_value=True)
    def test_mint_supereth_crosschain_invalid_amount(self, mock_is_address):
        # Act
        result = mint_supereth_crosschain("0xReceiverAddress", "not_a_number")
        
        # Assert
        self.assertIn("Error: Invalid amount format", result)
        mock_is_address.assert_called_once_with("0xReceiverAddress")
    
    @patch('supereth_tools.Web3.is_address', return_value=True)
    @patch('supereth_tools.crosschain_burn')
    @patch('supereth_tools.Account.from_key')
    def test_burn_supereth_crosschain_success(self, mock_account_from_key, mock_crosschain_burn, mock_is_address):
        # Arrange
        mock_account = MagicMock()
        mock_account_from_key.return_value = mock_account
        
        mock_crosschain_burn.return_value = {
            'tx_hash': '0xdef456',
            'status': 'success',
            'block_number': 456
        }
        
        # Act
        result = burn_supereth_crosschain("0xFromAddress", "1000")
        
        # Assert
        self.assertIn("Successfully burned", result)
        self.assertIn("0xdef456", result)
        mock_crosschain_burn.assert_called_once_with(mock_account, "0xFromAddress", 1000)
        mock_is_address.assert_called_once_with("0xFromAddress")
    
    @patch('supereth_tools.Web3.is_address', return_value=False)
    def test_burn_supereth_crosschain_invalid_address(self, mock_is_address):
        # Act
        result = burn_supereth_crosschain("InvalidAddress", "1000")
        
        # Assert
        self.assertEqual(result, "Error: Invalid Ethereum address format")
        mock_is_address.assert_called_once_with("InvalidAddress")
    
    @patch('supereth_tools.Web3.is_address', return_value=True)
    def test_burn_supereth_crosschain_invalid_amount(self, mock_is_address):
        # Act
        result = burn_supereth_crosschain("0xFromAddress", "not_a_number")
        
        # Assert
        self.assertIn("Error: Invalid amount format", result)
        mock_is_address.assert_called_once_with("0xFromAddress")
    
    @patch('os.environ', {})
    def test_mint_supereth_crosschain_missing_private_key(self):
        # Act
        with patch.dict('os.environ', {}, clear=True):
            result = mint_supereth_crosschain("0xReceiverAddress", "1000")
        
        # Assert
        self.assertEqual(result, "Error: PRIVATE_KEY not set in environment")
    
    @patch('os.environ', {})
    def test_burn_supereth_crosschain_missing_private_key(self):
        # Act
        with patch.dict('os.environ', {}, clear=True):
            result = burn_supereth_crosschain("0xFromAddress", "1000")
        
        # Assert
        self.assertEqual(result, "Error: PRIVATE_KEY not set in environment")

if __name__ == '__main__':
    unittest.main()
