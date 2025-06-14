import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
import chatbot  # Optimism
import agent2   # Base Sepolia
import agent3   # Ethereum Sepolia
import agent4   # Another variant

class TestMultiChainCompatibility(unittest.TestCase):
    
    def setUp(self):
        # Set up environment variables for testing
        self.env_patcher = patch.dict(os.environ, {
            "CDP_API_KEY_ID": "test_key_id",
            "CDP_API_KEY_SECRET": "test_key_secret",
            "OPENAI_API_KEY": "test_openai_key",
            "OPTIMISM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "ETHEREUM_CONTRACT_ADDRESS": "0x1fba25D5e71Aa1ed0aD8384f693872AbeC79e9B3",
            "BASE_SEPOLIA_CONTRACT_ADDRESS": "0x2fba25D5e71Aa1ed0aD8384f693872AbeC79e9B4",
            "CHAIN_ID_BASE_SEPOLIA": "84532",
            "CHAIN_ID_ETHEREUM_SEPOLIA": "11155111",
            "CHAIN_ID_OPTIMISM_SEPOLIA": "11155420"
        })
        self.env_patcher.start()
    
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('os.path.exists')
    @patch('json.dump')
    @patch('json.load')
    @patch('builtins.open')
    def test_correct_chain_id_selection(self, mock_open, mock_json_load, mock_json_dump, mock_exists):
        """Test that each agent selects the correct chain ID for its network."""
        # Setup mocks
        mock_exists.return_value = True
        mock_json_load.return_value = {"private_key": "0" * 64, "chain_id": "", "created_at": ""}
        
        # Test chatbot (Optimism)
        with patch('chatbot.initialize_agent') as mock_init:
            mock_init.return_value = (MagicMock(), {})
            chatbot.setup()
            args, _ = mock_init.call_args
            config = args[0]
            self.assertEqual(config.chain_id, os.getenv("CHAIN_ID", "84532"))
        
        # Test agent2 (Base Sepolia)
        with patch('agent2.initialize_agent') as mock_init:
            mock_init.return_value = (MagicMock(), {})
            agent2.setup()
            args, _ = mock_init.call_args
            config = args[0]
            self.assertEqual(config.chain_id, os.getenv("CHAIN_ID_BASE_SEPOLIA", "84532"))
        
        # Test agent3 (Ethereum Sepolia)
        with patch('agent3.initialize_agent') as mock_init:
            mock_init.return_value = (MagicMock(), {})
            agent3.setup()
            args, _ = mock_init.call_args
            config = args[0]
            self.assertEqual(config.chain_id, os.getenv("CHAIN_ID_ETHEREUM_SEPOLIA", "11155111"))
    
    def test_different_contract_addresses(self):
        """Test that each agent uses the correct contract address for its network."""
        # Check contract addresses are correctly set in env vars
        self.assertEqual(os.getenv("OPTIMISM_CONTRACT_ADDRESS"), "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2")
        self.assertEqual(os.getenv("ETHEREUM_CONTRACT_ADDRESS"), "0x1fba25D5e71Aa1ed0aD8384f693872AbeC79e9B3")
        self.assertEqual(os.getenv("BASE_SEPOLIA_CONTRACT_ADDRESS"), "0x2fba25D5e71Aa1ed0aD8384f693872AbeC79e9B4")
    
    @patch('chatbot.initialize_agent')
    @patch('agent2.initialize_agent')
    @patch('agent3.initialize_agent') 
    def test_agent_state_modifiers(self, mock_init_agent3, mock_init_agent2, mock_init_chatbot):
        """Test that each agent has the appropriate state modifier for its network."""
        # Setup mocks to capture the state_modifier parameter
        mock_init_chatbot.return_value = (MagicMock(), {})
        mock_init_agent2.return_value = (MagicMock(), {})
        mock_init_agent3.return_value = (MagicMock(), {})
        
        # Get state modifiers by calling initialize_agent with a dummy config
        dummy_config = MagicMock()
        
        chatbot.initialize_agent(dummy_config)
        agent2.initialize_agent(dummy_config)
        agent3.initialize_agent(dummy_config)
        
        # Extract state modifiers
        _, kwargs_chatbot = mock_init_chatbot.call_args
        _, kwargs_agent2 = mock_init_agent2.call_args
        _, kwargs_agent3 = mock_init_agent3.call_args
        
        # Verify network-specific mentions in state modifiers
        self.assertIn("Optimism", str(kwargs_chatbot))
        self.assertIn("Base", str(kwargs_agent2))
        self.assertIn("ETHEREUM", str(kwargs_agent3))
    
    @patch('os.path.exists')
    @patch('json.dump')
    def test_wallet_file_naming(self, mock_json_dump, mock_exists):
        """Test that wallet files are named according to the correct chain ID."""
        mock_exists.return_value = False
        
        # Test each agent with mocked Account.create
        with patch('eth_account.Account.create') as mock_create:
            mock_create.return_value = (MagicMock(), "private_key")
            
            # Test each agent's wallet file name pattern
            with patch('builtins.open') as mock_file:
                with patch('chatbot.initialize_agent', return_value=(MagicMock(), {})):
                    chatbot.setup()
                    # Get first positional arg of the first call
                    file_path = mock_file.call_args_list[0][0][0]
                    self.assertIn(f"wallet_data_{os.getenv('CHAIN_ID', '84532')}.txt", file_path)
            
            with patch('builtins.open') as mock_file:
                with patch('agent2.initialize_agent', return_value=(MagicMock(), {})):
                    agent2.setup()
                    # Get first positional arg of the first call
                    file_path = mock_file.call_args_list[0][0][0]
                    self.assertIn(f"wallet_data_{os.getenv('CHAIN_ID_BASE_SEPOLIA', '84532')}.txt", file_path)
            
            with patch('builtins.open') as mock_file:
                with patch('agent3.initialize_agent', return_value=(MagicMock(), {})):
                    agent3.setup()
                    # Get first positional arg of the first call
                    file_path = mock_file.call_args_list[0][0][0]
                    self.assertIn(f"wallet_data_{os.getenv('CHAIN_ID_ETHEREUM_SEPOLIA', '11155111')}.txt", file_path)

    @patch('supereth_helper.connect_to_optimism')
    @patch('supereth_helper.get_supereth_contract')
    def test_optimism_connection(self, mock_get_contract, mock_connect):
        """Test that the connection to Optimism Sepolia is correctly established."""
        from eth_account import Account
        from supereth_helper import crosschain_mint
        
        # Create test account
        private_key = "0x" + "0" * 64
        account = Account.from_key(private_key)
        
        # Setup mocks
        mock_web3 = MagicMock()
        mock_connect.return_value = mock_web3
        
        mock_contract = MagicMock()
        mock_get_contract.return_value = mock_contract
        
        # Setup function call mocks
        mock_fn = MagicMock()
        mock_contract.functions.crosschainMint.return_value = mock_fn
        mock_fn.build_transaction.return_value = {"from": "0x", "gas": 21000, "gasPrice": 20000000000, "nonce": 0}
        
        # Setup transaction processing mocks
        mock_web3.eth.account.sign_transaction.return_value = MagicMock(raw_transaction=b'0x')
        mock_web3.eth.send_raw_transaction.return_value = b'0xtxhash'
        mock_web3.eth.wait_for_transaction_receipt.return_value = MagicMock(status=1, blockNumber=123)
        
        # Act
        crosschain_mint(account, "0xReceiverAddress", 1000)
        
        # Assert
        mock_connect.assert_called_once()
        mock_get_contract.assert_called_once_with(mock_web3, os.getenv("OPTIMISM_CONTRACT_ADDRESS"))

if __name__ == '__main__':
    unittest.main()
