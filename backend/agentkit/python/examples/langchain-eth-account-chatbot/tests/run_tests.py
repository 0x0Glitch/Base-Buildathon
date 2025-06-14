#!/usr/bin/env python
import unittest
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from tests.test_supereth_helper import TestSuperEthHelper
from tests.test_supereth_tools import TestSuperEthTools
from tests.test_agent_initialization import TestAgentInitialization
from tests.test_integration import TestIntegration
from tests.test_agent_interaction import TestAgentInteraction
from tests.test_multi_chain import TestMultiChainCompatibility

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add tests to the suite
    test_suite.addTest(unittest.makeSuite(TestSuperEthHelper))
    test_suite.addTest(unittest.makeSuite(TestSuperEthTools))
    test_suite.addTest(unittest.makeSuite(TestAgentInitialization))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    test_suite.addTest(unittest.makeSuite(TestAgentInteraction))
    test_suite.addTest(unittest.makeSuite(TestMultiChainCompatibility))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
