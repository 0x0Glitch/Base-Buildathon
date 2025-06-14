import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import json
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eth_account import Account
from coinbase_agentkit import EthAccountWalletProviderConfig

# Import modules to test
import chatbot
import agent2
import agent3
from supereth_helper import connect_to_optimism, get_supereth_contract
from supereth_tools import mint_supereth_crosschain, burn_supereth_crosschain

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test account
        self.private_key = "0x" + "1" * 64
        self.account = Account.from_key(self.private_key)
        
        # Set up environment variables for testing
        self.env_patcher = patch.dict(os.environ, {
            "CDP_API_KEY_ID": "test_key_id",
            "CDP_API_KEY_SECRET": "test_key_secret",
            "OPENAI_API_KEY": "test_openai_key",
            "OPTIMISM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "ETHEREUM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "BASE_SEPOLIA_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "CHAIN_ID": "84532",
            "PRIVATE_KEY": "1" * 64
        })
        self.env_patcher.start()
        
        # Create test wallet file
        self.wallet_data = {
            "private_key": "1" * 64,
            "chain_id": "84532",
            "created_at": "2023-01-01 00:00:00"
        }
        with open("wallet_data_84532.txt", "w") as f:
            json.dump(self.wallet_data, f)
    
    def tearDown(self):
        # Clean up test environment
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
        self.env_patcher.stop()
    
    @patch('chatbot.ChatOpenAI')
    @patch('chatbot.EthAccountWalletProvider')
    @patch('chatbot.AgentKit')
    @patch('chatbot.get_langchain_tools')
    @patch('chatbot.create_react_agent')
    def test_end_to_end_agent_initialization(self, mock_create_agent, mock_get_tools, 
                                           mock_agentkit, mock_provider, mock_openai):
        # Arrange
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_wallet_provider = MagicMock()
        mock_provider.return_value = mock_wallet_provider
        
        mock_kit = MagicMock()
        mock_agentkit.return_value = mock_kit
        
        mock_tools = ["tool1", "tool2"]
        mock_get_tools.return_value = mock_tools
        
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        # Act
        with patch('json.load') as mock_json_load:
            mock_json_load.return_value = self.wallet_data
            agent_executor, agent_config = chatbot.setup()
        
        # Assert
        self.assertIsNotNone(agent_executor)
        self.assertIsNotNone(agent_config)
        mock_openai.assert_called_once()
        mock_provider.assert_called_once()
        mock_agentkit.assert_called_once()
        mock_get_tools.assert_called_once()
        mock_create_agent.assert_called_once()
    
    @patch('supereth_tools.crosschain_mint')
    @patch('supereth_tools.Account.from_key')
    def test_mint_tool_integration(self, mock_from_key, mock_crosschain_mint):
        # Arrange
        mock_account = MagicMock()
        mock_from_key.return_value = mock_account
        
        mock_result = {
            'tx_hash': '0xabc123',
            'status': 'success',
            'block_number': 123
        }
        mock_crosschain_mint.return_value = mock_result
        
        recipient = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        amount = "1000000000000000000"  # 1 ETH in wei
        
        # Act
        result = mint_supereth_crosschain(recipient, amount)
        
        # Assert
        mock_from_key.assert_called_once()
        mock_crosschain_mint.assert_called_once_with(mock_account, recipient, 1000000000000000000)
        self.assertIn("Successfully minted", result)
        self.assertIn("0xabc123", result)
    
    @patch('supereth_tools.crosschain_burn')
    @patch('supereth_tools.Account.from_key')
    def test_burn_tool_integration(self, mock_from_key, mock_crosschain_burn):
        # Arrange
        mock_account = MagicMock()
        mock_from_key.return_value = mock_account
        
        mock_result = {
            'tx_hash': '0xdef456',
            'status': 'success',
            'block_number': 456
        }
        mock_crosschain_burn.return_value = mock_result
        
        from_addr = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        amount = "500000000000000000"  # 0.5 ETH in wei
        
        # Act
        result = burn_supereth_crosschain(from_addr, amount)
        
        # Assert
        mock_from_key.assert_called_once()
        mock_crosschain_burn.assert_called_once_with(mock_account, from_addr, 500000000000000000)
        self.assertIn("Successfully burned", result)
        self.assertIn("0xdef456", result)
    
    @patch('builtins.input')
    def test_choose_mode_chat(self, mock_input):
        # Arrange
        mock_input.return_value = "chat"
        
        # Act
        mode = chatbot.choose_mode()
        
        # Assert
        self.assertEqual(mode, "chat")
        mock_input.assert_called_once()
    
    @patch('builtins.input')
    def test_choose_mode_auto(self, mock_input):
        # Arrange
        mock_input.return_value = "auto"
        
        # Act
        mode = chatbot.choose_mode()
        
        # Assert
        self.assertEqual(mode, "auto")
        mock_input.assert_called_once()
    
    @patch('builtins.input')
    def test_choose_mode_number(self, mock_input):
        # Arrange
        mock_input.return_value = "1"  # chat
        
        # Act
        mode = chatbot.choose_mode()
        
        # Assert
        self.assertEqual(mode, "chat")
        mock_input.assert_called_once()
    
    @patch('chatbot.initialize_agent')
    @patch('chatbot.os.path.exists')
    @patch('json.load')
    @patch('json.dump')
    @patch('builtins.open')
    def test_setup_existing_wallet(self, mock_open, mock_json_dump, mock_json_load, mock_exists, mock_init):
        # Arrange
        mock_exists.return_value = True
        mock_json_load.return_value = self.wallet_data
        
        mock_agent = MagicMock()
        mock_config = {"test": "config"}
        mock_init.return_value = (mock_agent, mock_config)
        
        # Act
        agent, config = chatbot.setup()
        
        # Assert
        self.assertEqual(agent, mock_agent)
        self.assertEqual(config, mock_config)
        mock_json_load.assert_called_once()
        mock_init.assert_called_once()
    
    @patch('agent2.initialize_agent')
    @patch('agent2.os.path.exists')
    @patch('json.load')
    @patch('json.dump')
    @patch('builtins.open')
    def test_agent2_setup_existing_wallet(self, mock_open, mock_json_dump, mock_json_load, mock_exists, mock_init):
        # Arrange
        mock_exists.return_value = True
        mock_json_load.return_value = self.wallet_data
        
        mock_agent = MagicMock()
        mock_config = {"test": "config"}
        mock_init.return_value = (mock_agent, mock_config)
        
        # Act
        agent, config = agent2.setup()
        
        # Assert
        self.assertEqual(agent, mock_agent)
        self.assertEqual(config, mock_config)
        mock_json_load.assert_called_once()
        mock_init.assert_called_once()
    
    @patch('agent3.initialize_agent')
    @patch('agent3.os.path.exists')
    @patch('json.load')
    @patch('json.dump')
    @patch('builtins.open')
    def test_agent3_setup_existing_wallet(self, mock_open, mock_json_dump, mock_json_load, mock_exists, mock_init):
        # Arrange
        mock_exists.return_value = True
        mock_json_load.return_value = {
            "private_key": "1" * 64,
            "chain_id": "11155111",  # Ethereum Sepolia
            "created_at": "2023-01-01 00:00:00"
        }
        
        mock_agent = MagicMock()
        mock_config = {"test": "config"}
        mock_init.return_value = (mock_agent, mock_config)
        
        # Act
        agent, config = agent3.setup()
        
        # Assert
        self.assertEqual(agent, mock_agent)
        self.assertEqual(config, mock_config)
        mock_json_load.assert_called_once()
        mock_init.assert_called_once()

if __name__ == '__main__':
    unittest.main()
