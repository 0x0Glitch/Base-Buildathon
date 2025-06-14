import os
import unittest
from unittest.mock import patch, MagicMock, call
import sys
from io import StringIO
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_core.messages import HumanMessage

# Import the agents to test
import chatbot
import agent2
import agent3

class TestAgentInteraction(unittest.TestCase):
    
    def setUp(self):
        # Set up environment variables for testing
        self.env_patcher = patch.dict(os.environ, {
            "CDP_API_KEY_ID": "test_key_id",
            "CDP_API_KEY_SECRET": "test_key_secret",
            "OPENAI_API_KEY": "test_openai_key",
            "OPTIMISM_CONTRACT_ADDRESS": "0x0fba25D5e71Aa1ed0aD8384f693872AbeC79e9B2",
            "CHAIN_ID": "84532",
            "PRIVATE_KEY": "1" * 64
        })
        self.env_patcher.start()
        
        # Create mock agent components
        self.mock_agent_executor = MagicMock()
        self.mock_agent_config = {"configurable": {"thread_id": "Test Thread"}}
    
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input')
    def test_run_chat_mode_exit(self, mock_input, mock_stdout):
        # Arrange
        mock_input.return_value = "exit"
        
        # Act
        chatbot.run_chat_mode(self.mock_agent_executor, self.mock_agent_config)
        
        # Assert
        mock_input.assert_called_once()
        # The function should exit without calling stream
        self.mock_agent_executor.stream.assert_not_called()
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input')
    def test_run_chat_mode_interaction(self, mock_input, mock_stdout):
        # Arrange
        mock_input.return_value = "Tell me about Ethereum"
        
        # Setup the stream mock to yield responses
        agent_response = {"agent": {"messages": [MagicMock(content="Ethereum is a blockchain platform")]}}
        tool_response = {"tools": {"messages": [MagicMock(content="Tool execution complete")]}}
        self.mock_agent_executor.stream.return_value = [agent_response, tool_response]
        
        # Act
        try:
            # Use try-except since we need to manually break out of the infinite loop
            chatbot.run_chat_mode(self.mock_agent_executor, self.mock_agent_config)
        except StopIteration:
            pass  # End the test when stream runs out
        
        # Assert
        mock_input.assert_called_once()
        self.mock_agent_executor.stream.assert_called_once_with(
            {"messages": [HumanMessage(content="Tell me about Ethereum")]}, 
            self.mock_agent_config
        )
        self.assertIn("Ethereum is a blockchain platform", mock_stdout.getvalue())
        self.assertIn("Tool execution complete", mock_stdout.getvalue())
    
    @patch('time.sleep', return_value=None)  # Mock sleep to speed up tests
    def test_run_autonomous_mode(self, mock_sleep):
        # Arrange
        # Setup the stream mock to yield responses, then raise StopIteration to break the loop
        agent_response = {"agent": {"messages": [MagicMock(content="I'll check Ethereum price")]}}
        tool_response = {"tools": {"messages": [MagicMock(content="Current price is $X")]}}
        self.mock_agent_executor.stream.return_value = [agent_response, tool_response]
        self.mock_agent_executor.stream.side_effect = [
            [agent_response, tool_response],  # First call returns these values
            StopIteration  # Second call breaks the loop
        ]
        
        # Act
        try:
            chatbot.run_autonomous_mode(self.mock_agent_executor, self.mock_agent_config)
        except StopIteration:
            pass  # End the test when StopIteration is raised
        
        # Assert
        expected_thought = (
            "Be creative and do something interesting on the blockchain. "
            "Choose an action or set of actions and execute it that highlights your abilities."
        )
        self.mock_agent_executor.stream.assert_called_with(
            {"messages": [HumanMessage(content=expected_thought)]}, 
            self.mock_agent_config
        )
    
    @patch('builtins.input')
    def test_choose_mode_multiple_attempts(self, mock_input):
        # Arrange - First input invalid, second is valid
        mock_input.side_effect = ["invalid", "chat"]
        
        # Act
        mode = chatbot.choose_mode()
        
        # Assert
        self.assertEqual(mode, "chat")
        self.assertEqual(mock_input.call_count, 2)
    
    @patch('sys.stdout', new_callable=StringIO)
    @patch('chatbot.ChatOpenAI')
    @patch('chatbot.AgentKit')
    @patch('chatbot.get_langchain_tools')
    @patch('chatbot.create_react_agent')
    def test_initialization_with_tool_inclusion(self, mock_create_agent, mock_get_tools, 
                                             mock_agentkit, mock_openai, mock_stdout):
        # Arrange
        from coinbase_agentkit import EthAccountWalletProviderConfig
        from eth_account import Account
        
        # Create test account
        private_key = "0x" + "0" * 64
        account = Account.from_key(private_key)
        
        # Create test config
        config = EthAccountWalletProviderConfig(
            account=account,
            chain_id="84532"  # Base Sepolia
        )
        
        # Set up mocks
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_kit = MagicMock()
        mock_agentkit.return_value = mock_kit
        
        agentkit_tools = ["wallet_tool", "erc20_tool"]
        mock_get_tools.return_value = agentkit_tools
        
        # Act
        chatbot.initialize_agent(config)
        
        # Assert
        # Verify that both AgentKit tools and SuperETH tools are included
        combined_tools = agentkit_tools + [chatbot.mint_supereth_crosschain, chatbot.burn_supereth_crosschain]
        mock_create_agent.assert_called_once()
        # Extract the tools argument from the call
        _, kwargs = mock_create_agent.call_args
        tools_arg = kwargs.get('tools', [])
        
        # Ensure all expected tools are in the tools argument
        self.assertEqual(len(tools_arg), len(combined_tools))

if __name__ == '__main__':
    unittest.main()
