// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../lib/forge-std/src/Test.sol";
import "../src/InterOp.sol";

contract SuperETHTest is Test {
    SuperETH public superETH;
    address public aiAgent;
    address public owner;
    address public user1;
    address public user2;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event CrosschainMinted(address indexed receiver, uint256 amount);
    event CrosschainBurned(address indexed from, uint256 amount);

    function setUp() public {
        aiAgent = makeAddr("aiAgent");
        owner = makeAddr("owner");
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");

        vm.deal(user1, 10 ether);
        vm.deal(user2, 10 ether);

        superETH = new SuperETH(aiAgent, owner);
    }

    function test_Deployment() public {
        assertEq(superETH.name(), "SuperETH");
        assertEq(superETH.symbol(), "sETH");
        assertEq(superETH.aiAgent(), aiAgent);
        assertEq(superETH.owner(), owner);
        assertEq(superETH.totalSupply(), 0);
    }

    function test_Deposit() public {
        uint256 depositAmount = 1 ether;

        vm.startPrank(user1);
        vm.expectEmit(true, true, true, true);
        emit Deposited(user1, depositAmount);

        superETH.deposit{value: depositAmount}();

        assertEq(superETH.balanceOf(user1), depositAmount);
        assertEq(address(superETH).balance, depositAmount);
        vm.stopPrank();
    }

    function test_DepositZeroAmount() public {
        vm.startPrank(user1);
        vm.expectRevert("Amount must be greater than zero");
        superETH.deposit{value: 0}();
        vm.stopPrank();
    }

    function test_Withdraw() public {
        uint256 depositAmount = 1 ether;

        // First deposit
        vm.startPrank(user1);
        superETH.deposit{value: depositAmount}();

        // Then withdraw
        vm.expectEmit(true, true, true, true);
        emit Withdrawn(user1, depositAmount);

        superETH.withdraw(depositAmount);

        assertEq(superETH.balanceOf(user1), 0);
        assertEq(address(superETH).balance, 0);
        vm.stopPrank();
    }

    function test_WithdrawInsufficientBalance() public {
        vm.startPrank(user1);
        vm.expectRevert("Insufficient sETH balance");
        superETH.withdraw(1 ether);
        vm.stopPrank();
    }

    function test_WithdrawInsufficientReserves() public {
        uint256 depositAmount = 1 ether;

        // First deposit
        vm.startPrank(user1);
        superETH.deposit{value: depositAmount}();
        vm.stopPrank();

        // Simulate the contract losing all its ETH
        vm.deal(address(superETH), 0);

        // Now try to withdraw - should fail due to insufficient reserves
        vm.startPrank(user1);
        vm.expectRevert("Insufficient reserves");
        superETH.withdraw(depositAmount);
        vm.stopPrank();
    }

    function test_CrosschainMint() public {
        uint256 mintAmount = 1 ether;

        vm.startPrank(aiAgent);
        vm.expectEmit(true, true, true, true);
        emit CrosschainMinted(user1, mintAmount);

        superETH.crosschainMint(user1, mintAmount);

        assertEq(superETH.balanceOf(user1), mintAmount);
        vm.stopPrank();
    }

    function test_CrosschainMintUnauthorized() public {
        vm.startPrank(user1);
        vm.expectRevert("Unauthorized: Only AI agent can mint");
        superETH.crosschainMint(user2, 1 ether);
        vm.stopPrank();
    }

    function test_CrosschainBurn() public {
        uint256 amount = 1 ether;

        // First mint some tokens
        vm.startPrank(aiAgent);
        superETH.crosschainMint(user1, amount);

        // Then burn them
        vm.expectEmit(true, true, true, true);
        emit CrosschainBurned(user1, amount);

        superETH.crosschainBurn(user1, amount);

        assertEq(superETH.balanceOf(user1), 0);
        vm.stopPrank();
    }

    function test_CrosschainBurnUnauthorized() public {
        vm.startPrank(user1);
        vm.expectRevert("Unauthorized: Only AI agent can burn");
        superETH.crosschainBurn(user2, 1 ether);
        vm.stopPrank();
    }

    function test_CrosschainBurnInsufficientBalance() public {
        vm.startPrank(aiAgent);
        vm.expectRevert("Insufficient balance");
        superETH.crosschainBurn(user1, 1 ether);
        vm.stopPrank();
    }
}

// Helper contract to receive ETH
contract MaliciousContract {
    receive() external payable {}
}
