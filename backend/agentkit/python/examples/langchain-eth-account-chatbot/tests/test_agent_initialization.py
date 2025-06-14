import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eth_account import Account
from coinbase_agentkit import EthAccountWalletProviderConfig

# Import the agents to test
import chatbot
import agent2
import agent3
import agent4

class TestAgentInitialization(unittest.TestCase):
    
    def setUp(self):
        # Create a test account
        self.private_key = "0x" + "0" * 64
        self.account = Account.from_key(self.private_key)
        
        # Create test config
        self.config = EthAccountWalletProviderConfig(
            account=self.account,
            chain_id="84532"  # Base Sepolia
        )
        
        # Set up environment variables
        self.env_patcher = patch.dict(os.environ, {
            "CDP_API_KEY_ID": "test_key_id",
            "CDP_API_KEY_SECRET": "test_key_secret",
            "OPENAI_API_KEY": "test_openai_key",
            "OPTIMISM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "ETHEREUM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "BASE_SEPOLIA_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2"
        })
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('chatbot.ChatOpenAI')
    @patch('chatbot.EthAccountWalletProvider')
    @patch('chatbot.AgentKit')
    @patch('chatbot.get_langchain_tools')
    @patch('chatbot.create_react_agent')
    @patch('chatbot.MemorySaver')
    def test_chatbot_initialize_agent(self, mock_memory, mock_create_agent, 
                                    mock_get_tools, mock_agentkit, mock_provider, mock_openai):
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
        agent, config = chatbot.initialize_agent(self.config)
        
        # Assert
        self.assertEqual(agent, mock_agent)
        self.assertTrue("configurable" in config)
        self.assertEqual(config["configurable"]["thread_id"], "Ethereum Account Chatbot")
        mock_get_tools.assert_called_once_with(mock_kit)
        mock_create_agent.assert_called_once()
    
    @patch('agent2.ChatOpenAI')
    @patch('agent2.EthAccountWalletProvider')
    @patch('agent2.AgentKit')
    @patch('agent2.get_langchain_tools')
    @patch('agent2.create_react_agent')
    @patch('agent2.MemorySaver')
    def test_agent2_initialize_agent(self, mock_memory, mock_create_agent, 
                                   mock_get_tools, mock_agentkit, mock_provider, mock_openai):
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
        agent, config = agent2.initialize_agent(self.config)
        
        # Assert
        self.assertEqual(agent, mock_agent)
        self.assertTrue("configurable" in config)
        self.assertEqual(config["configurable"]["thread_id"], "Ethereum Account Chatbot")
        mock_get_tools.assert_called_once_with(mock_kit)
        mock_create_agent.assert_called_once()
    
    @patch('agent3.ChatOpenAI')
    @patch('agent3.EthAccountWalletProvider')
    @patch('agent3.AgentKit')
    @patch('agent3.get_langchain_tools')
    @patch('agent3.create_react_agent')
    @patch('agent3.MemorySaver')
    def test_agent3_initialize_agent(self, mock_memory, mock_create_agent, 
                                   mock_get_tools, mock_agentkit, mock_provider, mock_openai):
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
        agent, config = agent3.initialize_agent(self.config)
        
        # Assert
        self.assertEqual(agent, mock_agent)
        self.assertTrue("configurable" in config)
        self.assertEqual(config["configurable"]["thread_id"], "Ethereum Account Chatbot")
        mock_get_tools.assert_called_once_with(mock_kit)
        mock_create_agent.assert_called_once()
    
    @patch('chatbot.os.path.exists')
    @patch('chatbot.open')
    @patch('chatbot.initialize_agent')
    @patch('chatbot.Account.create')
    def test_chatbot_setup_new_wallet(self, mock_create, mock_init, mock_open, mock_exists):
        # Arrange
        mock_exists.return_value = False  # Wallet file doesn't exist
        
        mock_account = MagicMock(address="0xTestAddress")
        mock_account.key = b'test_key'
        mock_create.return_value = (mock_account, "new_private_key")
        
        mock_agent = MagicMock()
        mock_config = {"test": "config"}
        mock_init.return_value = (mock_agent, mock_config)
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Act
        with patch('json.dump') as mock_json_dump:
            agent, config = chatbot.setup()
        
        # Assert
        mock_create.assert_called_once()
        mock_init.assert_called_once()
        self.assertEqual(agent, mock_agent)
        self.assertEqual(config, mock_config)
        mock_json_dump.assert_called()
    
    @patch('chatbot.run_chat_mode')
    @patch('chatbot.run_autonomous_mode')
    @patch('chatbot.setup')
    @patch('chatbot.choose_mode')
    @patch('chatbot.load_dotenv')
    def test_chatbot_main_chat_mode(self, mock_dotenv, mock_choose, mock_setup, mock_auto, mock_chat):
        # Arrange
        mock_choose.return_value = "chat"
        mock_agent = MagicMock()
        mock_config = {"test": "config"}
        mock_setup.return_value = (mock_agent, mock_config)
        
        # Act
        chatbot.main()
        
        # Assert
        mock_dotenv.assert_called_once()
        mock_setup.assert_called_once()
        mock_choose.assert_called_once()
        mock_chat.assert_called_once_with(agent_executor=mock_agent, config=mock_config)
        mock_auto.assert_not_called()
    
    @patch('chatbot.run_chat_mode')
    @patch('chatbot.run_autonomous_mode')
    @patch('chatbot.setup')
    @patch('chatbot.choose_mode')
    @patch('chatbot.load_dotenv')
    def test_chatbot_main_auto_mode(self, mock_dotenv, mock_choose, mock_setup, mock_auto, mock_chat):
        # Arrange
        mock_choose.return_value = "auto"
        mock_agent = MagicMock()
        mock_config = {"test": "config"}
        mock_setup.return_value = (mock_agent, mock_config)
        
        # Act
        chatbot.main()
        
        # Assert
        mock_dotenv.assert_called_once()
        mock_setup.assert_called_once()
        mock_choose.assert_called_once()
        mock_auto.assert_called_once_with(agent_executor=mock_agent, config=mock_config)
        mock_chat.assert_not_called()

if __name__ == '__main__':
    unittest.main()
